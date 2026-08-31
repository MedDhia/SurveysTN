# World Values Survey Wave 6 — Tunisia

| | |
|---|---|
| Respondents | 1,205 |
| Variables | 370 |
| Fieldwork (Tunisia) | November 2013 to December 2013 |
| Language | English (translated instrument; variable labels only, no value labels) |
| Source release | Tunisia country file, 1,205 respondents |
| Source file | `WV6_Data_Tunisia_Excel_v20221117.1.xlsx` |
| Publisher | WVS Association / JD Systems Institute |

## Files

| File | Size | SHA-256 (first 16) |
|---|---:|---|
| `codebook.csv` | 0.03 MB | `7d0f0c8b7b1878a7` |
| `codebook.json` | 0.11 MB | `4e5c23cf24c00144` |
| `world-values-survey-w06-tunisia-codes.csv` | 1.09 MB | `d9bf7fd3a9a481ad` |
| `world-values-survey-w06-tunisia.dta` | 3.63 MB | `8fe7fd738d213a36` |
| `world-values-survey-w06-tunisia.sav` | 3.44 MB | `9c8a53bf5ddd4024` |

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

Note: Excel edition, data file version 20221117.1. Country file: Tunisia only. Substantive items are V-numbered here and Q-numbered in Wave 7.
