# EU Neighbourhood Barometer Wave 3 — Tunisia

| | |
|---|---|
| Respondents | 1,041 |
| Variables | 549 |
| Fieldwork (Tunisia) | 2013-06-04 to 2013-06-19 |
| Language | Arabic instrument; the release labels variables and answers in English |
| Pooled release | 16,103 respondents across 16 countries |
| Source file | `ZA6290_v100.dta` |
| Publisher | European Commission (ENPI Regional Communication Programme), fieldwork by a consortium led by TNS opinion; archived by GESIS |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.09 MB | `a4b256f4898673e5` |
| `codebook.json` | 0.22 MB | `31c5a1aff12d0b3e` |
| `eu-neighbourhood-barometer-w03-tunisia-codes.csv` | 1.20 MB | `19b8c1906abbf1dd` |
| `eu-neighbourhood-barometer-w03-tunisia-labels.csv` | 8.27 MB | `7cfd6d0ebe3b636a` |
| `eu-neighbourhood-barometer-w03-tunisia.dta` | 3.67 MB | `2546d398e7e41ded` |
| `eu-neighbourhood-barometer-w03-tunisia.sav` | 4.51 MB | `e1c18e5c5cfd7cd1` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

13 variables carry a value label keyed on a Stata extended missing
(`.a` to `.z`) rather than on a number — ac2_4 among them.
SPSS will not attach a label to a non-numeric key, so those labels are dropped;
in ac2_4 the dropped label was 'i: Inap. (not DZ EG TN JO LB LY PS MA in isocntry)'. No code and no answer
is lost, only the label on a missing marker no Tunisian row carries.

Note: EU Neighbourhood Barometer Spring 2013, GESIS study ZA6290, doi:10.4232/1.12459, version 1.0.0 (2016-04-19). Commissioned by the European Commission and fielded by a consortium led by TNS opinion across sixteen neighbourhood countries and territories plus Russia. Carries a demographic country weight (w1), a sample point (p9) and a region code (p7); p7 is unlabelled in the release and is passed through as found. The wave's season name is not its fieldwork -- see docs/not-in-the-archive.md.
