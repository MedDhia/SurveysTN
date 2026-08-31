# Afrobarometer Round 10 — Tunisia

| | |
|---|---|
| Respondents | 1,200 |
| Variables | 372 (363 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2024-02-25 to 2024-03-11 |
| Language | English (translated instrument and labels) |
| Pooled release | 1,200 respondents across 1200 countries |
| Source file | `afrobarometer_tun_r10_en.sav` |
| Publisher | Afrobarometer |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `afrobarometer-w10-tunisia-codes.csv` | 1.90 MB | `de1521ef9cfcd32c` |
| `afrobarometer-w10-tunisia-labels.csv` | 6.20 MB | `3656dcf11dad83d8` |
| `afrobarometer-w10-tunisia.dta` | 3.99 MB | `a72885f083638672` |
| `afrobarometer-w10-tunisia.sav` | 3.90 MB | `ca33f5010d7c1b42` |
| `codebook.csv` | 0.11 MB | `314957c0c7d2d09f` |
| `codebook.json` | 0.19 MB | `a3fbc8c1a00bb117` |

The pooled release carries items asked in only some countries, so 9 of the 372 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`Q38A` ('None'), `Q38B` ('None'), `Q38C` ('None'), `Q38E` ('None'), `Q38F` ('None'), `Q38G` ('None'), `Q38I` ('None'), `Q38J` ('None'), `Q38K` ('None'), `Q66` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

## Renamed variables

The release uses names SPSS and Stata will not accept, so they are rewritten
here. Nothing else about them changes.

| In the release | Here |
|---|---|
| `LOCATION.LEVEL.1` | `LOCATION_LEVEL_1` |

Note: Round 10 release of 2 May 2024, updated 13 February 2025, English.
