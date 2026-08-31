# Provenance

Every file under `data/` outside `data/raw/` is generated. Nothing is hand-edited,
and nothing is recoded, rescaled, imputed or renamed. The only operation applied
to the source data is a row filter — keep the respondents whose country variable
identifies Tunisia — plus a rewrite of the same values into four file formats.

## Chain of custody

| Step | What happens |
|---|---|
| 1 | The publisher's release is placed in `data/raw/`, which is tracked, so the input is in the repository beside the output. Two files exceed GitHub's 100 MB limit and are fetched by `scripts/fetch_raw.py` against a recorded checksum instead (see `data/raw/README.md`). |
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

## Questionnaires

`docs/questionnaires/` holds the published English instrument for each wave, and
`catalog/sources.json` records the source URL per wave. They are the publisher's
own documents, downloaded from arabbarometer.org.

They are documentation, but they are also an input: `scripts/build_crosswalk.py`
parses them for question text where a release carries no variable labels, which is
the whole of Wave IV, and for the wording behind a label that only names its topic,
which is the whole of Wave V. Anything the crosswalk sourced that way is marked in
its `text_from_questionnaire` column, and a sub-item that inherited its parent
question's wording is marked `questionnaire (stem …)`.

The parse is validated against the releases that do carry wording as labels —
85–97% agreement per wave, recorded in `catalog/crosswalk-report.json` — rather
than taken on trust. Waves IV and V are reported unvalidated with a reason instead
of a rate: Wave IV has no labels, and Wave V's are a controlled vocabulary in
capitals that names each question without restating it, so comparing them with the
wording would score the labelling style rather than the parse.

## Two releases do not say what they seem to

**Afrobarometer Round 9 is distributed as the English release and labels its
variables in French** — `Raison d'un entretien infructueux Ménage1` where the other
rounds say `Reason for Unsuccessful Call Household 1`. 277 of its 386 labels are
French. Nothing is changed in the data; `catalog/sources.json` records
`"release_label_language": "French"` for that survey, and the crosswalk marks the
269 entries that take their text from it `release label (French)` rather than
letting French wording pass as English.

**Afrobarometer numbers variables differently from its own questionnaire.** In Round
10 the variable `Q6` carries the label `Q5b.`, `Q52C` carries `Q53c.`, and 18 more
diverge. That is why no Afrobarometer questionnaire is parsed for question text: a
number-to-variable mapping would be wrong for those twenty.

## Wave VI is three surveys

Arab Barometer fielded Wave VI as three telephone rounds during the pandemic, each
with its own sample and questionnaire, so the archive carries three surveys rather
than one: `wave-06-part-1`, `-2` and `-3`, fielded July 2020, October 2020 and
March 2021.

They are not a panel. Their `ID` values overlap — 223 to 339 shared values between
any two rounds — but on those shared IDs sex agrees 51–57% of the time and age 1–3%,
which is what coincidence looks like rather than a link. The IDs are per-release
sequence numbers. Do not join the rounds on them.

## Fieldwork dates

Waves III, VI and VII record an interview date per respondent, as does Wave VIII,
so the Tunisia fieldwork window for those is read out of the data. Waves II, IV and
V carry no date variable; for those the catalog leaves `fieldwork_tunisia` empty
and reports only the fieldwork years the publisher gives for the wave as a whole. Rather than assert a window from memory, no
Tunisia-specific dates are given for them; the country report on the Arab Barometer
site has them.

## Country identification

Each series identifies Tunisia its own way, and `catalog/sources.json` records
which for every survey:

| Series | How |
|---|---|
| Arab Barometer | country code **21**, in a variable spelled `country` in the early waves and `COUNTRY` from Wave VI on |
| World Values Survey | ISO code **788**, in `B_COUNTRY` in Wave 7 and `V2` in Wave 6 |
| Afrobarometer | no country column at all — the country files carry respondent numbers prefixed `TUN`, so the filter matches on the prefix of `RESPNO` |
| Arab Opinion Index | country code **2**, in `Q1`, in every round from 2011 to 2024/2025 |

The filter runs even on a country file that holds nothing else, so a file is
always checked to contain what its name claims rather than trusted.

## Known departures from the source

| Output | Departure |
|---|---|
| `.dta` | Stata caps a variable label at 80 characters. Longer labels are truncated with a trailing `...`. Wave II has 364 such labels and Wave VIII has 114; Wave V has none. The untruncated label is in `codebook.csv` and in the `.sav`. |
| `.sav`, `.dta` | Numeric columns are written as doubles rather than the narrower storage types some source files use. Values are unchanged; the files are larger than they strictly need to be. |
| `-labels.csv` | Where a variable has value labels, the label text replaces the code. Where it has none, the code is written through unchanged. A label can be attached to more than one code — Wave V's party variables label both `0` and `150000` "no party" — so this file is not always reversible. Use `-codes.csv` when you need the code. |
| `-codes.csv`, `-labels.csv` | CSV cannot distinguish an empty string from a missing value. One variable is affected: Wave V's `E2001B`, a string variable that is empty for every Tunisian respondent. The `.sav` and `.dta` preserve the distinction. |
| `-codes.csv`, `-labels.csv` | An answer spelled the way CSV readers spell a missing value is read as missing by default. One is affected: Wave IV's `q1019b` answers "None" to a second-language question. Read with `keep_default_na=False`, or use the `.sav` or `.dta`. Every wave is scanned for this and hits are recorded in `catalog/catalog.json` under `csv_answers_read_as_missing`. |
| `.sav`, `.dta` | Both formats embed a creation timestamp, so re-running the extractor produces byte-different files with identical content. The recorded SHA-256 identifies the committed file; it is not a reproducible-build guarantee. `scripts/verify.py` compares values, not bytes. |
| `.dta` | Stata stores a time of day as a float and rounds it. Five of Afrobarometer Round 7's interview start times come back a microsecond off, and a few in Rounds 9 and 10. `scripts/verify.py` compares date and time columns to the millisecond for that reason. |
| all | A variable name SPSS and Stata will not accept is rewritten, and the change recorded in `renamed_variables` in the catalog and in the survey's README. Afrobarometer Round 10's `LOCATION.LEVEL.1` becomes `LOCATION_LEVEL_1`, and 196 variables in the Arab Opinion Index 2019/2020 round lose a dot the same way. |
| all | Value labels on a date or time column are dropped, since neither format will attach them. Three Afrobarometer rounds have one, marking a sentinel on the interview start and end times that the reader has already parsed as a time of day. |
| all | Column order and column names are otherwise exactly those of the release. |

None of these lose information that the format in question could have carried, and
`scripts/verify.py` checks every cell of every output against the source.

## Terms of use

The survey data is the property of the programme that collected it. Arab Barometer
makes its data freely available for research but asks users to register and to
cite the source; it is redistributed here in subset form for research use. Anyone
using these files should cite Arab Barometer and the specific wave, not this
repository, as the source of the data. See <https://www.arabbarometer.org>.
