# Life in Transition Survey Round IV — Tunisia

| | |
|---|---|
| Respondents | 1,036 |
| Variables | 1,319 (741 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2022-10-26 to 2023-02-14 |
| Language | English (translated instrument and labels) |
| Pooled release | 37,478 respondents across 37 countries |
| Source file | `lits_iv.dta` |
| Publisher | European Bank for Reconstruction and Development, with the World Bank |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.46 MB | `531ef4358a0b30c3` |
| `codebook.json` | 0.76 MB | `87fb47bb5c0580a7` |
| `ebrd-life-in-transition-w04-tunisia-codes.csv` | 2.30 MB | `0d338c99adb2a541` |
| `ebrd-life-in-transition-w04-tunisia-labels.csv` | 6.11 MB | `8aed5b85c43e61c9` |
| `ebrd-life-in-transition-w04-tunisia.dta` | 9.08 MB | `3f93f7cd0b02b2a9` |
| `ebrd-life-in-transition-w04-tunisia.sav` | 11.23 MB | `931a729663670f15` |

The pooled release carries items asked in only some countries, so 578 of the 1,319 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`q802` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Fourth round of the EBRD/World Bank Life in Transition Survey, the first to include Tunisia. A household and attitudinal survey rather than a firm survey. Date and time columns are stored in Stata's %tc form, milliseconds since 1960-01-01, and are left as the release stores them.
