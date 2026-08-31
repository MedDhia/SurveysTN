# Arab Opinion Index 2024/2025 — Tunisia

| | |
|---|---|
| Respondents | 3,245 |
| Variables | 1,251 (616 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2024-2025) |
| Language | English (translated instrument and labels) |
| Pooled release | 40,130 respondents across 15 countries |
| Source file | `aoi-2024-2025.sav` |
| Publisher | Arab Center for Research and Policy Studies (Doha Institute) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-opinion-index-2024-2025-tunisia-codes.csv` | 4.99 MB | `8b66cb6a5be5258e` |
| `arab-opinion-index-2024-2025-tunisia-labels.csv` | 9.24 MB | `d087d5b5eb82456c` |
| `arab-opinion-index-2024-2025-tunisia.dta` | 34.63 MB | `d3e1f3d760338912` |
| `arab-opinion-index-2024-2025-tunisia.sav` | 34.37 MB | `18adfa9e498763ca` |
| `codebook.csv` | 1.31 MB | `147444df2794cb28` |
| `codebook.json` | 1.59 MB | `5db42dad7cb1afd7` |

The pooled release carries items asked in only some countries, so 635 of the 1,251 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`q2025_43_1` ('None'), `q2025_44_1` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.
