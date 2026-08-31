# Using the data

Each survey folder under `data/<series>/<wave>/` holds the same respondents in
several formats. Pick by tool, not by preference — they contain identical values.
Two are short of one file, because the release they come from is: Arab Barometer
Wave IV has no `-codes.csv`, and the two WVS waves have no `-labels.csv`.

| File | Use it when |
|---|---|
| `<stem>.sav` | SPSS, or R via `haven::read_sav()`, or Python via `pyreadstat`. Carries full variable and value labels. |
| `<stem>.dta` | Stata, or R via `haven::read_dta()`. Same content; variable labels over 80 characters are truncated. |
| `<stem>-codes.csv` | Anything that reads CSV, when you want the numeric codes and will apply labels yourself from `codebook.csv`. Not present for Arab Barometer Wave IV, which has no codes. |
| `<stem>-labels.csv` | Quick inspection, or tools with no notion of value labels. Answers appear as text. Not present for either WVS wave, whose releases define no value labels to substitute. |

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

## Seven things to check before you analyse

**Weights.** Every survey here carries a design weight except Arab Barometer Wave
II, and each series names it differently:

| Series | Weight | Design variables alongside it |
|---|---|---|
| Arab Barometer | `wt`, `WT` | stratum and PSU in Waves IV, V, VII, VIII; PSU only in the Wave VI rounds; none in Wave III |
| World Values Survey | `W_WEIGHT` | — |
| Afrobarometer | `withinwt` (Rounds 6–7), `withinwt_ea` and `withinwt_hh` (Rounds 8–10) | — |
| Arab Opinion Index | `Weight` | — |

Unweighted estimates from a weighted survey are not nationally representative.

```stata
svyset psu [pw=wt], strata(stratum)
```

**The series do not share a question numbering, and some do not keep their own.**
`Q1` is the governorate in Arab Barometer, "Important in life: Family" in the World
Values Survey, and the country code in the Arab Opinion Index — so the crosswalk
matches within a series only, and so should you. Within WVS, Wave 6 numbers its items `V`-something and Wave 7 `Q`-something —
`V9` and `Q6` are the same question — so name matching finds only the derived
indices. Afrobarometer renumbers between rounds while keeping the `Q` prefix, which is
worse: a shared name there is often a different question, and 423 of its 901
variables are flagged for wording that does not match. The Arab Opinion Index names
many variables for the year they were asked in — `Q2020_71_1`, `q2025_43_1` — so its
rounds overlap little by construction: 54 of 2,813 variables appear in all nine. Use
[`crosswalk-suggested.csv`](crosswalk-suggested.csv), which pairs them by question
text, and confirm against the WVS crosswalk before relying on a pair.

**Don't-know and refused are codes, not blanks.** Arab Barometer stores them as
sentinel values and does not declare them missing, so an unguarded `mean()` will
average them into your estimate. The codes differ by survey. In Arab Barometer,
Wave II mostly uses 8 and 9, Wave V uses 98 and 99 alongside a block of variables
coded -8 and -9, and Waves VII and VIII use 98 and 99; wider scales use 998/999,
99998/99999 and longer, and a handful of Wave VIII indicator variables code
don't-know as `1`. Wave IV has no codes at all — the answer reads "Don't know (Do
not read)" as text. WVS Wave 7 uses negative codes — −1, −2, −3, −5 — and ships no
value labels saying which is which. Their meanings are in the Wave 7 questionnaire
and are quoted in `docs/missing-value-codes.md`; Wave 6 also uses a `-4` that the
questionnaire does not list. Afrobarometer labels its own, mostly 8, 9, 98 and 99, and so does
the Arab Opinion Index. Read
`docs/missing-value-codes.md` for the full per-survey inventory, check the variable
in `codebook.csv`, and recode before analysing — there is no single rule that
covers a whole file.

**Many columns are empty here.** A pooled release carries items asked in only some
countries, and they survive into the Tunisia subset as empty columns. It is worst
in the largest files: 635 of the Arab Opinion Index 2024/2025 round's 1,251
variables have no data at all, 224 of Arab Barometer Wave VIII's 690, and 165 of
Wave II's 468. The Afrobarometer and WVS country files are the clean ones, with
almost nothing empty. Columns are kept so positions match the release;
`codebook.csv` gives `n_valid` per variable, and filtering on it is usually the
first thing to do.

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

## Pooling surveys

Read [`crosswalk.md`](crosswalk.md) first. Across every series, most variables
appear in exactly one survey, and how much genuinely carries over differs sharply:

| Series | Present in all its surveys | Named alike but worded differently |
|---|---:|---:|
| Arab Barometer | 13 of 1,966 | 97 |
| World Values Survey | 43 of 724 | 3 |
| Afrobarometer | 61 of 901 | 423 |
| Arab Opinion Index | 54 of 2,813 | 3 |

A shared name is not evidence of a shared question — Afrobarometer is the warning,
where a name that persists across rounds is often a different item. The crosswalk
gives you `text_varies_across_waves` and `lowest_text_agreement` to check, and the
per-survey question text to read for yourself. It compares wording only, so confirm
the response scale in each survey's `codebook.csv` before you stack anything: a
question that survived unchanged can still have been rescaled.

Two surveys need their question text read from elsewhere. Arab Barometer Wave IV
has none of its own, so what the crosswalk shows for it is parsed from its
questionnaire. Wave V has labels, but they are topic tags rather than wording.
