# World Values Survey Wave 7 — Tunisia

| | |
|---|---|
| Respondents | 1,208 |
| Variables | 397 |
| Fieldwork (Tunisia) | 2019-04-26 to 2019-05-20 |
| Language | English (translated instrument; variable labels only, no value labels) |
| Source release | Tunisia country file, 1,208 respondents |
| Source file | `WVS_Wave_7_Tunisia_Excel_v5.0.xlsx` |
| Publisher | WVS Association / JD Systems Institute |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.04 MB | `9b4ec8af30d0e945` |
| `codebook.json` | 0.12 MB | `e0903a9dff2af23c` |
| `world-values-survey-w07-tunisia-codes.csv` | 1.31 MB | `7c24e67b4bb43d3e` |
| `world-values-survey-w07-tunisia.dta` | 3.91 MB | `0f6c4c7ef61cbf31` |
| `world-values-survey-w07-tunisia.sav` | 3.74 MB | `d4c6114383da2992` |

Every variable carries data for at least one respondent.

## Derived from the spreadsheet edition

The publisher ships this as an Excel file whose header row carries
`NAME: question text` in a single cell. The header is split into the variable
name and its label, so the question text survives into every format here.

What does not survive is the response options: the spreadsheet carries the
numeric codes and no value labels for them. There is therefore no
`-labels.csv` — it would be a second copy of `-codes.csv` — and the `.sav` and
`.dta` hold bare codes. Read the response options from the publisher's codebook.

Negative codes are non-response sentinels rather than measurements.
`codebook.csv` lists the ones each variable actually uses in `sentinel_codes`,
and `docs/missing-value-codes.md` collects them per survey. What each one means
is in the publisher's codebook; this archive does not guess.

Supplying the SPSS release for this survey and switching `source_format` to
`sav` would add the value labels with no other change.

Regenerate with `python3 scripts/extract_tunisia.py`.

Note: Excel edition, data file version 5.0. Country file: Tunisia only, not a subset of a pooled release.
