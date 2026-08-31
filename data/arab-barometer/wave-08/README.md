# Arab Barometer Wave VIII — Tunisia

| | |
|---|---|
| Respondents | 2,406 |
| Variables | 690 (466 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2023-09-13 to 2023-11-04 |
| Language | English (translated instrument and labels) |
| Pooled release | 15,627 respondents across 8 countries |
| Source file | `ArabBarometer_WaveVIII_English_v3.sav` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w08-tunisia-codes.csv` | 4.06 MB | `a0babe76b695be8d` |
| `arab-barometer-w08-tunisia-labels.csv` | 10.24 MB | `548f6a13972019ee` |
| `arab-barometer-w08-tunisia.dta` | 13.25 MB | `341c9150a520bf19` |
| `arab-barometer-w08-tunisia.sav` | 12.85 MB | `96aaa3b6db2145a6` |
| `codebook.csv` | 0.15 MB | `06dfba09fcc99e1b` |
| `codebook.json` | 0.30 MB | `4a7131451b93ebd3` |

The pooled release carries items asked in only some countries, so 224 of the 690 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Release v3 (archive labelled v2).
