# Adding a survey

The repository is a thin pipeline over publisher releases, so adding a survey
means describing it rather than committing files by hand.

## If the survey is another wave of a series already here

1. Put the pooled release in `data/raw/`.
2. Append an entry to the `waves` array in `catalog/sources.json`:

   ```json
   {
     "series": "arab-barometer",
     "wave": 7,
     "wave_label": "Wave VII",
     "slug": "wave-07",
     "raw_file_stem": "ArabBarometer_WaveVII_English_v3",
     "country_var": "COUNTRY",
     "fieldwork_years_series": "2021-2022",
     "fieldwork_tunisia": null,
     "fieldwork_source": "not recorded in the data file",
     "notes": ""
   }
   ```

   `raw_file_stem` is the filename in `data/raw/` without its extension;
   `country_var` is spelled as the release spells it. If the release records an
   interview date per respondent, set `"fieldwork_tunisia": "derive"` and
   `"fieldwork_date_var"` to the date variable, and the extractor will read the
   window out of the data instead of taking it on trust.

   A wave fielded in separate rounds — as Wave VI was — takes a `part` number as
   well, and becomes one entry per round with its own `slug`. The extractor tags
   those `w06p1`, `w06p2`, `w06p3`.

   Add `questionnaire` with the published instrument's path and source URL if one
   exists, and put the PDF in `docs/questionnaires/` as `ab-<tag>-questionnaire.pdf`.
   The crosswalk parses it for question text, which matters most when the release
   has no variable labels.

3. Run the scripts in the order given in the README, and commit what changes.

## If it is a new series

Add it to the `series` object first, including the value its country variable
takes for Tunisia:

```json
"afrobarometer": {
  "name": "Afrobarometer",
  "prefix": "afro",
  "publisher": "Afrobarometer",
  "homepage": "https://www.afrobarometer.org",
  "data_page": "https://www.afrobarometer.org/data/",
  "country_variable_values": {"tunisia": 30}
}
```

`prefix` is the short tag the crosswalk uses to name that series' columns, and it
must be unique: variables are matched within a series and never across one, since
`Q1` is the governorate in Arab Barometer and "Important in life: Family" in the
World Values Survey.

`scripts/extract_tunisia.py` reads three kinds of release, set per survey as
`source_format`:

| `source_format` | Release | What it costs |
|---|---|---|
| `sav` | SPSS, with variable and value labels | nothing; prefer it wherever the publisher offers one |
| `csv-labels` | CSV of label text | no numeric codes, no question text |
| `xlsx-headers` | Excel with `NAME: question text` headers | no value labels |

A `csv-labels` survey also needs `country_value` set to the country's name as the
CSV spells it, since there is no numeric country code to match on. A release in
none of these shapes needs a reader added to `read_pooled()`, not a workaround in
the data.

A series numbered by year rather than by wave sets `tag` directly — the Arab
Opinion Index rounds are `2011` and `2012-2013`, not `w01` and `w02` — and the tag
becomes the folder name and the crosswalk's column prefix.

If a release is too large for git to hold (GitHub refuses anything over 100 MB),
give the wave a `download_url` and add the file to `.gitignore` by name.
`scripts/fetch_raw.py` will retrieve it and check it against the recorded SHA-256.

If the release has no country column at all — Afrobarometer's country files do not —
find something that still identifies the country and match on that rather than
skipping the check. Afrobarometer prefixes its respondent numbers, so those surveys
set `"country_var": "RESPNO"`, `"country_value": "TUN"` and
`"country_match": "startswith"`.

A country file rather than a pooled release is fine: give it its country variable
and value anyway, so the filter checks that the file holds what it claims to.

## Ground rules

- **Nothing hand-edited.** If a file under `data/` cannot be reproduced by running
  the scripts, it does not belong in the repository.
- **No recoding.** Don't-know codes, weights and scale directions are left exactly
  as the publisher wrote them. Harmonisation is the analyst's job and belongs in
  analysis code, not in the archive.
- **`scripts/verify.py` must pass** before you commit an extract.
- **Check the licence.** Not every survey programme permits redistribution of its
  microdata. Confirm the terms before adding a series, and record them in
  `docs/provenance.md`.
