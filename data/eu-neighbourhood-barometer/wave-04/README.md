# EU Neighbourhood Barometer Wave 4 — Tunisia

| | |
|---|---|
| Respondents | 1,009 |
| Variables | 432 |
| Fieldwork (Tunisia) | 2013-12-07 to 2013-12-20 |
| Language | Arabic instrument; the release labels variables and answers in English |
| Pooled release | 16,097 respondents across 16 countries |
| Source file | `ZA6291_v100.dta` |
| Publisher | European Commission (ENPI Regional Communication Programme), fieldwork by a consortium led by TNS opinion; archived by GESIS |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.09 MB | `7ed7d60f35aec028` |
| `codebook.json` | 0.19 MB | `df4ae2d7cbc9aa72` |
| `eu-neighbourhood-barometer-w04-tunisia-codes.csv` | 0.93 MB | `be8b6edcfd832a88` |
| `eu-neighbourhood-barometer-w04-tunisia-labels.csv` | 6.76 MB | `d8454d44028bce7f` |
| `eu-neighbourhood-barometer-w04-tunisia.dta` | 2.86 MB | `cfe9b1db956e97e2` |
| `eu-neighbourhood-barometer-w04-tunisia.sav` | 3.46 MB | `2e7f0648a96cf58c` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

Regenerate with `python3 scripts/extract_tunisia.py`.

13 variables carry a value label keyed on a Stata extended missing
(`.a` to `.z`) rather than on a number — aa7_2 among them.
SPSS will not attach a label to a non-numeric key, so those labels are dropped;
in aa7_2 the dropped label was 'i: Inap. (not DZ EG TN JO LB LY PS MA in isocntry)'. No code and no answer
is lost, only the label on a missing marker no Tunisian row carries.

Note: EU Neighbourhood Barometer Autumn 2013, GESIS study ZA6291, doi:10.4232/1.12497, version 1.0.0 (2016-04-22). Commissioned by the European Commission and fielded by a consortium led by TNS opinion across sixteen neighbourhood countries and territories plus Russia. Carries a demographic country weight (w1), a sample point (p9) and a region code (p7); p7 is unlabelled in the release and is passed through as found. The wave's season name is not its fieldwork -- see docs/not-in-the-archive.md.
