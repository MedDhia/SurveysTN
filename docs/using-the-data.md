# Using the data

Each wave folder under `data/<series>/<wave>/` holds the same respondents in four
formats. Pick by tool, not by preference — they contain identical values.

| File | Use it when |
|---|---|
| `<stem>.sav` | SPSS, or R via `haven::read_sav()`, or Python via `pyreadstat`. Carries full variable and value labels. |
| `<stem>.dta` | Stata, or R via `haven::read_dta()`. Same content; variable labels over 80 characters are truncated. |
| `<stem>-codes.csv` | Anything that reads CSV, when you want the numeric codes and will apply labels yourself from `codebook.csv`. |
| `<stem>-labels.csv` | Quick inspection, or tools with no notion of value labels. Answers appear as text. |

## Loading

```r
library(haven)
ab8 <- read_sav("data/arab-barometer/wave-08/arab-barometer-w08-tunisia.sav")
```

```python
import pyreadstat
df, meta = pyreadstat.read_sav(
    "data/arab-barometer/wave-08/arab-barometer-w08-tunisia.sav", user_missing=True
)
meta.column_names_to_labels["Q101"]   # the question text
meta.variable_value_labels["Q101"]    # the response options
```

```stata
use "data/arab-barometer/wave-08/arab-barometer-w08-tunisia.dta", clear
```

## Four things to check before you analyse

**Weights.** Waves V and VIII carry a design weight (`wt`, `WT`); Wave II does
not. Unweighted Wave V and VIII estimates are not nationally representative.

```stata
svyset psu [pw=wt], strata(stratum)
```

**Don't-know and refused are codes, not blanks.** Arab Barometer stores them as
sentinel values and does not declare them missing, so an unguarded `mean()` will
average them into your estimate. The codes differ by wave: Wave II mostly uses 8
and 9, Wave V uses 98 and 99 alongside a block of variables coded -8 and -9, and
Wave VIII uses 98 and 99. Wider scales use 998/999, 99998/99999 and longer. A
handful of Wave VIII indicator variables code don't-know as `1`. Read
`docs/missing-value-codes.md` for the full per-wave inventory, check the variable
in `codebook.csv`, and recode before analysing — there is no single rule that
covers a whole file.

**Many columns are empty here.** The pooled releases carry items asked in only
some countries. In the Tunisia sub-sample 165 of Wave II's 468 variables, 77 of
Wave V's 359 and 224 of Wave VIII's 690 have no data at all. They are kept so
column positions match the pooled release. `codebook.csv` gives `n_valid` per
variable; filter on it.

**Variable names change case between waves.** `country` in Waves II and V,
`COUNTRY` in Wave VIII, and the same for most question numbers. Match on the
upper-cased name. `docs/variable-index.csv` does this for you: one row per
variable, the spelling used in each wave, its label in each wave, and `n_waves`.

## Pooling waves

Only 23 variables appear in all three waves under a shared name, and 80 more in
exactly two — twelve years of questionnaire revision, and Wave II predates much of
the current numbering. Start from `docs/variable-index.csv`, and confirm from the
two labels that a shared name really is the same question before you stack it: a
matching name is not by itself evidence that the wording or the response scale
survived unchanged.
