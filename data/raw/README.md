# Pooled releases (not tracked in git)

`scripts/extract_tunisia.py` and `scripts/verify.py` read the pooled,
multi-country release files from this directory. They are not committed: they run
to roughly 300 MB, the survey programmes distribute them themselves, and the
extracts in `data/` are what this repository is for.

Download them from the publisher and drop them here, unzipped and under their
original names. The expected files, with the SHA-256 that `catalog/catalog.json`
records for each:

| File | Source |
|---|---|
| `ABII_English.sav` | Arab Barometer Wave II, English release |
| `ArabBarometer_WaveV_English_v2.sav` | Arab Barometer Wave V, English release v2 |
| `ABIII_English.sav` | Arab Barometer Wave III, English release |
| `ABIV_English.csv` | Arab Barometer Wave IV, English release (label-text CSV) |
| `Arab_Barometer_Wave_6_Part_1_ENG_RELEASE.sav` | Arab Barometer Wave VI Part 1 |
| `Arab_Barometer_Wave_6_Part_2_ENG_RELEASE.sav` | Arab Barometer Wave VI Part 2 |
| `Arab_Barometer_Wave_6_Part_3_ENG_RELEASE.sav` | Arab Barometer Wave VI Part 3 |
| `AB7_ENG_Release_Version6.sav` | Arab Barometer Wave VII, English release version 6 |
| `ArabBarometer_WaveVIII_English_v3.sav` | Arab Barometer Wave VIII, English release v3 |

Wave IV is read from CSV because no SPSS release was available for it. If you have
one, add `ABIV_English.sav` here, set that wave's `source_format` to `sav` in
`catalog/sources.json`, and re-run the scripts: the extract gains numeric codes and
question text with no other change.

Arab Barometer distributes its data from <https://www.arabbarometer.org/surveys/>
after a short registration. See `docs/provenance.md`.
