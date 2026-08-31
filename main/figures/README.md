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
