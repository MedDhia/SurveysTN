# Arab Barometer Wave IV — Tunisia

| | |
|---|---|
| Respondents | 1,200 |
| Variables | 290 (248 with at least one non-missing answer in Tunisia) |
| Fieldwork (Tunisia) | not recorded in the data file (series fieldwork 2016-2017) |
| Language | English (translated instrument and labels) |
| Pooled release | 9,000 respondents across 7 countries |
| Source file | `ABIV_English.csv` |
| Publisher | Arab Barometer (Princeton University / University of Michigan) |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w04-tunisia-labels.csv` | 4.62 MB | `0fe815de59659e0f` |
| `arab-barometer-w04-tunisia.dta` | 9.00 MB | `550c134facc6d524` |
| `arab-barometer-w04-tunisia.sav` | 9.85 MB | `33f22c940edd3701` |
| `codebook.csv` | 0.05 MB | `b23707bc410c1894` |
| `codebook.json` | 0.11 MB | `2f61899b851d633e` |

The pooled release carries items asked in only some countries, so 42 of the 290 variables are entirely missing in the
Tunisia sub-sample. They are kept so that column positions line up with the
pooled release; `codebook.csv` reports `n_valid` for each.

## Derived from a label-only CSV release

Arab Barometer distributes this wave as a CSV of label text, with no SPSS or
Stata release alongside it. Two things follow, and they are limitations of the
source rather than of this extract:

- **No numeric codes.** Answers exist only as text, so there is no `-codes.csv`,
  and the `.sav` and `.dta` hold strings rather than coded categoricals. In Stata,
  `encode` them; in R, `haven::as_factor()` has nothing to do because the labels
  are already the values.
- **No question text.** The CSV carries variable names but no variable labels, so
  the `label` column of `codebook.csv` is empty. In its place the codebook records
  `observed_values`, the distinct answers each variable actually takes. For the
  question wording, use the questionnaire on the Arab Barometer site.

Columns that parse as numeric across the whole pooled release are typed numeric;
the rest are left as text. `codebook.csv` reports the storage type of each.

Dropping the SPSS release for this wave into `data/raw/`, setting
`source_format` to `sav` in `catalog/sources.json` and re-running the scripts
upgrades this folder to a full extract with codes and question text.

## Reading the CSV

`q1019b` ('None') — these are substantive answers spelled the way most CSV readers
spell a missing value. `pandas.read_csv` and friends will turn them into
missing unless you say otherwise:

```python
pd.read_csv(path, keep_default_na=False)   # then treat "" as missing
```

The `.sav` and `.dta` are unaffected.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Only the label-text CSV release was available; no numeric codes or question text.
