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
"world-values-survey": {
  "name": "World Values Survey",
  "publisher": "WVS Association",
  "homepage": "https://www.worldvaluessurvey.org",
  "data_page": "https://www.worldvaluessurvey.org/WVSDocumentationWVL.jsp",
  "country_variable_values": {"tunisia": 788}
}
```

`scripts/extract_tunisia.py` reads two kinds of release, set per wave as
`source_format`: `sav` for an SPSS release with variable and value labels attached,
which is the common case and the better one, and `csv-labels` for a CSV of label
text with no codes and no question text. A `csv-labels` wave also needs
`country_value` set to the country's name as the CSV spells it, since there is no
numeric country code to match on. A series that ships neither needs a reader added
to `read_pooled()`, not a workaround in the data.

Prefer the SPSS release wherever the publisher offers one. A `csv-labels` wave is
a fallback: it loses the numeric codes and the question text, and both show up as
gaps in the codebook.

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
