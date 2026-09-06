# SAHWA Youth Survey 2015 — Tunisia

| | |
|---|---|
| Respondents | 2,000 |
| Variables | 843 (735 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2015-09-01 to 2015-10-20 |
| Language | English (translated instrument and labels) |
| Pooled release | 9,860 respondents across 5 countries |
| Source file | `SAHWA_Data_file_edition_4.0.sav` |
| Publisher | CIDOB (Barcelona Centre for International Affairs), with RECSM, Universitat Pompeu Fabra |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.21 MB | `bc6fe283e5579906` |
| `codebook.json` | 0.40 MB | `e85f1d902c99da4b` |
| `sahwa-w2015-tunisia-codes.csv` | 4.34 MB | `28036cf860ed4d15` |
| `sahwa-w2015-tunisia-labels.csv` | 8.90 MB | `5a6f01effe4b05d0` |
| `sahwa-w2015-tunisia.dta` | 13.62 MB | `7f708dcf5e1976fd` |
| `sahwa-w2015-tunisia.sav` | 13.10 MB | `b7744731ba701b69` |

The pooled release carries items asked in only some countries, so 108 of the 843 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`MIG514` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Edition 4.0 of the SAHWA Youth Survey, a five-country survey of 15-to-29-year-olds run by CIDOB with RECSM at Universitat Pompeu Fabra. Tunisian fieldwork ran in September and October 2015, ahead of the 2016 the dataset is named for. It is the only survey in the archive restricted to young people by design, so its marginals are not comparable with the general-population surveys beside it. Published on Zenodo under CC BY-NC-SA 4.0.
