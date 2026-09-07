# EU Neighbourhood Barometer Wave 2 — Tunisia

| | |
|---|---|
| Respondents | 1,005 |
| Variables | 513 |
| Fieldwork (Tunisia) | 2012-11-02 to 2012-12-24 |
| Language | Arabic instrument; the release labels variables and answers in English |
| Pooled release | 16,086 respondents across 16 countries |
| Source file | `ZA6289_v100.dta` |
| Publisher | European Commission (ENPI Regional Communication Programme), fieldwork by a consortium led by TNS opinion; archived by GESIS |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.08 MB | `789270373c48ca24` |
| `codebook.json` | 0.20 MB | `2cf7b8cc34e707a4` |
| `eu-neighbourhood-barometer-w02-tunisia-codes.csv` | 1.08 MB | `9892ff7120a56540` |
| `eu-neighbourhood-barometer-w02-tunisia-labels.csv` | 7.00 MB | `9c513f616023842b` |
| `eu-neighbourhood-barometer-w02-tunisia.dta` | 3.50 MB | `277d238ec35426bb` |
| `eu-neighbourhood-barometer-w02-tunisia.sav` | 4.07 MB | `dced34f29007f2f7` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

9 variables carry a value label keyed on a Stata extended missing
(`.a` to `.z`) rather than on a number — ac2_4 among them.
SPSS will not attach a label to a non-numeric key, so those labels are dropped;
in ac2_4 the dropped label was 'i: Inap. (not DZ EG TN JO LB LY PS MA in isocntry)'. No code and no answer
is lost, only the label on a missing marker no Tunisian row carries.

Note: EU Neighbourhood Barometer Autumn 2012, GESIS study ZA6289, doi:10.4232/1.12412, version 1.0.0 (2016-01-06). Commissioned by the European Commission and fielded by a consortium led by TNS opinion across sixteen neighbourhood countries and territories plus Russia. Carries a demographic country weight (w1), a sample point (p9) and a region code (p7); p7 is unlabelled in the release and is passed through as found. The wave's season name is not its fieldwork -- see docs/not-in-the-archive.md.
