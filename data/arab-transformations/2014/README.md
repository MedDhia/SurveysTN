# Arab Transformations Project 2014 — Tunisia

| | |
|---|---|
| Respondents | 1,215 |
| Variables | 366 (364 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2014-08-10 to 2014-10-04 |
| Language | English source questionnaire, fielded in Arabic; the release labels variables and answers in English |
| Pooled release | 9,809 respondents across 6 countries |
| Source file | `ArabTransformationsProjectDataSetPublic20170428.sav` |
| Publisher | University of Aberdeen, for the EU FP7 Arab Transformations Project |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-transformations-w2014-tunisia-codes.csv` | 1.79 MB | `c4d1f218453f7ad3` |
| `arab-transformations-w2014-tunisia-labels.csv` | 6.26 MB | `3f2c849c510cdf4f` |
| `arab-transformations-w2014-tunisia.dta` | 3.75 MB | `98a82cb3ceea05c7` |
| `arab-transformations-w2014-tunisia.sav` | 3.53 MB | `773cd15c202abd94` |
| `codebook.csv` | 0.13 MB | `595746aee51d302d` |
| `codebook.json` | 0.21 MB | `d32464ad922ab5aa` |

The pooled release carries items asked in only some countries, so 2 of the 366 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`V83` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: The Arab Transformations Project's 2014 survey, an EU FP7 study run by Pamela Abbott, Andrea Teti and Roger Sapsford. Fielded in six countries -- Egypt, Iraq, Jordan, Libya, Morocco and Tunisia; the public file has no Algerian rows despite the project covering it. The instrument borrows from Arab Barometer and the World Values Survey and adds questions on the uprisings themselves, on political activity and on social media use. It is the only survey in the archive fielded in 2014 that records an interview date, so it breaks what was otherwise a two-year hole in the dated record. It carries no weight variable of any kind, and its REGION codes (700-730) are unlabelled in the release.
