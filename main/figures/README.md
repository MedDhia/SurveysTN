# Figures

Generated. Rebuild with the script named under each figure; do not edit the output.

## `fieldwork-coverage.png` / `.svg`

`python3 scripts/build_coverage_figure.py`

When Tunisian survey fieldwork actually happened, one row per survey, 2010 to 2025.

The archive spans sixteen years. It does not cover them. Twelve of the twenty-five
surveys record an interview date per respondent, and between them those account for
**292 distinct days** — from 16,419 of the archive's 39,188 interviews. The rest is
inference from what the publisher printed on the release.

The figure keeps three levels of knowledge apart, because drawing them alike would
claim a precision the archive does not have:

| Drawn as | Means | Surveys |
|---|---|---:|
| solid bar | an interview date per respondent; the days are exact | 12 |
| hatched bar | only the month fieldwork opened and closed | 1 |
| outlined bar | only the year the publisher gives for the wave | 12 |

### What it shows

- **No two surveys were ever in the field on the same day.** Not once in 292 days.
  Nothing here supports a same-day comparison. The closest two windows come within
  70 days of each other, and they are two rounds of the same wave — Arab Barometer
  Wave VI Parts 1 and 2. Across programmes the nearest approach is 93 days, between
  Arab Barometer Wave VII and Afrobarometer Round 9.
- **The longest gap between two covered days is 1,057 days**, ending 31 March 2018 —
  most of 2015, all of 2016 and 2017 have no dated interview in the archive at all.
  The Arab Opinion Index ran in every one of those years, but its releases carry no
  dates, so the gap is a gap in what is *known*, not necessarily in what was asked.
- **Fieldwork is short.** Windows run from 5 days (Arab Barometer Wave VI Part 1) to
  53 (Wave VIII). A survey year is a fortnight of interviewing, not a year of it.

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
