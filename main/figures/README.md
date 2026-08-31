# Figures

Generated. Rebuild with the script named under each figure; do not edit the output.

## `fieldwork-coverage.png` / `.svg`

`python3 scripts/build_coverage_figure.py`

When Tunisian survey fieldwork actually happened, one row per survey, 2010 to 2025.

The archive spans sixteen years. It does not cover them. Thirteen of the twenty-six
surveys record an interview date per respondent, and between them those account for
**314 distinct days** — from 17,619 of the archive's 40,388 interviews. The rest is
inference from what the publisher printed on the release.

The figure keeps three levels of knowledge apart, because drawing them alike would
claim a precision the archive does not have:

| Drawn as | Means | Surveys |
|---|---|---:|
| solid bar | an interview date per respondent; the days are exact | 13 |
| hatched bar | only the month fieldwork opened and closed | 1 |
| outlined bar | only the year the publisher gives for the wave | 12 |

### What it shows

- **No two surveys were ever in the field on the same day.** Not once in 314 days.
  But two came within **two days** of each other, and they are from different
  programmes: Afrobarometer Round 5 closed on 1 February 2013 and Arab Barometer
  Wave III opened on 3 February. That pair is as close to a contemporaneous
  cross-programme reading of Tunisia as this archive gets. The next nearest are 70
  days apart (two rounds of Arab Barometer Wave VI) and 93 days (Arab Barometer Wave
  VII and Afrobarometer Round 9).
- **The longest gap between two covered days is 1,057 days**, ending 31 March 2018 —
  most of 2015, all of 2016 and 2017 have no dated interview in the archive at all.
  The Arab Opinion Index ran in every one of those years, but its releases carry no
  dates, so the gap is a gap in what is *known*, not necessarily in what was asked.
- **Fieldwork is short.** Windows run from 5 days (Arab Barometer Wave VI Part 1) to
  53 (Wave VIII). A survey year is a fortnight of interviewing, not a year of it.
- **Early 2013 is the densest stretch in the archive.** Afrobarometer Round 5, Arab
  Barometer Wave III and — at month resolution — WVS Wave 6 all fall in that year.

### Reading it honestly

A five-day window is a third of a percent of a sixteen-year axis, so windows
shorter than 40 days are widened to stay visible. **Bar length is therefore not
readable as duration** — the exact span and day count are printed beside every row,
and that is the number to quote.

The outlined bars are the publisher's year range, not evidence that fieldwork ran
all year. They are drawn full-width across the year precisely so they cannot be
mistaken for a measured window.

### The data behind it

| File | |
|---|---|
| `fieldwork-coverage-days.csv` | one row per date, survey and interview count — the day-level record |
| `fieldwork-coverage-surveys.csv` | one row per survey: precision, span, day count, respondents |

Both are generated from the extracts in `data/`, so they carry only what the
releases record. Every date is derived, never asserted: `catalog/sources.json` names
the variable each one comes from.

## `inequality-coverage`, `-trends`, `-distributions`, `-correlations`

`python3 scripts/build_inequality_figures.py`

Four figures for the inequality questions, indexed in
[`docs/topics/inequality.md`](../../docs/topics/inequality.md). Each answers a
different question, and each has a limit worth stating before it is read.

### `inequality-coverage.png` / `.svg`

The **22 inequality questions asked in more than two surveys**, and the years each
was asked in — drawn from the concordance, so a row is a question rather than a
variable name. 16 surveys, 2012 to 2024.

Every row is one colour. No inequality question in this archive is asked by two
different programmes, so a run over time can be built inside Arab Barometer, or
inside Afrobarometer, or inside the Arab Opinion Index, and never between them.
21 of the 22 recur with an identical response scale; the one that does not is
marked `differs` and greyed.

Thirteen of the 22 are one Arab Opinion Index battery, opening with the same words
and closing with the same words. Truncating those labels at the front prints thirteen
identical rows; deleting the shared part instead leaves rows reading "religion",
"wealth", "gender/sex" — categories, with nothing left saying what was asked about
them. So the battery is drawn as a shaded block under a heading carrying the wording
its items share, *Equality … is applied in your country?*, and each row beneath it
carries only the clause that varies.

### `inequality-trends.png` / `.svg`

The share giving either affirmative answer, per question, over time — the same ten
questions as the distributions, on one common baseline.

This is the figure that answers *did it move*. Behind each panel, in grey, are the
other questions sharing its response scale, so a line is read against its siblings
rather than in isolation, which is what a battery is for. The Arab Opinion Index
battery separates sharply and stays separated: equality is most often seen as applied
regardless of **religion** (59% → 63%) and **gender/sex** (60% → 51%), least often
regardless of **wealth** (27% → 28%) and **social status** (31% → 30%). Every item in
that battery dips together in 2022 and recovers in 2024.

It buys that readability by collapsing four categories into two, which discards how
strongly people answered — so it sits beside the distributions rather than replacing
them. Each point is a separate cross-section, not a panel of the same respondents;
the line between two points is drawn to be followed, not measured.

### `inequality-distributions.png` / `.svg`

How Tunisians answered ten of the most-repeated of those questions — the twelve that
recur most, less two whose variables are empty in every survey that carries them — as
weighted shares
of substantive answers — each survey's own design weight, don't-know and refused
dropped rather than counted as an answer.

**Diverging from zero, not stacked to 100%.** A 100%-stacked bar gives a common
baseline to exactly two things: the bottom segment and the total. Every middle
category floats on the one below it, so `applied to some extent` cannot be read across
years — both of its ends move — and that comparison is the point of a battery asked
eight times. Splitting the scale at its midpoint and running the affirmative half up
from zero and the negative half down gives *each pole* a common baseline. Nothing is
aggregated away: all four categories are drawn at their real shares, which is what
this figure has over the trends.

They are also not densities. These are four-point ordinal items, and a smoothed
density over four categories invents shape between points that do not exist.

**Every panel says what it measures.** Seven of the ten belong to the same battery,
and a panel titled only "Religion" has lost the question — so each of those carries
the wording it shares with the rest of the battery on a line under its title.

**Each panel carries its own scale**, because the releases do not share one and do
not all run the same way: the Arab Opinion Index codes `applied completely` as 1,
Afrobarometer codes `very badly` as 1. Bars are oriented so the affirmative pole is
dark blue in every panel, which reverses the code order of the Afrobarometer items —
read the panel's own legend, never the colour alone, when comparing across panels.

### `inequality-correlations.png` / `.svg`

Spearman rank correlations among the ordinal inequality items of **Arab Barometer
Wave VIII**, the survey carrying the most of them (43 items, 14 of them ordinal and
populated enough to correlate).

**Within one survey only.** Different surveys are different respondents, so there is
no cross-survey correlation to compute, and a matrix spanning them would be an
artefact of the layout rather than a finding.

Almost nothing moves together: the strongest pair reaches ρ = 0.49 and most cells sit
inside ±0.1, so the scale ends at ±0.5 rather than ±1 — on the full range every cell
washes to white. The limit is printed on the colour bar. Grey on the diagonal is a
variable against itself; **hatched cells are pairs never put to the same respondents**
(split-ballot items), which is not the same as a pair that was asked and came back
uncorrelated.
