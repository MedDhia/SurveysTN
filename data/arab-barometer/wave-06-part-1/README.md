# Arab Barometer Wave VI Part 1 — Tunisia

| | |
|---|---|
| Respondents | 1,005 |
| Variables | 98 (75 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2020-07-24 to 2020-07-28 |
| Language | English (translated instrument and labels) |
| Pooled release | 5,729 respondents across 6 countries |
| Source file | `Arab_Barometer_Wave_6_Part_1_ENG_RELEASE.sav` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w06p1-tunisia-codes.csv` | 0.34 MB | `625834318466d2ed` |
| `arab-barometer-w06p1-tunisia-labels.csv` | 1.05 MB | `a77dd963464d9289` |
| `arab-barometer-w06p1-tunisia.dta` | 0.81 MB | `c54ead4e6eeda9e6` |
| `arab-barometer-w06p1-tunisia.sav` | 0.78 MB | `1678650cb06b1bb3` |
| `codebook.csv` | 0.03 MB | `fb01ba2143c2e692` |
| `codebook.json` | 0.05 MB | `5206a66207761bb7` |

The pooled release carries items asked in only some countries, so 23 of the 98 variables are
entirely missing in the Tunisia sub-sample. They are kept so that column positions
line up with the pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Round 1, fielded by telephone during the COVID-19 pandemic.
