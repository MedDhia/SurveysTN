# Arab Opinion Index 2011 — Tunisia

| | |
|---|---|
| Respondents | 1,229 |
| Variables | 196 (148 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2011) |
| Language | English (translated instrument and labels) |
| Pooled release | 14,605 respondents across 11 countries |
| Source file | `aoi-2011.sav` |
| Publisher | Arab Center for Research and Policy Studies (Doha Institute) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-opinion-index-2011-tunisia-codes.csv` | 0.76 MB | `af0be985ff37434f` |
| `arab-opinion-index-2011-tunisia-labels.csv` | 3.34 MB | `e4ca349bba4f9505` |
| `arab-opinion-index-2011-tunisia.dta` | 2.02 MB | `1ecefc040843219b` |
| `arab-opinion-index-2011-tunisia.sav` | 1.91 MB | `7ce7ba1f96f64b5a` |
| `codebook.csv` | 0.07 MB | `f52f80ce17b85ec9` |
| `codebook.json` | 0.11 MB | `057966bf6d7a65b1` |

The pooled release carries items asked in only some countries, so 48 of the 196 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`Q101_8` ('N/A') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.
