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

## Inequality — eight figures

`python3 scripts/build_inequality_figures.py`
`python3 scripts/build_inequality_breakdowns.py`

Eight figures for the inequality questions, indexed in
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

Spearman rank correlations among the **25 ordinal inequality items of Arab Opinion
Index 2016**, 1,499 respondents, grouped by battery with the blocks drawn apart.

**Why that survey.** Not the one with the most rows in `inequality.csv` — that is Arab
Barometer Wave VIII with 43, but 28 of those are a single multi-response question
exploded into `Q884A_*`/`Q884B_*` dummy columns. That is a count of columns, not of
questions, and ranking on it picked a survey whose 14 usable items were a grab-bag
where the three strongest cells were simply neighbouring items in the same battery.
The script now ranks surveys by the items actually eligible for the matrix — an
ordered scale of three to seven substantive answers, at least 100 respondents — read
from each `codebook.json` without loading the data.

**What it shows.** Perceived inequality is not one attitude. Inside a battery the mean
|ρ| is **0.34**; between batteries it is **0.12**. Someone who thinks equality is not
applied on one dimension is only weakly more likely to think so on another — and that
holds even where two batteries measure the same thing: *equality applied regardless of
gender/sex* and *are men and women equal in law* sit in the same questionnaire and
reach only 0.33, the strongest pair spanning two batteries.

Read the within-battery figure with care: part of it is question order and response
set rather than agreement, which is why the blocks are separated rather than left to
blend into one red field. One item argues against pure acquiescence — `Q504_3`, *"in
general, men are better than women at positions of political leadership"*, is worded
against its battery mates and correlates negatively with them (−0.13, −0.10), which is
what a real attitude does and a yea-saying pattern would not.

**Within one survey only.** Different surveys are different respondents, so there is
no cross-survey correlation to compute, and a matrix spanning them would be an
artefact of the layout rather than a finding.

The scale ends at ±0.6 rather than ±1 — on the full range every cell washes to white —
and the limit is printed on the colour bar. Grey on the diagonal is a variable against
itself; hatched cells, where any appear, are pairs never put to the same respondents,
which is not the same as a pair that was asked and came back uncorrelated.

The four above take a **question** as the unit. The four below take a **respondent**
as the unit, or step back to the archive. They come from
`scripts/build_inequality_breakdowns.py`.

All three respondent-level figures pool the eight Arab Opinion Index rounds that carry
the `Q422` equality battery — 15,539 respondents, 2012 to 2025. The 2011 round is left
out: it codes location by region rather than governorate, on codes the release's shared
multi-country label map names for another country entirely, and it carries none of the
battery anyway.

Intervals are 95% and use **Kish's effective sample size**, so the weighting is paid
for rather than ignored. The spread is the weighted sample variance, not the binomial
`p(1−p)`: for a single yes/no dimension the two agree, but the index is a mean of eight
of them and is far less variable than a coin at the same rate. No Arab Opinion Index
release carries the stratum and PSU a full design correction wants, so these are still
narrower than a design-based interval would be.

### `inequality-by-dimension.png` / `.svg`

The share saying equality is applied, ranked by dimension. **The ordering is the
finding.** Equality is reported to hold across the lines people are born on — skin
colour 64%, religion 55%, gender 54% — and to fail across the lines of money and power
— geographic area 32%, social status 31%, political influence 29%, wealth 26%. The two
ends are 38 points apart, far outside the intervals.

### `inequality-by-region.png` / `.svg`

The same, by Tunisia's seven statistical regions, alongside the one item that asks about
regional equality directly. The **Centre West** — Kairouan, Kasserine and Sidi Bouzid,
the poorest region and where the 2010 uprising began — is lowest on both measures, 37%
against 46% in the South West.

Poverty does not order the rest, and the figure says so: the South West is interior too
and ranks highest, Grand Tunis sits below both southern regions, and most adjacent pairs
have overlapping intervals. The coast/interior marker on each row is there to be checked
against the ranking, not to assert it.

The regional grouping is **not in any release**. It is applied from
[`catalog/tunisia-regions.json`](../../catalog/tunisia-regions.json), which names its
source (the INS *grandes régions*) and maps by governorate name rather than code —
the Arab Opinion Index ships one value-label map for every country it covers, so the
same code carries different names across releases.

### `inequality-by-group.png` / `.svg`

The same index by household income, education, age and sex. A panel's ends count as
**separated** when the highest group's interval clears the lowest group's — a test the
reader can run off the figure — and separated is reported apart from **ordered**, because
a difference between the ends says nothing about the order of the middle. Household
income is the only grouping that is both. Education differs end to end while running down
and back up in between; sex does not separate at all across 15,539 respondents. Flat
panels are drawn rather than dropped: a null that large is a result.

### `inequality-archive-map.png` / `.svg`

Every one of the 300 inequality variables by facet and survey, in fieldwork order — the
only inequality figure covering the whole archive rather than the questions that recur.
A variable matching two facets is counted in both, so the cells sum to more than 300, and
blank means nothing rather than a small number.

Coverage is uneven enough that the facet decides which programme you can use: the Arab
Opinion Index carries equality-as-a-principle and gender, Afrobarometer and Arab Barometer
Wave VIII carry discrimination, and wasta appears only in Arab Barometer. Four of the 26
surveys carry nothing on inequality at all. Counts are on a log scale, so a dark cell is
many times a pale one rather than a few more.

## Economic and spatial inequality — four figures

`python3 scripts/build_spatial_economic_figures.py`

The inequality figures above ask what people *think* about equality. These four ask
what they **have**, and **where**, using the two instruments in the archive that
measure material conditions rather than opinions about them. Regions are the seven
Tunisia uses for regional accounts, from
[`catalog/tunisia-regions.json`](../../catalog/tunisia-regions.json); Afrobarometer
Rounds 7–10 code them directly, Rounds 5–6 code governorates that roll up, and the
Arab Opinion Index codes governorates throughout.

**Littoral is a development category, not a coastline.** The South East (Gabes,
Medenine, Tataouine) fronts the sea but is counted outside the littoral, as it is in
Tunisia's own regional accounts.

**Batteries are matched on question wording, never on variable names.** The
lived-poverty items are `Q8A–E` in Rounds 5–7, `Q7A–E` in Rounds 8 and 10, and `Q6A–E`
in Round 9 — where `Q7A` is instead *"did not feel safe in the neighbourhood"*, which a
name-based match would fold into a poverty index without complaint.

### `spatial-conditions-and-perception.png` / `.svg`

The payoff. Left panel: each of the seven regions plotted with Afrobarometer's lived
poverty on one axis and the Arab Opinion Index's perceived equality on the other. The
two axes come from **different programmes, different respondents and different years**
— Afrobarometer 2013–2024 against the Arab Opinion Index 2012–2025 — and rank the
regions almost identically, **ρ = −0.89 (p = 0.007)**. Neither survey could produce that
agreement alone.

Right panel re-runs it inside one programme across 20 governorates, where it is weaker
but holds, **ρ = −0.64 (p = 0.002)**.

This also explains why the littoral/interior line did so little work in
`inequality-by-region`: the interior holds both the worst two regions and the best two.
The material axis orders the regions; the coastline does not.

Read as association between places. Seven points carry little weight, both panels are
ecological — they describe regions, not the individuals in them — and nothing here
identifies which way the relationship runs.

### `spatial-lived-poverty.png` / `.svg`

The Lived Poverty Index by region across six rounds, 7,198 respondents: how often a
household went without food, clean water, medical care, cooking fuel or cash income,
averaged over the five items on their 0-to-4 scale. Each panel carries the other six
regions in grey.

North West and Centre West sit above every littoral region in almost every round. 2022
is the exception — deprivation rose in most regions and they converge, rather than the
interior improving — and the steepest climb over the period is **Centre East**, a
littoral region, which nearly doubles.

### `spatial-provision.png` / `.svg`

Share of respondents whose enumeration area contains each amenity, pooled over six
rounds and weighted. Electricity is universal; almost nothing else is. A bank is in
reach for **63%** in Grand Tunis and **17%** in the North West; a sewage system for 95%
against 40% in the Centre West.

Note what this is not: an enumeration area is where the interview happened, so it
describes the places sampled rather than the territory, and "in the area" is a coarser
thing than a household connection.

### `economic-hardship-by-governorate.png` / `.svg`

Share saying household income does not cover their requirements, by governorate, pooled
over eight Arab Opinion Index rounds. This is the finest geography the archive supports
for a material measure — Afrobarometer's lived-poverty items exist only at region level
from Round 7 on.

The seven hardest governorates are all interior, from Beja at 66% down through Jendouba,
El Kef, Kairouan, Siliana, Kasserine and Sidi Bouzid. But the split is not clean: two
interior governorates, Medenine and Tataouine, sit among the five easiest. A governorate
enters with at least 150 effective respondents.

## Perception of democracy — four figures

`python3 scripts/build_democracy_figures.py`

Indexed in [`docs/topics/democracy-perception.md`](../../docs/topics/democracy-perception.md).
**Assessment, not preference** — whether Tunisians *want* democracy is a different
question and lives in [`regime-preference.md`](../../docs/topics/regime-preference.md).

**Both Afrobarometer items are matched on question wording, never variable names.**
Extent of democracy is `Q42`, `Q40`, `Q35`, `Q36`, `Q30`, `Q32` across the six rounds and
satisfaction is `Q43`, `Q41`, `Q36`, `Q37`, `Q31`, `Q33` — note that **`Q36` is the
assessment item in one round and the satisfaction item in another**, so a name-based
match would silently swap two different questions.

### `democracy-assessment-and-satisfaction.png` / `.svg`

The period is the point. Afrobarometer fielded Round 8 from 24 February to 18 March
2020, **seventeen months before Kais Saied suspended parliament on 25 July 2021**, and
Round 9 from 21 February to 17 March 2022, **seven months after**. The break falls
cleanly between two rounds of an identical question.

| | 2020 | 2022 | 2024 |
|---|---:|---:|---:|
| A democracy with minor problems or better | 47% | 28% | **53%** |
| Not a democracy at all | 22% | 32% | **16%** |
| Fairly or very satisfied | 55% | 38% | **63%** |

It fell hard across the coup and then **reversed past where it started**: by 2024 both
readings are the strongest in the series.

Three cautions are on the figure. These are separate cross-sections, not the same people
asked twice. The satisfaction scale's answer "the country is not a democracy" is not a
point on that scale and is excluded, reported separately (3% in 2022, its high point).
And a question about how democratic a country is need not hold its meaning fixed across
a change of regime — which is a reason to read the 2024 rise as a change in what
respondents say rather than a measurement of what Tunisia became.

### `democracy-rating-across-programmes.png` / `.svg`

Three programmes ask the question and none asks it the same way, so they are drawn apart
rather than joined. Left: numeric self-ratings rescaled to 0–100 on their own floor and
ceiling, each survey's raw range printed beside its point — Arab Barometer Waves II and
III run 0–10, Wave IV and both WVS waves run 1–10, so their floors are a step apart.
Right: Afrobarometer's four-point item, which has no numeric scale to rescale.

Two surveys landed in 2013 nine months apart, and that is the only check available.
**It comes out badly: they disagree by 10 points**, Arab Barometer reading 43 and the
World Values Survey 33. Read the levels as programme-specific and the movement within a
programme as the thing worth comparing.

### `democracy-perception-who.png` / `.svg`

Whether the swing was general or concentrated: the share calling Tunisia a democracy, by
region and by urban or rural residence, in the round before the coup and the two after.
Every region falls across the break and every region recovers; town and country move
together. A bar is drawn only where at least 40 effective respondents fall in the cell,
which at this resolution binds — region intervals are wide, and the ordering between
regions within a round should not be read as a ranking.

### `democracy-meaning.png` / `.svg`

What Tunisians picked as most essential to democracy, Afrobarometer Round 5, 2013. Four
separate questions each offered four candidates; shares are within a question, so options
from different questions are not rivals and the code in the right margin says which
question each came from.

**Delivery ranks far above procedure.** Basic necessities 62%, clean politics 61% and
jobs for all 55%, against free expression 15%, a critical press 13%, parties competing
fairly 12% and the right to demonstrate 4%. If that is what the word means to a
respondent, a government judged to deliver can be called democratic by someone who would
not call it liberal — which bears on the 2024 reading above without establishing it.
This was asked in 2013 and not since, so the connection is a hypothesis the archive
cannot test.

### `democracy-fear-claim.png` / `.svg`

The argument that Tunisians turned against democracy — offered widely to explain Kais
Saied's popularity — tested on its own terms, four ways, across three programmes and 17
surveys. It draws on items indexed under both `democracy-perception` and
`regime-preference`.

**The claim fails as stated.** Agreement that *"democracy has its own problems but
remains better than other systems"* never falls below **81%** in nine Arab Opinion Index
rounds and stands at **89% in 2024**. On Afrobarometer's harder forced choice —
*"democracy is preferable to any other kind of government"*, against two rival statements
— the floor is **48%, and it came in 2018**, before the coup rather than after; 2024 sits
at 55%. Asked to rate systems one at a time in 2013 and again in 2019, Tunisians moved
*away* from every alternative: a strong leader unbothered by parliament fell 48% → 22%,
rule by experts 77% → 43%, army rule 37% → 30%.

**What did change is not desire.** Two things moved, and the figure shows both rather
than only the convenient one:

- Agreement that *"democracies are characterised by indecisiveness and discord"* rose
  from **32% (2011) to 69% (2022)**, easing to 51% in 2024.
- Disapproval of **one-man rule collapsed: 84% (2013) → 63% (2018) → 40% (2020)**,
  recovering only to 48% by 2024. Disapproval of *one-party* rule barely moved over the
  same period (61% → 57%), so this is specific to personalised rule rather than a general
  softening toward authoritarianism.

The 2020 reading matters for sequencing: Afrobarometer Round 8 left the field on 18 March
2020, **seventeen months before** Saied acted. The guardrail was down first.

So the population that emerges from these data kept wanting democracy and stopped
objecting to a strongman. That is a different claim from fearing democracy, and it points
at performance rather than principle.

**Cautions.** Levels are instrument-specific and not comparable across programmes: the
Arab Opinion Index and World Values items ask for agreement with a statement and run
high; Afrobarometer forces a choice and runs lower. The 2022 Afrobarometer round is in
French and words the third rejection item as *"rejet de la dictature"* rather than of
one-man rule. Every point is a separate cross-section. And the WVS and Afrobarometer
readings on strongman rule are in some tension over 2013–2020 — approval of a strong
leader falls on one instrument while disapproval of one-man rule also falls on the other
— which is a reason to weigh the direction of movement within an instrument rather than
the levels across them.
