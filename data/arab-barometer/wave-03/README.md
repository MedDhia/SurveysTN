# Arab Barometer Wave III — Tunisia

| | |
|---|---|
| Respondents | 1,199 |
| Variables | 296 (247 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2013-02-03 to 2013-03-25 |
| Language | English (translated instrument and labels) |
| Pooled release | 14,809 respondents across 12 countries |
| Source file | `ABIII_English.sav` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w03-tunisia-codes.csv` | 1.19 MB | `6a6e2579fd31c41c` |
| `arab-barometer-w03-tunisia-labels.csv` | 5.21 MB | `a1b740a76a6072f6` |
| `arab-barometer-w03-tunisia.dta` | 2.99 MB | `a29c4b86846941c8` |
| `arab-barometer-w03-tunisia.sav` | 2.83 MB | `7142db6125add3b8` |
| `codebook.csv` | 0.11 MB | `39c90875a10a708e` |
| `codebook.json` | 0.18 MB | `5cecdb182f381592` |

The pooled release carries items asked in only some countries, so 49 of the 296 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.
