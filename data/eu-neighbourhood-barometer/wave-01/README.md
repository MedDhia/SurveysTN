# EU Neighbourhood Barometer Wave 1 — Tunisia

| | |
|---|---|
| Respondents | 1,015 |
| Variables | 462 |
| Fieldwork (Tunisia) | 2012-07-07 to 2012-07-21 |
| Language | Arabic instrument; the release labels variables and answers in English |
| Pooled release | 16,196 respondents across 16 countries |
| Source file | `ZA6288_v100.dta` |
| Publisher | European Commission (ENPI Regional Communication Programme), fieldwork by a consortium led by TNS opinion; archived by GESIS |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.08 MB | `f8980685fa5c9fb6` |
| `codebook.json` | 0.18 MB | `6070a3dc95bb41ac` |
| `eu-neighbourhood-barometer-w01-tunisia-codes.csv` | 1.01 MB | `48836d98a84817fb` |
| `eu-neighbourhood-barometer-w01-tunisia-labels.csv` | 6.59 MB | `1fa86c9f2124d2ee` |
| `eu-neighbourhood-barometer-w01-tunisia.dta` | 3.17 MB | `447d26d00505f50e` |
| `eu-neighbourhood-barometer-w01-tunisia.sav` | 3.70 MB | `6049a64b9736ce5a` |

Every variable carries data for at least one respondent.

`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`
substitutes the value label wherever the release defines one. The `.sav` carries
full variable and value labels; the `.dta` is identical except that variable
labels longer than 80 characters are truncated, which Stata's format requires.
Consult `codebook.csv` for the untruncated labels.

## Reading the CSV

`bd1a` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

13 variables carry a value label keyed on a Stata extended missing
(`.a` to `.z`) rather than on a number — aa6b_19 among them.
SPSS will not attach a label to a non-numeric key, so those labels are dropped;
in aa6b_19 the dropped label was 'i: Inap. (coded 22 or 23 in AA6A)'. No code and no answer
is lost, only the label on a missing marker no Tunisian row carries.

Note: EU Neighbourhood Barometer Spring 2012, GESIS study ZA6288, doi:10.4232/1.12410, version 1.0.0 (2016-01-05). Commissioned by the European Commission and fielded by a consortium led by TNS opinion across sixteen neighbourhood countries and territories plus Russia. Carries a demographic country weight (w1), a sample point (p9) and a region code (p7); p7 is unlabelled in the release and is passed through as found. The wave's season name is not its fieldwork -- see docs/not-in-the-archive.md.
