# SurveysTN

Public-opinion survey data covering Tunisia, extracted from the pooled
multi-country releases the survey programmes publish, and reorganised so that each
survey is one self-describing folder: the respondents, in every common format, with a
codebook and a provenance record.

The point is that the pooled releases are awkward to work with if Tunisia is your
case. They are large, they mix twelve or more countries, they carry hundreds of
columns that were never asked in Tunisia, and their formats disagree with each
other from one wave to the next. What is here is the same data, filtered and made
consistent, with nothing recoded.

## What's in it

| Survey | Respondents | Variables | Fieldwork | Folder |
|---|---:|---:|---|---|
| Arab Barometer Wave II | 1,196 | 468 (303 with data) | 2010–2011 | [`data/arab-barometer/wave-02`](data/arab-barometer/wave-02) |
| Arab Barometer Wave IV | 1,200 | 290 (248 with data) | 2016–2017 | [`data/arab-barometer/wave-04`](data/arab-barometer/wave-04) |
| Arab Barometer Wave V | 2,400 | 359 (281 with data) | 2018–2019 | [`data/arab-barometer/wave-05`](data/arab-barometer/wave-05) |
| Arab Barometer Wave VII | 2,400 | 453 (373 with data) | Oct–Nov 2021 | [`data/arab-barometer/wave-07`](data/arab-barometer/wave-07) |
| Arab Barometer Wave VIII | 2,406 | 690 (466 with data) | Sep–Nov 2023 | [`data/arab-barometer/wave-08`](data/arab-barometer/wave-08) |

9,602 Tunisian respondents. `catalog/catalog.csv` and `catalog/catalog.json` carry
the same table in machine-readable form, with per-file checksums.

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
| `data/raw/` | pooled multi-country releases, not tracked in git |
| `catalog/` | `catalog.json` / `catalog.csv`, generated; `sources.json`, hand-maintained |
| `docs/` | how to use the data, provenance, cross-wave variable index, missing-value codes |
| `scripts/` | extraction, verification, doc generation |

## Regenerating

Everything outside `catalog/sources.json` and the top-level docs is generated.
Put the pooled releases in `data/raw/` (see [`data/raw/README.md`](data/raw/README.md)),
then:

```bash
pip install -r scripts/requirements.txt
python3 scripts/extract_tunisia.py        # extracts + codebooks + catalog
python3 scripts/build_variable_index.py   # docs/variable-index.csv
python3 scripts/build_missing_codes.py    # docs/missing-value-codes.md
python3 scripts/verify.py                 # cell-by-cell check against the releases
```

Without the releases, `python3 scripts/verify.py --offline` checks the committed
files against the checksums and counts in `catalog/catalog.json`.

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
