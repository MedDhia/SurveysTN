# Using the data

Each wave folder under `data/<series>/<wave>/` holds the same respondents in
several formats. Pick by tool, not by preference — they contain identical values.
Wave IV has no `-codes.csv`, because the release it comes from has no codes.

| File | Use it when |
|---|---|
| `<stem>.sav` | SPSS, or R via `haven::read_sav()`, or Python via `pyreadstat`. Carries full variable and value labels. |
| `<stem>.dta` | Stata, or R via `haven::read_dta()`. Same content; variable labels over 80 characters are truncated. |
| `<stem>-codes.csv` | Anything that reads CSV, when you want the numeric codes and will apply labels yourself from `codebook.csv`. Not present for Wave IV. |
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

## Six things to check before you analyse

**Weights.** Every wave except Wave II carries a design weight (`wt`, `WT`);
Waves IV, V, VII and VIII carry a stratum and PSU alongside it, and the three
Wave VI rounds a PSU only. Unweighted estimates from the weighted waves are not
nationally representative.

```stata
svyset psu [pw=wt], strata(stratum)
```

**Don't-know and refused are codes, not blanks.** Arab Barometer stores them as
sentinel values and does not declare them missing, so an unguarded `mean()` will
average them into your estimate. The codes differ by wave: Wave II mostly uses 8
and 9, Wave V uses 98 and 99 alongside a block of variables coded -8 and -9, and
Waves VII and VIII use 98 and 99. Wider scales use 998/999, 99998/99999 and
longer. A handful of Wave VIII indicator variables code don't-know as `1`. Wave IV
has no codes at all — the answer reads "Don't know (Do not read)" as text. Read
`docs/missing-value-codes.md` for the full per-wave inventory, check the variable
in `codebook.csv`, and recode before analysing — there is no single rule that
covers a whole file.

**Many columns are empty here.** The pooled releases carry items asked in only
some countries. In the Tunisia sub-sample 165 of Wave II's 468 variables, 42 of
Wave IV's 290, 78 of Wave V's 359, 80 of Wave VII's 453 and 224 of Wave VIII's 690
have no data at all; the three Wave VI rounds are tighter, at 23, 4 and 7. They are
kept so column positions match the pooled release. `codebook.csv` gives `n_valid`
per variable; filter on it.

**Wave VI is three surveys, not one.** Three telephone rounds, months apart, with
separate samples and separate questionnaires. Their ID numbers overlap but do not
link: on the overlapping IDs sex agrees at chance and age almost never. Treat them
as three cross-sections.

**One answer reads as missing in CSV.** Wave IV's `q1019b`, a second-language
question, records "None" as a substantive answer — and `pandas.read_csv` turns
that into `NaN` by default, silently emptying the variable for 518 of the 1,200
Tunisian respondents. Read the labelled CSVs with `keep_default_na=False` and
treat `""` as missing, or use the `.sav` or `.dta`, which are unaffected.
`catalog/catalog.json` records this per wave under `csv_answers_read_as_missing`,
so the check runs on every wave added later.

**Variable names change case between waves.** `country` in Waves II, IV and V,
`COUNTRY` from Wave VI on, and the same for most question numbers. Match on the
upper-cased name. `docs/crosswalk.csv` does this for you: one row per variable, the
spelling used in each wave, the question each wave asked, and `n_waves`.

## Pooling waves

Read [`crosswalk.md`](crosswalk.md) first. 13 variables appear in all eight surveys
under a shared name; most appear in only one. Thirteen years of questionnaire
revision, three short pandemic rounds with cut-down instruments, and a Wave II that
predates much of the current numbering.

A shared name is not evidence of a shared question: 86 variables carry a name in
more than one wave and a wording that does not match between them. The crosswalk
gives you `text_varies_across_waves` and `lowest_text_agreement` to check that, and
the per-wave question text to read for yourself. It compares wording only — confirm
the response scale in each wave's `codebook.csv` before you stack anything, since a
question that survived unchanged can still have been rescaled.

Wave IV has no question text of its own; what the crosswalk shows for it is parsed
from its questionnaire PDF.
