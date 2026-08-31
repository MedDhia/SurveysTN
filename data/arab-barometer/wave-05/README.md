# Arab Barometer Wave V — Tunisia

| | |
|---|---|
| Respondents | 2,400 |
| Variables | 359 (281 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2018-2019) |
| Language | English (translated instrument and labels) |
| Pooled release | 27,850 respondents across 13 countries |
| Source file | `ArabBarometer_WaveV_English_v2.sav` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w05-tunisia-codes.csv` | 2.34 MB | `3fa5981a055e2fed` |
| `arab-barometer-w05-tunisia-labels.csv` | 4.90 MB | `46d1c6c631be1418` |
| `arab-barometer-w05-tunisia.dta` | 6.88 MB | `4272b5cf044c0589` |
| `arab-barometer-w05-tunisia.sav` | 6.68 MB | `31e4a06eb47733e4` |
| `codebook.csv` | 0.10 MB | `71bf3f26aa546cd0` |
| `codebook.json` | 0.18 MB | `f73d537e2bab1300` |

The pooled release carries items asked in only some countries, so 78 of the 359 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Release v2.
