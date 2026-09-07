# The releases these extracts come from

Tracked, not ignored. Every file the pipeline reads is here, so the archive can be
regenerated and fully verified from a clone with nothing else downloaded. The
extracts under `data/<series>/` are what you want for analysis; this directory is
the input side, and the answer to "where exactly did that number come from".

Some releases are here in more than one format because the publisher ships them
that way. The pipeline reads one per survey — the one named in
`raw_file_stem` plus `source_format` in
[`../../catalog/sources.json`](../../catalog/sources.json) — and the others are
kept because they are the same data in a form another tool may prefer.

| Survey | File the pipeline reads | Also here |
|---|---|---|
| Arab Barometer Wave II | `ABII_English.sav` | `.csv`, `.dta` |
| Arab Barometer Wave III | `ABIII_English.sav` | `.csv`, `.dta` |
| Arab Barometer Wave IV | `ABIV_English.csv` | — |
| Arab Barometer Wave V | `ArabBarometer_WaveV_English_v2.sav` | `.csv`, `.dta` |
| Arab Barometer Wave VI Parts 1–3 | `Arab_Barometer_Wave_6_Part_{1,2,3}_ENG_RELEASE.sav` | `.csv`, `.dta` |
| Arab Barometer Wave VII | `AB7_ENG_Release_Version6.sav` | `.csv`, `.dta` |
| Arab Barometer Wave VIII | `ArabBarometer_WaveVIII_English_v3.sav` | `.csv`, `.dta` |
| World Values Survey Wave 6 | `WV6_Data_Tunisia_Excel_v20221117.1.xlsx` | `.csv` |
| World Values Survey Wave 7 | `WVS_Wave_7_Tunisia_Excel_v5.0.xlsx` | — |
| Afrobarometer Rounds 6–10 | `afrobarometer_tun_r{6,7,8,9,10}_en.sav` | — |
| Arab Opinion Index, nine rounds | `aoi-<round>.sav` | — |
| Life in Transition Round IV | `lits_iv.dta` | — |
| ISSP Religion IV (2018) | `ZA7629_v1-0-0.sav` | — |
| SAHWA Youth Survey 2015 | `SAHWA_Data_file_edition_4.0.sav` | — |
| Arab Transformations Project 2014 | `ArabTransformationsProjectDataSetPublic20170428.sav` | — |
| EU Neighbourhood Barometer, six waves | `ZA628{8,9}_v100.dta`, `ZA629{0,1,2,3}_v100.dta` | — |

Where a survey ships both, the SPSS file is the one read: it is the only format
that carries the variable labels and the value labels together. Wave IV has no
SPSS release, and the two WVS waves are read from Excel because the header row
carries the question text the CSV drops. `docs/provenance.md` has the reasoning.

Seven files are Stata rather than SPSS, because that is what their publishers ship:
Life in Transition Round IV and all six EU Neighbourhood Barometer waves. Reading
Stata with its user-missing values kept has two consequences the pipeline handles and
records — extended missings (`.a` to `.z`) arrive as bare letters, and a column that
is numeric for other countries can arrive untyped. Both are in `docs/provenance.md`.

The Afrobarometer files are renamed to a consistent scheme; every other file keeps
the name its publisher gave it. `catalog/catalog.json` records a SHA-256 for each,
and `scripts/verify.py` checks it before re-deriving anything.

## Three files are fetched, not committed

GitHub refuses a file over 100 MB. The Arab Opinion Index rounds for 2019/2020 and
2024/2025 are 132 MB and 202 MB, and the Life in Transition Round IV release is over
the limit too, so they are the three exceptions to everything above and are listed in
`.gitignore` by name. Run:

```bash
python3 scripts/fetch_raw.py
```

It downloads whatever is missing from the URL recorded in `catalog/sources.json`
and checks it against the SHA-256 in `catalog/catalog.json`, so a truncated or
changed file is rejected rather than quietly extracted from. The Arab Opinion Index
publishes at a direct URL with no registration, and their server is slow and cannot
resume, so a failed transfer starts again.

The alternative was Git LFS for the whole archive, or an inconsistent rule about
which sources the repository carries. This keeps the rule simple: everything git
can hold is here, and what it cannot is one command away.

## Where they came from

- Arab Barometer — <https://www.arabbarometer.org/surveys/>, after a short registration
- World Values Survey — <https://www.worldvaluessurvey.org>, Tunisia country files
- Afrobarometer — <https://www.afrobarometer.org/data/>, Tunisia country files
- Arab Opinion Index — <https://arabindex.dohainstitute.org>, one page per round, direct download
- Life in Transition — <https://www.ebrd.com>, Round IV data page, direct download
- ISSP — GESIS study ZA7629, <https://search.gesis.org/research_data/ZA7629>, free account
- SAHWA — the Zenodo deposit, <https://doi.org/10.5281/zenodo.5747748>, CC BY-NC-SA 4.0
- Arab Transformations — the University of Aberdeen research portal, direct download. The same dataset is on the ACSS Dataverse behind a guestbook; the Aberdeen copy is open, which is why it is the one used
- EU Neighbourhood Barometer — GESIS studies ZA6288 to ZA6293, free account. The data hosts refuse scripted requests; the questionnaires, on `access.gesis.org`, do not

The last four are recent additions and their terms differ from the first four's.
**SAHWA carries an explicit licence** — CC BY-NC-SA 4.0, whose share-alike condition
travels with anything derived from it — and the Arab Transformations deposit says
"creative commons" without naming a variant. `docs/provenance.md` has a row per
series.

They are redistributed here in the form the publishers released them. Cite the
programme and the round, not this repository. See `docs/provenance.md` for terms.
