# Afrobarometer Round 7 — Tunisia

| | |
|---|---|
| Respondents | 1,199 |
| Variables | 339 |
| Fieldwork (Tunisia) | 2018-03-31 to 2018-05-07 |
| Language | English (translated instrument and labels) |
| Pooled release | 1,199 respondents across 1199 countries |
| Source file | `afrobarometer_tun_r7_en.sav` |
| Publisher | Afrobarometer |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `afrobarometer-w07-tunisia-codes.csv` | 1.67 MB | `d70d6517b4c4a8db` |
| `afrobarometer-w07-tunisia-labels.csv` | 5.19 MB | `f898305c24d34ad9` |
| `afrobarometer-w07-tunisia.dta` | 3.82 MB | `04f7e86c9ea7f4ad` |
| `afrobarometer-w07-tunisia.sav` | 3.66 MB | `7a8a433c812774a7` |
| `codebook.csv` | 0.09 MB | `e0a148cdeb755cb3` |
| `codebook.json` | 0.16 MB | `d432041c499fc1b4` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`Q44A` ('None'), `Q44B` ('None'), `Q44C` ('None'), `Q44D` ('None'), `Q44E` ('None'), `Q44F` ('None'), `Q44G` ('None'), `Q44H` ('None'), `Q44I` ('None'), `Q44J` ('None'), `Q108` ('None') — these are substantive answers spelled the way most CSV readers
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

Note: Round 7 release, English.
