# Arab Opinion Index 2016 — Tunisia

| | |
|---|---|
| Respondents | 1,499 |
| Variables | 479 (412 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2016) |
| Language | English (translated instrument and labels) |
| Pooled release | 18,311 respondents across 12 countries |
| Source file | `aoi-2016.sav` |
| Publisher | Arab Center for Research and Policy Studies (Doha Institute) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-opinion-index-2016-tunisia-codes.csv` | 2.22 MB | `7c2885385c69d86f` |
| `arab-opinion-index-2016-tunisia-labels.csv` | 9.77 MB | `1beb382fd7bd2f4d` |
| `arab-opinion-index-2016-tunisia.dta` | 5.94 MB | `406a1da4e1345812` |
| `arab-opinion-index-2016-tunisia.sav` | 5.67 MB | `5720b2a3be21f00d` |
| `codebook.csv` | 0.18 MB | `cf0d374760e03ae1` |
| `codebook.json` | 0.28 MB | `8feec704af856ad2` |

The pooled release carries items asked in only some countries, so 67 of the 479 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.
