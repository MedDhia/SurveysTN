# Arab Barometer Wave VI Part 2 — Tunisia

| | |
|---|---|
| Respondents | 1,002 |
| Variables | 82 (78 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2020-10-06 to 2020-10-15 |
| Language | English (translated instrument and labels) |
| Pooled release | 6,037 respondents across 6 countries |
| Source file | `Arab_Barometer_Wave_6_Part_2_ENG_RELEASE.sav` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w06p2-tunisia-codes.csv` | 0.33 MB | `8fb335c5a231c068` |
| `arab-barometer-w06p2-tunisia-labels.csv` | 1.25 MB | `70420f11546bd52f` |
| `arab-barometer-w06p2-tunisia.dta` | 0.71 MB | `1625e670206c3173` |
| `arab-barometer-w06p2-tunisia.sav` | 0.66 MB | `a23a213b48abe492` |
| `codebook.csv` | 0.03 MB | `cccd13167b2be7c6` |
| `codebook.json` | 0.05 MB | `50b611dea7c81a41` |

The pooled release carries items asked in only some countries, so 4 of the 82 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Round 2, a fresh sample with its own questionnaire.
