# Arab Barometer Wave VI Part 3 — Tunisia

| | |
|---|---|
| Respondents | 1,200 |
| Variables | 105 (98 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2021-03-06 to 2021-03-16 |
| Language | English (translated instrument and labels) |
| Pooled release | 7,835 respondents across 7 countries |
| Source file | `Arab_Barometer_Wave_6_Part_3_ENG_RELEASE.sav` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w06p3-tunisia-codes.csv` | 0.46 MB | `dde683b654bcb3d3` |
| `arab-barometer-w06p3-tunisia-labels.csv` | 1.60 MB | `4d6e691ba9e1b252` |
| `arab-barometer-w06p3-tunisia.dta` | 1.06 MB | `a07fb6d94fcb0c31` |
| `arab-barometer-w06p3-tunisia.sav` | 1.01 MB | `9c3f760d1a380b2b` |
| `codebook.csv` | 0.03 MB | `7996389587d44f0e` |
| `codebook.json` | 0.06 MB | `08390629368e68f9` |

The pooled release carries items asked in only some countries, so 7 of the 105 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Round 3, a fresh sample with its own questionnaire.
