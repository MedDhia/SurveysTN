# What is not in the archive

A repository of surveys is only useful if it says what it leaves out. This is the
gap list: every Tunisia survey programme checked, whether it is here, and if not,
why not.

Checked September 2026 against the publishers' own catalogues. Where a claim rests
on a source rather than on the data in this repository, the source is linked.

## Eight of the nine series here are complete

Each series starts where it does because that is when Tunisia entered it, not
because a wave is missing. The EU Neighbourhood Barometer is the one exception, and
its missing wave is named below.

| Series | Here | Why it starts there |
|---|---|---|
| Arab Barometer | Waves II–VIII (9 surveys) | [Wave I (2006–07)](https://www.arabbarometer.org/surveys/arab-barometer-wave-i/) covered Algeria, Jordan, Kuwait, Lebanon, Morocco, Palestine and Yemen. Tunisia first appears in Wave II, fielded after the 2010–11 uprising. |
| World Values Survey | Waves 6 and 7 | The [IHSN catalogue](https://catalog.ihsn.org/catalog?ps=50&sk=Tunisia+World+Values+Survey) lists two Tunisia WVS studies and no earlier one. Tunisia is not in Waves 1–5. |
| Afrobarometer | Rounds 5–10 (6 surveys) | Afrobarometer's own [country page](https://www.afrobarometer.org/countries/tunisia/) records surveys in 2013, 2015, 2018, 2020, 2022 and 2024 — six, and all six are here. North Africa entered the series with the round fielded in Tunisia in January 2013. |
| Arab Opinion Index | All 9 rounds, 2011 to 2024/2025 | The series began in 2011; every round since is here. |
| Life in Transition | Round IV only | [LiTS I–III](https://www.ebrd.com/home/what-we-do/office-of-the-chief-economist/lits/life-in-transition-survey-data.html) did not cover Tunisia. Round IV (2022–23) is the first to. |
| ISSP | Religion IV (2018) only | Tunisia has taken part in one ISSP module. GESIS releases it on its own as [ZA7629](https://search.gesis.org/research_data/ZA7629) rather than inside the ISSP 2018 international file, because of the quota sampling used and because background variables were missing from the first deposit. No other module carries a Tunisian sample. |
| SAHWA | Youth Survey 2015 only | The [SAHWA project](https://www.cidob.org/en/projects/sahwa) ran one survey round, in 2015–16, and Tunisia is in it. The project ended in 2017 and no second round was fielded. |
| Arab Transformations | 2014 only | A single-round EU FP7 study, fielded in late 2014 and completed in 2017. There was no second wave. The public file also has no Algerian rows, though the project covered Algeria. |
| EU Neighbourhood Barometer | Waves 1, 3, 4, 5 and 6 (5 of 6) | Tunisia is in all six waves. **Wave 2 (ZA6289, fielded November–December 2012) is the one gap in this archive that is a missing wave rather than a missing programme.** Everything needed to close it is recorded: the study number, the Tunisian questionnaire at [dbk/58182](https://access.gesis.org/dbk/58182), and a wave spec that only needs the release file dropping into `data/raw/`. |

**Open at the far end.** WVS Wave 8 is in the field for 2024–2026 and Tunisia's
participation is not yet established; Arab Barometer, Afrobarometer, the Arab
Opinion Index and LiTS are all continuing series, and the ISSP fields a module a
year that Tunisia may rejoin. SAHWA and Arab Transformations are the two closed
series: both projects ended, so their rows will not grow. This list will go stale.

## Programmes covering Tunisia that are absent

### Would fit, and could be added

These are attitudinal surveys of individuals — the same unit of analysis as
everything here — and their microdata is obtainable.

| Programme | Tunisia coverage | Access |
|---|---|---|
| **Pew Global Attitudes** | 2012, 2013 and 2014, ~1,000 face-to-face interviews each ([2014 methods](https://www.pewresearch.org/global/2014/10/15/tunisia-survey-methods-2/)) | Free Pew Research Center account. Their terms restrict redistribution, so a clone could not carry the files; the catalogue entry and a fetch script could. |

### Cover Tunisia but do not fit

- **World Bank / EBRD / EIB Enterprise Surveys** (2013 and 2024). The respondent is
  a firm, not a person, and the microdata is licensed behind a signed
  confidentiality declaration that forbids redistribution. Already recorded in the
  README.
- **UNICEF MICS**, **PAPFAM** and the national statistics institute's household
  surveys. Household and demographic instruments rather than opinion surveys; they
  measure conditions, not attitudes.

### Cannot be redistributed

- **Gallup World Poll.** Annual, covers Tunisia, and is the longest continuous
  series on the country — but it is a commercial product sold under licence. No
  part of it can be committed here.
- **Sigma Conseil, Emrhod Consulting** and the other Tunisian polling houses.
  Published as toplines in the press; the microdata is client-owned and not
  released.
- **ASDA'A BCW Arab Youth Survey.** Reports only; no microdata is published.

## What has not been checked

Named here so the list does not read as exhaustive when it is not: the Anna Lindh
Foundation's Intercultural Trends survey, Transparency International's Global
Corruption Barometer MENA editions, the ILO School-to-Work Transition Survey, and
one-off academic surveys fielded in Tunisia after 2011 and deposited with ICPSR or
the UK Data Service. Each may cover Tunisia; none has been verified either way.

## What the last pass could not reach

Recorded so that a later attempt starts from the right place rather than repeating
the work.

**GESIS is not reachable from an automated client.** `dbk.gesis.org`,
`search.gesis.org` and `www.gesis.org` all answer a scripted request with a challenge
page. That is why the ISSP file in this archive was added by hand, and why the EU
Neighbourhood Barometer's Tunisia coverage above is still an inference from the
programme description rather than a fact read off a release. Both need a browser and
a GESIS account.

**Tunisia is in all six EU Neighbourhood Barometer waves.** This was an inference
until it was checked, one wave at a time, against the Tunisian field questionnaire
GESIS deposits for each. Five of the six are now in the archive; the table is kept
because it is the record of how coverage was established, and because Wave 2 still
needs it:

| Wave | Study | Fieldwork, all countries | Tunisian fieldwork | In the archive |
|---|---|---|---|---|
| 1 | ZA6288 | July–August 2012 | 7–21 July 2012 | yes |
| 2 | ZA6289 | November–December 2012 | — | **no** |
| 3 | ZA6290 | June–July 2013 | 4–19 June 2013 | yes |
| 4 | ZA6291 | December 2013 – January 2014 | 7–20 December 2013 | yes |
| 5 | ZA6292 | May–June 2014 | 1 May – 29 June 2014 | yes |
| 6 | ZA6293 | Autumn 2014 | 3 October – 24 November 2014 | yes |

The Tunisian columns are derived from `p1d` and `p1m` in the releases themselves. The
all-country column comes from the cover of each wave's basic questionnaire.

**Do not trust the season in the wave name.** "Spring 2012" was fielded in July;
"Autumn 2013" ran into January 2014 across the programme, though Tunisia's share of it
was December. The names are the programme's labels for its rounds, not statements
about when interviewers were in the field.

The Wave 6 cover's own date line is unreadable — the PDF uses a subset font whose
digits do not map back to characters — which is why that row was once left at the wave
label. The data settled it: **3 October to 24 November 2014**.

**`access.gesis.org` answers a scripted request; the hosts that carry the data do
not.** `dbk.gesis.org`, `search.gesis.org` and `www.gesis.org` all return a challenge
page, which is why this was recorded as unverifiable. The documentation host serves
PDFs directly, and every one of the questionnaires above came from it. That settles
coverage. It does not settle access: the microdata still needs a GESIS account, so
the programme stays on this list.

**A dataset can be gated in one place and open in another.** The Arab Transformations
Project is in this archive because it is deposited twice: behind a guestbook on the
ACSS Dataverse, and openly on the University of Aberdeen research portal, which is
where these files came from. When a deposit looks closed, it is worth checking
whether the authors' own institution holds a copy before recording it as unavailable.

Regenerating this list is manual. If you add a programme, record it in
`catalog/sources.json` and move its row out of this file.
