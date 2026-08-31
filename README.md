# SurveysTN

Public-opinion survey data covering Tunisia — Arab Barometer, the World Values
Survey and Afrobarometer so far — reorganised so that each survey is one self-describing folder: the
respondents, in every common format, with a codebook and a provenance record. Most
are extracted from the pooled multi-country releases the programmes publish; where
a programme ships a Tunisia country file, that is used as it stands.

The point is that the pooled releases are awkward to work with if Tunisia is your
case. They are large, they mix twelve or more countries, they carry hundreds of
columns that were never asked in Tunisia, and their formats disagree with each
other from one wave to the next. What is here is the same data, filtered and made
consistent, with nothing recoded.

## What's in it

| Survey | Respondents | Variables | Fieldwork | Folder |
|---|---:|---:|---|---|
| Arab Barometer Wave II | 1,196 | 468 (303 with data) | 2010–2011 | [`data/arab-barometer/wave-02`](data/arab-barometer/wave-02) |
| Arab Barometer Wave III | 1,199 | 296 (247 with data) | Feb–Mar 2013 | [`data/arab-barometer/wave-03`](data/arab-barometer/wave-03) |
| Arab Barometer Wave IV | 1,200 | 290 (248 with data) | 2016–2017 | [`data/arab-barometer/wave-04`](data/arab-barometer/wave-04) |
| Arab Barometer Wave V | 2,400 | 359 (281 with data) | 2018–2019 | [`data/arab-barometer/wave-05`](data/arab-barometer/wave-05) |
| Arab Barometer Wave VI Part 1 | 1,005 | 98 (75 with data) | Jul 2020 | [`data/arab-barometer/wave-06-part-1`](data/arab-barometer/wave-06-part-1) |
| Arab Barometer Wave VI Part 2 | 1,002 | 82 (78 with data) | Oct 2020 | [`data/arab-barometer/wave-06-part-2`](data/arab-barometer/wave-06-part-2) |
| Arab Barometer Wave VI Part 3 | 1,200 | 105 (98 with data) | Mar 2021 | [`data/arab-barometer/wave-06-part-3`](data/arab-barometer/wave-06-part-3) |
| Arab Barometer Wave VII | 2,400 | 453 (373 with data) | Oct–Nov 2021 | [`data/arab-barometer/wave-07`](data/arab-barometer/wave-07) |
| Arab Barometer Wave VIII | 2,406 | 690 (466 with data) | Sep–Nov 2023 | [`data/arab-barometer/wave-08`](data/arab-barometer/wave-08) |
| World Values Survey Wave 6 | 1,205 | 370 | Nov–Dec 2013 | [`data/world-values-survey/wave-06`](data/world-values-survey/wave-06) |
| World Values Survey Wave 7 | 1,208 | 397 | Apr–May 2019 | [`data/world-values-survey/wave-07`](data/world-values-survey/wave-07) |
| Afrobarometer Round 6 | 1,200 | 334 | Apr–May 2015 | [`data/afrobarometer/round-06`](data/afrobarometer/round-06) |
| Afrobarometer Round 7 | 1,199 | 339 | Mar–May 2018 | [`data/afrobarometer/round-07`](data/afrobarometer/round-07) |
| Afrobarometer Round 8 | 1,200 | 377 | Feb–Mar 2020 | [`data/afrobarometer/round-08`](data/afrobarometer/round-08) |
| Afrobarometer Round 9 | 1,200 | 388 (380 with data) | Feb–Mar 2022 | [`data/afrobarometer/round-09`](data/afrobarometer/round-09) |
| Afrobarometer Round 10 | 1,200 | 372 (363 with data) | Feb–Mar 2024 | [`data/afrobarometer/round-10`](data/afrobarometer/round-10) |

22,420 Tunisian respondents across sixteen surveys in three series, plus one derived file:
[`wave-06-merged`](data/arab-barometer/wave-06-merged) stacks the three Wave VI
rounds into 3,207 rows with a `PART` column. `catalog/catalog.csv` and
`catalog/catalog.json` carry the same table in machine-readable form, with
per-file checksums.

[`wave-06-merged`](data/arab-barometer/wave-06-merged) is the one derived file in
the archive — the three Wave VI rounds stacked, for when you want them pooled. It
is built and checked by script, and its README says what stacking cost. Wave VI is
otherwise carried as three surveys rather than one. Arab Barometer fielded it as
three telephone rounds during the pandemic, months apart, each with its own sample
and its own questionnaire. They are not a panel: the ID numbers overlap between
rounds, but on the overlapping IDs sex agrees at chance and age almost never, so
the numbers are per-release sequence numbers and must not be used to link
respondents.

Wave IV is the one partial entry: Arab Barometer distributes it as a CSV of label
text with no SPSS release, so it has no numeric codes and no question text. It is
laid out like the rest, and
[its README](data/arab-barometer/wave-04/README.md) says what is missing and how
supplying the SPSS release would fill it in.

## Each survey folder

```
data/arab-barometer/wave-08/
├── README.md                              provenance and file listing
├── arab-barometer-w08-tunisia.sav         SPSS, full variable and value labels
├── arab-barometer-w08-tunisia.dta         Stata 14
├── arab-barometer-w08-tunisia-codes.csv   numeric codes (absent for Wave IV)
├── arab-barometer-w08-tunisia-labels.csv  value labels as text
├── codebook.csv                           one row per variable
└── codebook.json
```

The data files hold identical values. Start with
[`docs/using-the-data.md`](docs/using-the-data.md) — in particular the five things
worth checking before you analyse anything, which include a weighting variable
Wave II does not have and don't-know codes that are not declared missing.

## Repository layout

| Path | |
|---|---|
| `data/<series>/<wave>/` | one folder per survey — the extracts |
| `data/<series>/wave-06-merged/` | derived: the three Wave VI rounds stacked |
| `data/raw/` | the publishers' releases, tracked, so the archive can be rebuilt from a clone |
| `catalog/` | `catalog.json` / `catalog.csv`, generated; `sources.json`, hand-maintained |
| `docs/` | how to use the data, provenance, the cross-wave crosswalk, missing-value codes |
| `docs/questionnaires/` | the published questionnaire for every wave, as PDF |
| `scripts/` | extraction, verification, doc generation |

## Regenerating

Everything outside `catalog/sources.json` and the top-level docs is generated, and
the releases it is generated from are in `data/raw/` (see
[`data/raw/README.md`](data/raw/README.md)), so a clone can rebuild the whole
archive and check it:

```bash
pip install -r scripts/requirements.txt
python3 scripts/extract_tunisia.py        # extracts + codebooks + catalog
python3 scripts/build_crosswalk.py        # docs/crosswalk.csv, docs/crosswalk.md
python3 scripts/build_wave06_merge.py     # data/arab-barometer/wave-06-merged
python3 scripts/build_missing_codes.py    # docs/missing-value-codes.md
python3 scripts/verify.py                 # cell-by-cell check against the releases
```

`python3 scripts/verify.py --offline` is the quicker check, comparing the committed
files against the checksums and counts in `catalog/catalog.json` without re-reading
the releases.

## Matching the waves to each other

[`docs/crosswalk.md`](docs/crosswalk.md) and the full
[`docs/crosswalk.csv`](docs/crosswalk.csv) line the waves up: one row per variable,
the name it takes in each wave, the question each wave asked, and whether the
wording held. 3,591 variables, 3,528 of them with question text; within Arab Barometer, 13 are
present in all nine of its surveys, and within Afrobarometer 61 in all five.

Where a programme renumbers its variables, matching on name finds nothing —
the World Values Survey asks as `V9` in Wave 6 what it asks as `Q6` in Wave 7.
[`docs/crosswalk-suggested.csv`](docs/crosswalk-suggested.csv) pairs those up by
question text instead: 595 pairs, offered only where the wordings are all but
identical, unambiguous, and agreed on any numbers they contain. They are
suggestions to confirm, not findings.

Variables are matched **within a series and never across one** — `Q1` is the
governorate in Arab Barometer and "Important in life: Family" in the World Values
Survey, and a shared name between series means nothing.

The question text comes from the release's own variable labels where it has them,
and otherwise from the survey's questionnaire in
[`docs/questionnaires/`](docs/questionnaires), parsed by question number. That is
the only source for Wave IV, and it also repairs labels that are truncated in the
release — Arab Barometer's own Wave VIII label for `Q101` ends "the current
economic situation in?". The parse is checked against release labels rather than trusted, and agrees on
85–97% of comparable variables in the seven waves where the check is meaningful.
It is not meaningful everywhere: Wave IV carries no labels at all, and Wave V
labels every variable from a controlled vocabulary in capitals —
`ELECTORAL PARTICIPATION: VISITED RALLY DURING PARLIAMENTARY ELECTION` for a
question reading "did you attend a campaign meeting or rally?". Those two say the
same thing and share almost no characters, so both waves are reported unvalidated
with the reason, rather than given a number that would measure labelling style.

Matching on name alone would mislead: 97 variables share a name across waves but
not a wording. Check `text_varies_across_waves` before pooling anything.

## Adding a survey

Append an entry to `catalog/sources.json` giving the release's file stem, its
country variable and the code Tunisia takes in it, then re-run the scripts. See
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Provenance and terms

Only a row filter is applied — keep the Tunisian respondents — plus a rewrite into
the formats above. Nothing is recoded, rescaled, imputed or renamed. Every generated
file's SHA-256 is recorded in `catalog/catalog.json`, and `scripts/verify.py`
re-derives each subset from its source and compares it cell by cell.
[`docs/provenance.md`](docs/provenance.md) has the details, including the two
places where a file format forced a departure from the source.

The data belongs to the programme that collected it. Arab Barometer makes its data
freely available for research and asks users to register and cite the source; it
is redistributed here in subset form for research use. **Cite Arab Barometer and
the specific wave, not this repository, as the source of the data.**
See <https://www.arabbarometer.org>.
