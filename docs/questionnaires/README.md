# Questionnaires

The published English questionnaire for each wave, as distributed by Arab
Barometer. These are the instruments the data was collected with, and the source
of the question text in [`../crosswalk.csv`](../crosswalk.csv) wherever a release
carries no variable labels of its own.

| File | Wave | Data in the archive |
|---|---|---|
| `ab-w02-questionnaire.pdf` | Wave II | [`wave-02`](../../data/arab-barometer/wave-02) |
| `ab-w03-questionnaire.pdf` | Wave III | — no Wave III release added yet |
| `ab-w04-questionnaire.pdf` | Wave IV | [`wave-04`](../../data/arab-barometer/wave-04) |
| `ab-w06p1-questionnaire.pdf` | Wave VI Part 1 | [`wave-06-part-1`](../../data/arab-barometer/wave-06-part-1) |
| `ab-w06p2-questionnaire.pdf` | Wave VI Part 2 | [`wave-06-part-2`](../../data/arab-barometer/wave-06-part-2) |
| `ab-w06p3-questionnaire.pdf` | Wave VI Part 3 | [`wave-06-part-3`](../../data/arab-barometer/wave-06-part-3) |
| `ab-w07-questionnaire.pdf` | Wave VII | [`wave-07`](../../data/arab-barometer/wave-07) |
| `ab-w08-questionnaire.pdf` | Wave VIII | [`wave-08`](../../data/arab-barometer/wave-08) |

Two gaps. **Wave V has no questionnaire here**, so its entries in the crosswalk
rest on its release labels alone — which is workable, because Wave V labels every
variable. **Wave III has a questionnaire but no data**; it is kept as the
instrument for a release that can be added later.

The source URL for each file is recorded per wave in
[`../../catalog/sources.json`](../../catalog/sources.json), under `questionnaire`.
They were downloaded from <https://www.arabbarometer.org>, which publishes them
openly; they are the publisher's documents, reproduced here so the archive
describes itself. Cite Arab Barometer, not this repository.

## Reading them by machine

`scripts/build_crosswalk.py` parses these PDFs into question number → question
text. Three things about the extracted text are worth knowing if you write your
own parser:

- Question numbers sit at the start of a line, but the prefix varies — `q101`,
  `Q127`, `aid1a`, `t302` — and the case is not stable across waves.
- The Wave IV PDF extracts some numbers **reversed**: `101q` for `q101`, a bidi
  artifact of the bilingual original. The parser matches both forms.
- Response options sometimes extract onto the question's own line
  (`Gender 1. Male2. Female`) and sometimes onto the following lines, depending on
  the wave.

The parse is validated against the releases that carry their own labels, and
agrees with them on 88–96% of comparable variables per wave. The per-wave figures
are in [`../../catalog/crosswalk-report.json`](../../catalog/crosswalk-report.json).
