# Afrobarometer Round 9 — Tunisia

| | |
|---|---|
| Respondents | 1,200 |
| Variables | 388 (380 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2022-02-21 to 2022-03-17 |
| Language | English (translated instrument and labels) |
| Pooled release | 1,200 respondents across 1200 countries |
| Source file | `afrobarometer_tun_r9_en.sav` |
| Publisher | Afrobarometer |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `afrobarometer-w09-tunisia-codes.csv` | 1.91 MB | `f5686df1d7e519d7` |
| `afrobarometer-w09-tunisia-labels.csv` | 7.80 MB | `8dc9f63cc8643f04` |
| `afrobarometer-w09-tunisia.dta` | 4.15 MB | `b0952dd677b97f8c` |
| `afrobarometer-w09-tunisia.sav` | 4.04 MB | `41fe913a4a04d457` |
| `codebook.csv` | 0.12 MB | `9b54e3378a34f047` |
| `codebook.json` | 0.21 MB | `2b8ec7e8c722982f` |

The pooled release carries items asked in only some countries, so 8 of the 388 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

Value labels on `STRTIME` are not carried over. They are date or time columns,
which neither SPSS nor Stata will attach value labels to, and the labels only
marked a sentinel the reader has already parsed as a time of day.

Note: Round 9 release of 1 March 2023, English. Its variable labels are in French despite the English release; question text comes from the questionnaire.
