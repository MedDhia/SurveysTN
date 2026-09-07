# Questionnaires and codebooks

The published instrument for every survey in the archive, as the programme released
it — **every survey has one**, and `scripts/verify.py` prints the count each run
rather than this page asserting a number that rots. These are the documents the data
was collected with, and for some surveys they are the only place the question wording
exists in English.

They are the publishers' own documents, reproduced so the archive describes itself.
`catalog/sources.json` records where each came from. Cite the programme, not this
repository.

`scripts/verify.py` checks the claim rather than repeating it: every survey must
have a questionnaire, the file must be present, open and have content, no two surveys
may point at the same file, and each must record a source. Any of those failing is an
error, because each is a way of appearing to have an instrument without having one.
The check covers supporting documents too, so a declared file that is missing fails
the same way as a missing questionnaire.

Almost all are PDFs. The one exception is the Arab Transformations questionnaire,
which the project publishes as a Word document and which is kept in that form rather
than converted; the check reads it as a Word document and asks the same questions of
it.

Most entries carry a direct URL. The two World Values Survey instruments do not:
the WVS serves its documentation through a download form rather than a stable file
address, so those record the wave's documentation page and the document id the file
is published under (`F00002608`, `F00010989`) instead of a link that would break.

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

These nine are the only questionnaires parsed for question text, in the whole archive.
Wave IV's release carries no variable labels at all and Wave V's are topic tags, so
for those the questionnaire is where the wording comes from. Every other series
labels its variables with the question, so parsing its instrument would add nothing
and could introduce error.

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
| `afro-w05-questionnaire.pdf` + `afro-w05-codebook.pdf` | [Round 5](../../data/afrobarometer/round-05) | English | no |
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

## Life in Transition Survey

`lits-w04-questionnaire.pdf`, English, for [Round IV](../../data/ebrd-life-in-transition/round-04).
Not parsed: the release labels every one of its 1,319 variables, so the wording is
already in the data.

## International Social Survey Programme

The 2018 Religion module is the most heavily documented survey here, because it needs
to be. Six documents, all from the GESIS deposit:

| File | What it is |
|---|---|
| `issp-2018-questionnaire.pdf` | the Tunisian field questionnaire, in Arabic |
| `issp-2018-read-me.pdf` | why GESIS released it on its own rather than in the international file |
| `issp-2018-study-description.pdf` | the depositor's account of the design, and the only statement of when fieldwork ran |
| `issp-2018-background-variables.pdf` | how each background variable was asked and coded in Tunisia |
| `issp-2018-population-characteristics.pdf` | the population benchmarks the quotas were set against |
| `issp-2018-study-monitoring.pdf` | the fieldwork-process form returned to the ISSP methodology committee |

None is parsed; the release labels every variable in English. They are here because
three things worth knowing about this survey are in them and not in the data file:
why it was excluded from the international file, how the sample was actually drawn,
and a fieldwork date that **contradicts the data**. The study description gives 6
January to 8 February 2019; `DATEYR` says 2018 for every respondent. The archive
reports the year the data carries and records the disagreement rather than choosing.

## SAHWA Youth Survey

`sahwa-2015-tunisia-questionnaire.pdf`, the Tunisian national questionnaire in French
and Arabic, for [2015](../../data/sahwa/2015-youth). Not parsed: the release labels
all 843 of its variables.

## Arab Transformations Project

`arabtrans-2014-questionnaire.docx`, version 2.1 of the source questionnaire, English,
for [2014](../../data/arab-transformations/2014). **The only instrument here that is
not a PDF** — the project publishes a Word document, and it is kept as published
rather than converted. Not parsed: the release labels all 366 of its variables.

## EU Neighbourhood Barometer

| File | Wave | Study |
|---|---|---|
| `enb-w01-tunisia-questionnaire.pdf` | [Wave 1](../../data/eu-neighbourhood-barometer/wave-01) | ZA6288 |
| `enb-w02-tunisia-questionnaire.pdf` | [Wave 2](../../data/eu-neighbourhood-barometer/wave-02) | ZA6289 |
| `enb-w03-tunisia-questionnaire.pdf` | [Wave 3](../../data/eu-neighbourhood-barometer/wave-03) | ZA6290 |
| `enb-w04-tunisia-questionnaire.pdf` | [Wave 4](../../data/eu-neighbourhood-barometer/wave-04) | ZA6291 |
| `enb-w05-tunisia-questionnaire.pdf` | [Wave 5](../../data/eu-neighbourhood-barometer/wave-05) | ZA6292 |
| `enb-w06-tunisia-questionnaire.pdf` | [Wave 6](../../data/eu-neighbourhood-barometer/wave-06) | ZA6293 |

The Tunisian field questionnaires, in Arabic, one per wave. None is parsed; the
releases label their variables in English.

These six came from `access.gesis.org`, which serves GESIS's documentation to an
ordinary request. The hosts that serve the *data* — `dbk.gesis.org`,
`search.gesis.org`, `www.gesis.org` — answer a scripted request with a challenge page
and need an account. That split is why this archive could confirm Tunisia's presence
in all six waves from the questionnaires before it had any of the data.

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
