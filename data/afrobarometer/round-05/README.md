# Afrobarometer Round 5 — Tunisia

| | |
|---|---|
| Respondents | 1,200 |
| Variables | 300 |
| Fieldwork (Tunisia) | 2013-01-10 to 2013-02-01 |
| Language | English (translated instrument and labels) |
| Pooled release | 1,200 respondents across 1200 countries |
| Source file | `afrobarometer_tun_r5_en.sav` |
| Publisher | Afrobarometer |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `afrobarometer-w05-tunisia-codes.csv` | 1.44 MB | `097531fe48b7c387` |
| `afrobarometer-w05-tunisia-labels.csv` | 4.69 MB | `557fd52fbc31e64c` |
| `afrobarometer-w05-tunisia.dta` | 3.32 MB | `7f18a48f787ae051` |
| `afrobarometer-w05-tunisia.sav` | 3.17 MB | `730bcf6d6a37681e` |
| `codebook.csv` | 0.08 MB | `ffa9a4994fe23c30` |
| `codebook.json` | 0.15 MB | `94378d0550badc6d` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`Q60A` ('None'), `Q60A1_TUN` ('None'), `Q60B` ('None'), `Q60C` ('None'), `Q60D` ('None'), `Q60E` ('None'), `Q60F` ('None'), `Q60G` ('None'), `Q108` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

Value labels on `STRTIME`, `ENDTIME` are not carried over. They are date or time columns,
which neither SPSS nor Stata will attach value labels to, and the labels only
marked a sentinel the reader has already parsed as a time of day.

Note: Round 5 release, English.
