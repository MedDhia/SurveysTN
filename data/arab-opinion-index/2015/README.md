# Arab Opinion Index 2015 — Tunisia

| | |
|---|---|
| Respondents | 1,497 |
| Variables | 441 (358 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2015) |
| Language | English (translated instrument and labels) |
| Pooled release | 18,311 respondents across 12 countries |
| Source file | `aoi-2015.sav` |
| Publisher | Arab Center for Research and Policy Studies (Doha Institute) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-opinion-index-2015-tunisia-codes.csv` | 2.09 MB | `aa706b0a3f481087` |
| `arab-opinion-index-2015-tunisia-labels.csv` | 9.05 MB | `877f46b24dfe4af2` |
| `arab-opinion-index-2015-tunisia.dta` | 5.46 MB | `defdd0807d60a0b8` |
| `arab-opinion-index-2015-tunisia.sav` | 5.22 MB | `9fd86bc664b98aea` |
| `codebook.csv` | 0.17 MB | `e034f2f8c7d9bdf3` |
| `codebook.json` | 0.27 MB | `d0069c51c793c9d6` |

The pooled release carries items asked in only some countries, so 83 of the 441 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.
