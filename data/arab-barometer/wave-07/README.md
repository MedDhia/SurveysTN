# Arab Barometer Wave VII — Tunisia

| | |
|---|---|
| Respondents | 2,400 |
| Variables | 453 (373 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2021-10-01 to 2021-11-20 |
| Language | English (translated instrument and labels) |
| Pooled release | 26,154 respondents across 12 countries |
| Source file | `AB7_ENG_Release_Version6.sav` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w07-tunisia-codes.csv` | 2.78 MB | `ef7fbaf899f1e75a` |
| `arab-barometer-w07-tunisia-labels.csv` | 7.95 MB | `176c436c2ad0f31c` |
| `arab-barometer-w07-tunisia.dta` | 8.72 MB | `f0ecdd6cf10b9515` |
| `arab-barometer-w07-tunisia.sav` | 8.47 MB | `6838f4318d0e60bb` |
| `codebook.csv` | 0.14 MB | `a569b21065cf0b76` |
| `codebook.json` | 0.24 MB | `a5bfd24760d0478d` |

The pooled release carries items asked in only some countries, so 80 of the 453 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Release version 6.
