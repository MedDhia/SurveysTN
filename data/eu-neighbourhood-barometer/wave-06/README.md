# EU Neighbourhood Barometer Wave 6 — Tunisia

| | |
|---|---|
| Respondents | 1,006 |
| Variables | 491 (489 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | 2014-10-03 to 2014-11-24 |
| Language | Arabic instrument; the release labels variables and answers in English |
| Pooled release | 14,924 respondents across 15 countries |
| Source file | `ZA6293_v100.dta` |
| Publisher | European Commission (ENPI Regional Communication Programme), fieldwork by a consortium led by TNS opinion; archived by GESIS |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.09 MB | `7791b43de1e60e3d` |
| `codebook.json` | 0.20 MB | `384a29b3fa2b246f` |
| `eu-neighbourhood-barometer-w06-tunisia-codes.csv` | 1.03 MB | `79d22241c3df9cd8` |
| `eu-neighbourhood-barometer-w06-tunisia-labels.csv` | 7.50 MB | `882dfaed3578744e` |
| `eu-neighbourhood-barometer-w06-tunisia.dta` | 3.22 MB | `846cdaf27c4ef914` |
| `eu-neighbourhood-barometer-w06-tunisia.sav` | 3.91 MB | `5e58eefff67747d0` |

The pooled release carries items asked in only some countries, so 2 of the 491 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

17 variables carry a value label keyed on a Stata extended missing
(`.a` to `.z`) rather than on a number — aa7_2 among them.
SPSS will not attach a label to a non-numeric key, so those labels are dropped;
in aa7_2 the dropped label was 'i: Inap. (not DZ EG TN JO LB PS MA in isocntry)'. No code and no answer
is lost, only the label on a missing marker no Tunisian row carries.

Note: EU Neighbourhood Barometer Autumn 2014, GESIS study ZA6293, doi:10.4232/1.12498, version 1.0.0 (2016-04-22). Commissioned by the European Commission and fielded by a consortium led by TNS opinion across sixteen neighbourhood countries and territories plus Russia. Carries a demographic country weight (w1), a sample point (p9) and a region code (p7); p7 is unlabelled in the release and is passed through as found. The wave's season name is not its fieldwork -- see docs/not-in-the-archive.md.
