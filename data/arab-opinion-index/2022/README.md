# Arab Opinion Index 2022 — Tunisia

| | |
|---|---|
| Respondents | 2,400 |
| Variables | 651 (546 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2022) |
| Language | English (translated instrument and labels) |
| Pooled release | 33,690 respondents across 14 countries |
| Source file | `aoi-2022.sav` |
| Publisher | Arab Center for Research and Policy Studies (Doha Institute) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-opinion-index-2022-tunisia-codes.csv` | 3.22 MB | `9dad143a481ec6fa` |
| `arab-opinion-index-2022-tunisia-labels.csv` | 13.58 MB | `dac411f5327313fc` |
| `arab-opinion-index-2022-tunisia.dta` | 14.65 MB | `1db472374e736422` |
| `arab-opinion-index-2022-tunisia.sav` | 14.42 MB | `06f43707ed6b79b8` |
| `codebook.csv` | 1.99 MB | `bcc42fdaed286e3c` |
| `codebook.json` | 2.13 MB | `591fd0198d4dada5` |

The pooled release carries items asked in only some countries, so 105 of the 651 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.
