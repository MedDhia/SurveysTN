# Questionnaires

The published English questionnaire for each wave, as distributed by Arab
Barometer. These are the instruments the data was collected with, and the source
of the question text in [`../crosswalk.csv`](../crosswalk.csv) wherever a release
carries no variable labels of its own.

| File | Wave | Data in the archive |
|---|---|---|
| `ab-w02-questionnaire.pdf` | Wave II | [`wave-02`](../../data/arab-barometer/wave-02) |
| `ab-w03-questionnaire.pdf` | Wave III | [`wave-03`](../../data/arab-barometer/wave-03) |
| `ab-w04-questionnaire.pdf` | Wave IV | [`wave-04`](../../data/arab-barometer/wave-04) |
| `ab-w05-questionnaire.pdf` | Wave V | [`wave-05`](../../data/arab-barometer/wave-05) |
| `ab-w06p1-questionnaire.pdf` | Wave VI Part 1 | [`wave-06-part-1`](../../data/arab-barometer/wave-06-part-1) |
| `ab-w06p2-questionnaire.pdf` | Wave VI Part 2 | [`wave-06-part-2`](../../data/arab-barometer/wave-06-part-2) |
| `ab-w06p3-questionnaire.pdf` | Wave VI Part 3 | [`wave-06-part-3`](../../data/arab-barometer/wave-06-part-3) |
| `ab-w07-questionnaire.pdf` | Wave VII | [`wave-07`](../../data/arab-barometer/wave-07) |
| `ab-w08-questionnaire.pdf` | Wave VIII | [`wave-08`](../../data/arab-barometer/wave-08) |

| `wvs-w06-questionnaire.pdf` | WVS Wave 6 | [`wave-06`](../../data/world-values-survey/wave-06) |
| `wvs-w06-methodology.pdf` | WVS Wave 6 | methodology, not the instrument |
| `wvs-w07-questionnaire.pdf` | WVS Wave 7 | [`wave-07`](../../data/world-values-survey/wave-07) |

Every survey in the archive has its instrument here.

The two WVS questionnaires are the Arabic instruments as fielded, and are **not**
parsed for question text: the Arabic does not extract as text, and it is not needed
— the WVS releases carry the question wording in their own column headers. The Wave
7 one earns its place another way. Its first page lists the technical codes in
English — `-1 Don't know`, `-2 No answer/refused`, `-3 Not applicable (filter)`,
`-5 Missing; Not applicable for other reasons` — which is the only documentation in
this archive of what the WVS negative codes mean, since the spreadsheet releases
ship them bare. `catalog/sources.json` quotes them with that page as the source.

`wvs-w06-methodology.pdf` is the WVS methodological questionnaire for Tunisia 2013:
how the survey was run rather than what it asked. It is kept as documentation and
is not parsed.

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
- Where the number sits depends on the wave. Most put it in front of the question;
  the Wave V PDF puts it alone on its own line, with the question below it and often
  a routing directive in between.
- The Wave IV PDF extracts some numbers **reversed**: `101q` for `q101`, a bidi
  artifact of the bilingual original. The parser matches both forms.
- Response options sometimes extract onto the question's own line
  (`Gender 1. Male2. Female`) and sometimes onto the following lines, depending on
  the wave.
- Answer boxes and rules extract as runs of `|__|`, underscores and dashes, and
  occasionally as untranslated Arabic. A capture that is mostly those is discarded
  rather than kept as a question.

The parse is validated against the releases that carry their own labels, and agrees
with them on 85–97% of comparable variables per wave.

Two waves cannot be checked that way and are reported as unvalidated, with the
reason, rather than given a number. Wave IV carries no labels. Wave V labels every
variable from a controlled vocabulary in capitals — `DEMOCRACY: SUITABILITY`,
`ELECTORAL PARTICIPATION: VISITED RALLY DURING PARLIAMENTARY ELECTION` — which
names the question without restating it, so a character-level comparison against
the wording scores near zero however good the parse is. Only two Wave V labels are
wording rather than tag, which is too few to conclude anything from.

The per-wave figures are in
[`../../catalog/crosswalk-report.json`](../../catalog/crosswalk-report.json).
