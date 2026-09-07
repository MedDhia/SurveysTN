# EU Neighbourhood Barometer Wave 5 — Tunisia

| | |
|---|---|
| Respondents | 1,006 |
| Variables | 445 |
| Fieldwork (Tunisia) | 2014-05-01 to 2014-06-29 |
| Language | Arabic instrument; the release labels variables and answers in English |
| Pooled release | 15,095 respondents across 15 countries |
| Source file | `ZA6292_v100.dta` |
| Publisher | European Commission (ENPI Regional Communication Programme), fieldwork by a consortium led by TNS opinion; archived by GESIS |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.08 MB | `82bd3569bff3f693` |
| `codebook.json` | 0.18 MB | `916913170545628f` |
| `eu-neighbourhood-barometer-w05-tunisia-codes.csv` | 0.95 MB | `0e8fffc54f6b6d34` |
| `eu-neighbourhood-barometer-w05-tunisia-labels.csv` | 7.29 MB | `7ce553e1f9e6ecf8` |
| `eu-neighbourhood-barometer-w05-tunisia.dta` | 3.24 MB | `3d406e488950c53d` |
| `eu-neighbourhood-barometer-w05-tunisia.sav` | 3.54 MB | `10ecbeaf9c0e1f49` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

34 variables carry a value label keyed on a Stata extended missing
(`.a` to `.z`) rather than on a number — aa6b_1 among them.
SPSS will not attach a label to a non-numeric key, so those labels are dropped;
in aa6b_1 the dropped label was 'i: Inap. (coded 22 or 23 in aa6a)'. No code and no answer
is lost, only the label on a missing marker no Tunisian row carries.

Note: EU Neighbourhood Barometer Spring 2014, GESIS study ZA6292, doi:10.4232/1.12524, version 1.0.0 (2016-04-22). Commissioned by the European Commission and fielded by a consortium led by TNS opinion across sixteen neighbourhood countries and territories plus Russia. Carries a demographic country weight (w1), a sample point (p9) and a region code (p7); p7 is unlabelled in the release and is passed through as found. The wave's season name is not its fieldwork -- see docs/not-in-the-archive.md.
