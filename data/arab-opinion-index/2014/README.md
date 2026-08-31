# Arab Opinion Index 2014 — Tunisia

| | |
|---|---|
| Respondents | 1,498 |
| Variables | 555 (424 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2014) |
| Language | English (translated instrument and labels) |
| Pooled release | 26,466 respondents across 15 countries |
| Source file | `aoi-2014.sav` |
| Publisher | Arab Center for Research and Policy Studies (Doha Institute) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-opinion-index-2014-tunisia-codes.csv` | 2.56 MB | `5ac3a27c0280b246` |
| `arab-opinion-index-2014-tunisia-labels.csv` | 10.50 MB | `ef897751e4d61276` |
| `arab-opinion-index-2014-tunisia.dta` | 6.88 MB | `b22ac65ad57faf6a` |
| `arab-opinion-index-2014-tunisia.sav` | 6.58 MB | `86a8cbd687b6a9e8` |
| `codebook.csv` | 0.22 MB | `ceb1596e4c820fa3` |
| `codebook.json` | 0.34 MB | `8fbbb1bfdb897f18` |

The pooled release carries items asked in only some countries, so 131 of the 555 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.
