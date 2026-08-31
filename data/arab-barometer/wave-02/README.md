# Arab Barometer Wave II — Tunisia

| | |
|---|---|
| Respondents | 1,196 |
| Variables | 468 (303 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2010-2011) |
| Language | English (translated instrument and labels) |
| Pooled release | 12,782 respondents across 10 countries |
| Source file | `ABII_English.sav` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w02-tunisia-codes.csv` | 1.57 MB | `f554c46c3d83c4cc` |
| `arab-barometer-w02-tunisia-labels.csv` | 7.01 MB | `a34c145ff076b2ed` |
| `arab-barometer-w02-tunisia.dta` | 4.76 MB | `73fcf359c94abf73` |
| `arab-barometer-w02-tunisia.sav` | 4.51 MB | `b622b183ef4a1537` |
| `codebook.csv` | 0.23 MB | `b019d258cd6ccba5` |
| `codebook.json` | 0.32 MB | `86f6d5f1a65d7699` |

The pooled release carries items asked in only some countries, so 165 of the 468 variables are
entirely missing in the Tunisia sub-sample. They are kept so that column positions
line up with the pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Distributed CSV ships value labels as text; SAV/DTA ship numeric codes.
