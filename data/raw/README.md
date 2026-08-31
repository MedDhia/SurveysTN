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

Where a survey ships both, the SPSS file is the one read: it is the only format
that carries the variable labels and the value labels together. Wave IV has no
SPSS release, and the two WVS waves are read from Excel because the header row
carries the question text the CSV drops. `docs/provenance.md` has the reasoning.

The Afrobarometer files are renamed to a consistent scheme; every other file keeps
the name its publisher gave it. `catalog/catalog.json` records a SHA-256 for each,
and `scripts/verify.py` checks it before re-deriving anything.

## Two files are fetched, not committed

GitHub refuses a file over 100 MB. The Arab Opinion Index rounds for 2019/2020 and
2024/2025 are 132 MB and 202 MB, so they are the two exceptions to everything above
and are listed in `.gitignore` by name. Run:

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

They are redistributed here in the form the publishers released them. Cite the
programme and the round, not this repository. See `docs/provenance.md` for terms.
