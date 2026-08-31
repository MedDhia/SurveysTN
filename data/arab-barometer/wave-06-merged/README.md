# Arab Barometer Wave VI — Tunisia, three rounds stacked

Derived, not a release. Built from the three Wave VI folders by
`scripts/build_wave06_merge.py`; regenerate rather than edit.

| | |
|---|---|
| Respondents | 3,207 (1005 + 1002 + 1200) |
| Variables | 192 — 40 asked in all three rounds, 135 in one |
| Rounds | Part 1 Jul 2020, Part 2 Oct 2020, Part 3 Mar 2021 |

## Read this before using it

**These are three samples, not three interviews with the same people.** The
rounds share no respondents that can be identified as shared: their `ID` values
overlap, but on the overlapping values sex agrees at chance and age almost never,
so the IDs are per-round sequence numbers. `MERGE_ID` gives each row a key that is
unique in this file; nothing links a row in one round to a row in another. Treat
the file as three pooled cross-sections and put `PART` in your model.

**Most variables were not asked in every round.** `codebook.csv` carries
`asked_in_parts` and `n_valid_where_asked` for each. A variable that is blank for
two thirds of the file is usually a variable those rounds never asked, not
non-response — check the column before reading a missingness pattern into it.

**The weights are per round.** Each round's `WT` is scaled to its own sample, so
the three sets of weights sum to three separate populations. Weighting the stacked
file with `WT` as it stands gives each round equal total weight only by accident of
its sample size. What to do depends on the estimand: for a pooled estimate treating
the rounds as equally informative, rescale within round so each contributes the
same total; for a round-by-round comparison, which is what these rounds are for,
weight and estimate within `PART` and compare. No pooled weight is supplied here,
because the right one is not a property of the data.

## Variables held apart

These carry a code that means different things in different rounds, so they are
**not** merged into one column. Each round keeps its own in `<NAME>__P<n>`:

| Variable | What disagrees |
|---|---|
| `Q1012A` | code 7: P2 “Sunni”, P3 “Shafi'i'” (+4 more codes) |

`Q1012A` is the clear case: the religious-sect list was recoded between rounds,
so code 7 is "Sunni" in Part 2 and "Shafi'i'" in Part 3. It happens to be empty
for every Tunisian respondent in all three rounds — the question was not asked in
Tunisia — so nothing is lost here in practice, but the column is split anyway
rather than merged on the assumption that it stays empty.

## Where the rounds only differed in wording

12 variables label a shared code differently
without meaning anything different — "Other" against "Other, specify: ___",
"Corruption" against "Financial and administrative corruption", the several ways a
round writes "refused". Those columns are merged and the fullest label kept. Every
one is listed in [`../../../catalog/wave-06-merge-report.json`](../../../catalog/wave-06-merge-report.json)
with the wording each round used, so the call can be checked.

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `arab-barometer-w06-tunisia-merged-codes.csv` | 1.45 MB | `ddfd311196f6b2d9` |
| `arab-barometer-w06-tunisia-merged-labels.csv` | 4.38 MB | `829516901d5034ad` |
| `arab-barometer-w06-tunisia-merged.dta` | 4.80 MB | `8525a2293619bdaa` |
| `arab-barometer-w06-tunisia-merged.sav` | 4.81 MB | `134f530abc9dc8c3` |
| `codebook.csv` | 0.06 MB | `fd9753d7a7d44b1d` |
| `codebook.json` | 0.11 MB | `74e15ec502588e68` |

`scripts/verify.py` rebuilds this file from the three round folders and compares it
cell by cell, so it cannot drift from the rounds it came from.
