# Arab Opinion Index 2012/2013 — Tunisia

| | |
|---|---|
| Respondents | 1,500 |
| Variables | 546 (329 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2012-2013) |
| Language | English (translated instrument and labels) |
| Pooled release | 19,421 respondents across 14 countries |
| Source file | `aoi-2012-2013.sav` |
| Publisher | Arab Center for Research and Policy Studies (Doha Institute) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-opinion-index-2012-2013-tunisia-codes.csv` | 2.12 MB | `56e0f9c7690a48bb` |
| `arab-opinion-index-2012-2013-tunisia-labels.csv` | 8.80 MB | `fb3a78d39dd2c234` |
| `arab-opinion-index-2012-2013-tunisia.dta` | 6.76 MB | `a9f2736dfb5eb7e5` |
| `arab-opinion-index-2012-2013-tunisia.sav` | 6.47 MB | `17871f45a2681d8b` |
| `codebook.csv` | 0.20 MB | `d758957590313ccc` |
| `codebook.json` | 0.32 MB | `1eff1dd42b98bdbf` |

The pooled release carries items asked in only some countries, so 217 of the 546 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.
