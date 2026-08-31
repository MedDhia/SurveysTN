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
| `ArabBarometer_WaveVIII_English_v3.sav` | Arab Barometer Wave VIII, English release v3 |

Arab Barometer distributes its data from <https://www.arabbarometer.org/surveys/>
after a short registration. See `docs/provenance.md`.
