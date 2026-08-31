# Questionnaires and codebooks

The published instrument for every survey in the archive, as the programme released
it. **All 25 surveys have one.** These are the documents the data was collected
with, and for some surveys they are the only place the question wording exists in
English.

They are the publishers' own documents, reproduced so the archive describes itself.
`catalog/sources.json` records the source URL for each. Cite the programme, not this
repository.

## Arab Barometer

| File | Survey | Parsed |
|---|---|---|
| `ab-w02-questionnaire.pdf` | [Wave II](../../data/arab-barometer/wave-02) | yes |
| `ab-w03-questionnaire.pdf` | [Wave III](../../data/arab-barometer/wave-03) | yes |
| `ab-w04-questionnaire.pdf` | [Wave IV](../../data/arab-barometer/wave-04) | yes |
| `ab-w05-questionnaire.pdf` | [Wave V](../../data/arab-barometer/wave-05) | yes |
| `ab-w06p1/2/3-questionnaire.pdf` | [Wave VI Parts 1–3](../../data/arab-barometer/wave-06-part-1) | yes |
| `ab-w07-questionnaire.pdf` | [Wave VII](../../data/arab-barometer/wave-07) | yes |
| `ab-w08-questionnaire.pdf` | [Wave VIII](../../data/arab-barometer/wave-08) | yes |

These nine are the only questionnaires parsed for question text. Wave IV's release
carries no variable labels at all and Wave V's are topic tags, so for those the
questionnaire is where the wording comes from.

## World Values Survey

| File | Survey | Parsed |
|---|---|---|
| `wvs-w06-questionnaire.pdf` | [Wave 6](../../data/world-values-survey/wave-06) | no |
| `wvs-w06-methodology.pdf` | Wave 6 — how the survey was run, not what it asked | no |
| `wvs-w07-questionnaire.pdf` | [Wave 7](../../data/world-values-survey/wave-07) | no |

Both instruments are the Arabic as fielded, and the Arabic does not extract as text.
It is not needed: the WVS releases carry their question wording in their own column
headers. The Wave 7 instrument earns its place another way — its first page defines
the negative sentinel codes (`-1` don't know, `-2` no answer/refused, `-3` not
applicable, `-5` missing) that the spreadsheet releases ship bare, and it is the
source `docs/missing-value-codes.md` quotes.

## Afrobarometer

| File | Round | Language | Parsed |
|---|---|---|---|
| `afro-w06-questionnaire.pdf` + `afro-w06-codebook.pdf` | [Round 6](../../data/afrobarometer/round-06) | English | no |
| `afro-w07-questionnaire.pdf` + `afro-w07-codebook.pdf` | [Round 7](../../data/afrobarometer/round-07) | English | no |
| `afro-w08-questionnaire.pdf` + `afro-w08-codebook.pdf` | [Round 8](../../data/afrobarometer/round-08) | questionnaire Arabic, codebook English | no |
| `afro-w09-questionnaire.pdf` + `afro-w09-codebook.pdf` | [Round 9](../../data/afrobarometer/round-09) | English | no |
| `afro-w10-questionnaire.pdf` + `afro-w10-codebook.pdf` | [Round 10](../../data/afrobarometer/round-10) | English | no |

**These are not parsed, and the reason is a trap worth knowing about.** Afrobarometer
numbers its variables differently from its questionnaire in places: in Round 10 the
variable `Q6` is labelled `Q5b.`, `Q52C` is labelled `Q53c.`, and 18 more diverge the
same way. Mapping a question number onto the variable of the same name would attach
the wrong question to those. The releases carry usable labels of their own, so the
cost of not parsing is small and the cost of parsing wrongly is not.

Round 8's questionnaire is the Arabic as fielded; Afrobarometer publishes no English
questionnaire for that round, and its English codebook covers the same instrument.

**Round 9 is distributed as the English release but its variable labels are in
French** — `Raison d'un entretien infructueux Ménage1`, not `Reason for Unsuccessful
Call Household 1`. The crosswalk marks every one of those 269 entries
`release label (French)` rather than letting French text pass as English. The English
questionnaire and codebook here are the English wording for that round.

## Arab Opinion Index

Nine codebooks, one per round, `aoi-2011-codebook.pdf` through
`aoi-2024-2025-codebook.pdf`. None is parsed: the releases carry full question text
as variable labels, so the codebook is documentation of the response options rather
than a source of wording.

The Arab Opinion Index calls its instrument a **codebook**. That is not the same
thing as the `codebook.csv` this archive generates in each survey folder, which
summarises the data as extracted.

The 2019/2020 one needed finding. The link the publisher prints for it,
`CodeBook-2019-2020-EN.pdf`, returns 404; the same page also links
`CodeBook-2019-2022-EN.pdf`, which is this round's codebook under a mistyped name.
That is the file here, and `catalog/sources.json` records the URL that works.

## Reading them by machine

`scripts/build_crosswalk.py` parses only the Arab Barometer set. Three things about
the extracted text matter if you write your own parser:

- Question numbers sit at the start of a line, but the prefix varies — `q101`,
  `Q127`, `aid1a`, `t302` — and the case is not stable across waves.
- Where the number sits depends on the wave. Most put it in front of the question;
  the Wave V PDF puts it alone on its own line, with the question below it and often
  a routing directive in between.
- The Afrobarometer PDFs extract **one word per line**, so a line-based reader sees
  nothing. They need the text flowed back together first.

The parse is validated against the releases that carry wording as labels, and agrees
with them on 85–97% of comparable variables per wave. Per-wave figures are in
[`../../catalog/crosswalk-report.json`](../../catalog/crosswalk-report.json).
