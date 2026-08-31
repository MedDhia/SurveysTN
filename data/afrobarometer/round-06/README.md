# Afrobarometer Round 6 — Tunisia

| | |
|---|---|
| Respondents | 1,200 |
| Variables | 334 |
| Fieldwork (Tunisia) | 2015-04-14 to 2015-05-09 |
| Language | English (translated instrument and labels) |
| Pooled release | 1,200 respondents across 1200 countries |
| Source file | `afrobarometer_tun_r6_en.sav` |
| Publisher | Afrobarometer |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `afrobarometer-w06-tunisia-codes.csv` | 1.60 MB | `2becdebc1a99e182` |
| `afrobarometer-w06-tunisia-labels.csv` | 5.35 MB | `50021569c3230aff` |
| `afrobarometer-w06-tunisia.dta` | 4.19 MB | `aa09d60dfe6b53f4` |
| `afrobarometer-w06-tunisia.sav` | 4.09 MB | `ae7013b0a0258713` |
| `codebook.csv` | 0.10 MB | `e9ea501de9140f8c` |
| `codebook.json` | 0.17 MB | `6845f773d4832dd6` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`Q53A` ('None'), `Q53B` ('None'), `Q53C` ('None'), `Q53D` ('None'), `Q53E` ('None'), `Q53F` ('None'), `Q53G` ('None'), `Q53H` ('None'), `Q53I` ('None'), `Q53J` ('None'), `Q81A` ('None'), `Q98A` ('     None'), `Q108` ('None') — these are substantive answers spelled the way most CSV readers
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

Note: Round 6 release, English.
