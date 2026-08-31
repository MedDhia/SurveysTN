# Afrobarometer Round 8 — Tunisia

| | |
|---|---|
| Respondents | 1,200 |
| Variables | 377 |
| Fieldwork (Tunisia) | 2020-02-24 to 2020-03-18 |
| Language | English (translated instrument and labels) |
| Pooled release | 1,200 respondents across 1200 countries |
| Source file | `afrobarometer_tun_r8_en.sav` |
| Publisher | Afrobarometer |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `afrobarometer-w08-tunisia-codes.csv` | 1.88 MB | `1babe80bd228a09d` |
| `afrobarometer-w08-tunisia-labels.csv` | 6.23 MB | `856c5bd26214edca` |
| `afrobarometer-w08-tunisia.dta` | 4.02 MB | `3a907704894fb37d` |
| `afrobarometer-w08-tunisia.sav` | 3.84 MB | `f52d0d49fd55ba09` |
| `codebook.csv` | 0.10 MB | `b1d3857795b67b3b` |
| `codebook.json` | 0.19 MB | `57264074d2d68886` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`Q42A` ('None'), `Q42B` ('None'), `Q42C` ('None'), `Q42D` ('None'), `Q42E` ('None'), `Q42F` ('None'), `Q42G` ('None'), `Q42I` ('None'), `Q69B` ('None'), `Q98A` ('None'), `Q108` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Round 8 release of 31 March 2021, English.
