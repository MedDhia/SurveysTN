# International Social Survey Programme Religion IV (2018) — Tunisia

| | |
|---|---|
| Respondents | 1,218 |
| Variables | 139 (138 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2018) |
| Language | English (translated instrument and labels) |
| Source release | Tunisia country file, 1,218 respondents |
| Source file | `ZA7629_v1-0-0.sav` |
| Publisher | GESIS – Leibniz Institute for the Social Sciences, Cologne |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.11 MB | `1cff162d455d2820` |
| `codebook.json` | 0.14 MB | `a1fe3dc9d805e3de` |
| `issp-w2018-tunisia-codes.csv` | 0.74 MB | `42b407f7958b1b5d` |
| `issp-w2018-tunisia-labels.csv` | 2.94 MB | `8eb22bb3c2ef629b` |
| `issp-w2018-tunisia.dta` | 1.50 MB | `02e6c8cd124d09fc` |
| `issp-w2018-tunisia.sav` | 1.44 MB | `cb62c519cdab8b4f` |

The pooled release carries items asked in only some countries, so 1 of the 139 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`TN_DEGR` ('NA') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: ISSP 2018 Religion IV, Tunisia, deposited by Abdelwahab Ben Hafaiedh, DOI 10.4232/1.13516, GESIS version 1.0.0 of 9 October 2020. Released on its own rather than inside the ISSP 2018 international file: GESIS excluded it because the fieldwork used quota sampling rather than a probability sample, and because background variables were missing from the first deposit. It also carries no weight — the WEIGHT variable is empty and labelled 'No weighting' — and no interview dates. Treat it as the least comparable survey in this archive.
