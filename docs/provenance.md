# Provenance

Every file under `data/` outside `data/raw/` is generated. Nothing is hand-edited,
and nothing is recoded, rescaled, imputed or renamed. The only operation applied
to the source data is a row filter — keep the respondents whose country variable
identifies Tunisia — plus a rewrite of the same values into four file formats.

## Chain of custody

| Step | What happens |
|---|---|
| 1 | The publisher's pooled, multi-country release is placed in `data/raw/` (see `data/raw/README.md`). |
| 2 | `scripts/extract_tunisia.py` reads the SPSS (`.sav`) release, filters to the Tunisia country code, and writes `.sav`, `.dta`, `-codes.csv` and `-labels.csv` plus a codebook. |
| 3 | The SHA-256 of the input release and of every generated file is recorded in `catalog/catalog.json`. |
| 4 | `scripts/verify.py` re-derives the subset from the release and compares it cell by cell against what is committed. |

Where an SPSS release exists it is the input for every output, not just the `.sav`.
That is deliberate: it is the only one of the distributed formats that carries both
the variable labels and the value labels, and using a single input keeps the waves
consistent with one another. Upstream they are not — the Wave II CSV ships value
labels as text while the Wave V and Wave VIII CSVs ship numeric codes.

Wave IV is the exception. Arab Barometer distributes it as a CSV of label text with
no SPSS release, so it is read from that CSV, declared in `catalog/sources.json` as
`"source_format": "csv-labels"`. It therefore has no `-codes.csv` and no question
text, and its `.sav` and `.dta` hold strings rather than coded categoricals. Columns
that parse as numeric across the whole pooled release — `qid`, `stratum`, `psu`,
`wt` — are typed numeric; the rest stay text. That decision is made on the pooled
release rather than on the Tunisia subset, so it does not change with the country
being extracted. Dropping the SPSS release into `data/raw/` and switching
`source_format` to `sav` upgrades the wave with no other change.

## Country identification

Arab Barometer numbers Tunisia **21** in the country variable in all three waves.
The variable is spelled `country` in Waves II and V and `COUNTRY` in Wave VIII;
`catalog/sources.json` records the spelling used for each wave.

## Fieldwork dates

Wave VIII records an interview date per respondent, so the Tunisia fieldwork
window in the catalog is derived from the data itself. Waves II and V carry no
date variable. Rather than assert a window from memory, the catalog leaves
`fieldwork_tunisia` empty for those two waves and reports only the fieldwork years
the publisher gives for the wave as a whole. For the Tunisia-specific dates,
consult the country report on the Arab Barometer site.

## Known departures from the source

| Output | Departure |
|---|---|
| `.dta` | Stata caps a variable label at 80 characters. Longer labels are truncated with a trailing `...`. Wave II has 364 such labels and Wave VIII has 114; Wave V has none. The untruncated label is in `codebook.csv` and in the `.sav`. |
| `.sav`, `.dta` | Numeric columns are written as doubles rather than the narrower storage types some source files use. Values are unchanged; the files are larger than they strictly need to be. |
| `-labels.csv` | Where a variable has value labels, the label text replaces the code. Where it has none, the code is written through unchanged. A label can be attached to more than one code — Wave V's party variables label both `0` and `150000` "no party" — so this file is not always reversible. Use `-codes.csv` when you need the code. |
| `-codes.csv`, `-labels.csv` | CSV cannot distinguish an empty string from a missing value. One variable is affected: Wave V's `E2001B`, a string variable that is empty for every Tunisian respondent. The `.sav` and `.dta` preserve the distinction. |
| `-codes.csv`, `-labels.csv` | An answer spelled the way CSV readers spell a missing value is read as missing by default. One is affected: Wave IV's `q1019b` answers "None" to a second-language question. Read with `keep_default_na=False`, or use the `.sav` or `.dta`. Every wave is scanned for this and hits are recorded in `catalog/catalog.json` under `csv_answers_read_as_missing`. |
| `.sav`, `.dta` | Both formats embed a creation timestamp, so re-running the extractor produces byte-different files with identical content. The recorded SHA-256 identifies the committed file; it is not a reproducible-build guarantee. `scripts/verify.py` compares values, not bytes. |
| all | Column order and column names are exactly those of the pooled release. |

None of these lose information that the format in question could have carried, and
`scripts/verify.py` checks every cell of every output against the source.

## Terms of use

The survey data is the property of the programme that collected it. Arab Barometer
makes its data freely available for research but asks users to register and to
cite the source; it is redistributed here in subset form for research use. Anyone
using these files should cite Arab Barometer and the specific wave, not this
repository, as the source of the data. See <https://www.arabbarometer.org>.
