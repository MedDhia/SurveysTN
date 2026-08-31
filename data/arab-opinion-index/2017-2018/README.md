# Arab Opinion Index 2017/2018 — Tunisia

| | |
|---|---|
| Respondents | 1,500 |
| Variables | 372 (306 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2017-2018) |
| Language | English (translated instrument and labels) |
| Pooled release | 18,830 respondents across 11 countries |
| Source file | `aoi-2017-2018.sav` |
| Publisher | Arab Center for Research and Policy Studies (Doha Institute) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-opinion-index-2017-2018-tunisia-codes.csv` | 1.76 MB | `f902fb516c1abf82` |
| `arab-opinion-index-2017-2018-tunisia-labels.csv` | 7.61 MB | `6488732382d69aa1` |
| `arab-opinion-index-2017-2018-tunisia.dta` | 4.62 MB | `5cc9a1a0ff40a560` |
| `arab-opinion-index-2017-2018-tunisia.sav` | 4.41 MB | `01227ce6b369eeae` |
| `codebook.csv` | 0.14 MB | `6fda3e8592a83a3c` |
| `codebook.json` | 0.22 MB | `70d9fc550708b5d0` |

The pooled release carries items asked in only some countries, so 66 of the 372 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.
