#!/usr/bin/env python3
"""Extract the Tunisia sub-sample from pooled Arab Barometer releases.

Reads the pooled, multi-country release files placed in ``data/raw/`` and writes
one harmonised folder per wave under ``data/<series>/<wave-slug>/``:

    <stem>.sav           SPSS
    <stem>.dta           Stata 14, variable labels truncated to Stata's 80 chars
    <stem>-codes.csv     numeric codes as stored in the release
    <stem>-labels.csv    value labels substituted wherever the release defines them
    codebook.csv         one row per variable
    codebook.json        same, machine readable
    README.md            wave-level provenance note

Two kinds of release are handled, declared per wave in ``catalog/sources.json``
as ``source_format``:

``sav`` (the default)
    An SPSS release, which carries the question text as variable labels and the
    response options as value labels. Every output above is derived from it, so
    the waves stay consistent with each other even though the upstream CSVs do
    not (Wave II ships label text where Waves V and VIII ship numeric codes).

``csv-labels``
    A CSV release holding label text and nothing else, which is all Arab
    Barometer distributes for some waves. There are no numeric codes to write, so
    no ``-codes.csv`` is produced, and there is no question text, so the codebook
    records the values observed for each variable instead of a label. Columns that
    parse as numeric throughout the pooled release are typed numeric; the rest
    stay strings. Supplying the SPSS release for such a wave and re-running
    upgrades it to a full ``sav`` extract with no other change.

``xlsx-headers``
    An Excel release whose header row carries ``NAME: question text`` in one cell,
    which is how the World Values Survey ships its spreadsheet edition. The header
    is split into the variable name and its label. The data is numeric codes, but
    the spreadsheet carries no value labels for them, so no ``-labels.csv`` is
    produced; read the response options from the publisher's codebook.

Usage:  python3 scripts/extract_tunisia.py [--raw data/raw] [--out data]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
STATA_LABEL_MAX = 80  # Stata's hard limit on a variable label
# SPSS and Stata both want a name that starts with a letter and carries only
# letters, digits and underscores. Afrobarometer Round 10 ships LOCATION.LEVEL.1.
VALID_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,31}")
MAX_OBSERVED_VALUES = 50  # beyond this a codebook listing stops being useful

# Strings that pandas.read_csv treats as missing by default, and that several
# other CSV readers treat the same way. A substantive answer spelled like one of
# these -- Wave IV answers "None" to a second-language question -- silently
# becomes missing unless the reader is told otherwise, so each wave is scanned
# for the collision and any hit is reported in the catalog and the wave README.
CSV_NA_STRINGS = frozenset({
    "", "#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN", "-NaN", "-nan",
    "1.#IND", "1.#QNAN", "<NA>", "N/A", "NA", "NULL", "NaN", "None", "n/a",
    "nan", "null",
})


def wave_tag(spec: dict) -> str:
    """Short identifier for a wave, or for one part of a wave fielded in parts.

    Arab Barometer ran Wave VI as three separate rounds with their own samples and
    questionnaires, so each is carried as its own survey: w06p1, w06p2, w06p3.
    A survey may also name its own tag, for a series numbered by year.
    """
    # A series that names its rounds by year rather than by number sets `tag`
    # directly: the Arab Opinion Index is "2012-2013", not "wave 2".
    if spec.get("tag"):
        return spec["tag"]
    tag = f"w{spec['wave']:02d}"
    if spec.get("part"):
        tag += f"p{spec['part']}"
    return tag


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_value_labels(labels: dict) -> dict:
    """Normalise value-label keys to ints where they are whole numbers.

    pyreadstat returns SPSS numeric codes as floats; Stata will only accept
    integer keys, and integers read better in a codebook.
    """
    out = {}
    for k, v in labels.items():
        if isinstance(k, float) and k.is_integer():
            k = int(k)
        out[k] = v
    return out


def settle_object_types(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Give each untyped column the type its own values warrant.

    A Stata release read with ``user_missing=True`` hands back extended missing values
    (``.a``, ``.b``) as their labels, so a column that is numeric for most countries
    arrives as ``object`` for all of them. Subsetting to one country leaves 309 such
    columns in the Life in Transition release holding nothing but integers, which
    pyreadstat then refuses to write because it takes them for text.

    Columns whose surviving values are all numeric become numeric; columns that still
    hold any label text become text, so nothing is coerced away. Returns the count of
    columns retyped, which the catalog records.
    """
    out = df.copy()
    changed = 0
    for col in out.columns:
        if out[col].dtype != object:
            continue
        present = out[col].dropna()
        if present.empty:
            continue
        if any(isinstance(v, str) for v in present.unique()):
            out[col] = out[col].astype("string").astype(object).where(out[col].notna())
            continue
        out[col] = pd.to_numeric(out[col], errors="coerce")
        changed += 1
    return out, changed


def writes_codes(fmt: str) -> bool:
    """Does the release store answers as numeric codes rather than as label text?"""
    return fmt in ("sav", "dta", "xlsx-headers")


def sanitise_names(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """Rename any column SPSS and Stata would reject, and say what was renamed."""
    renamed, taken = {}, {c.upper() for c in df.columns}
    for col in df.columns:
        if VALID_NAME.fullmatch(col):
            continue
        clean = re.sub(r"[^A-Za-z0-9_]", "_", col).lstrip("_")[:32] or "V"
        if not clean[0].isalpha():
            clean = f"V_{clean}"[:32]
        stem, n = clean, 1
        while clean.upper() in taken:
            n += 1
            clean = f"{stem[:30]}_{n}"
        taken.add(clean.upper())
        renamed[col] = clean
    return (df.rename(columns=renamed) if renamed else df), renamed


def select_country(df: pd.DataFrame, spec: dict, country_value) -> pd.DataFrame:
    """Keep the rows for Tunisia.

    Most releases carry a country code to match on. Afrobarometer ships country
    files with no country column at all, but its respondent numbers are prefixed
    with the country -- TUN0001 -- so the prefix serves, and the filter still
    checks that the file holds what it claims rather than trusting the filename.
    """
    column = df[spec["country_var"]]
    if spec.get("country_match") == "startswith":
        return df[column.astype(str).str.startswith(str(country_value))]
    return df[column == country_value]


def drop_extended_missing_labels(
    df: pd.DataFrame, value_labels: dict
) -> tuple[dict, dict[str, list[str]]]:
    """Drop labels keyed on a Stata extended missing rather than on a number.

    Stata lets a variable carry .a to .z alongside its numeric codes, and a release
    can label them -- the EU Neighbourhood Barometer labels .i as "Inap.". Read with
    the user-missing values kept, pyreadstat hands those keys back as the bare letter,
    so the label map for an otherwise numeric variable ends up mixing ints with the
    string 'i'. SPSS will not take that, and the letter is not a value any Tunisian
    row holds anyway: the codes those labels describe survive, only the labels on
    non-numeric keys go. Every drop is recorded in the catalog.
    """
    dropped: dict[str, list[str]] = {}
    for name, labels in list(value_labels.items()):
        if name not in df.columns or not pd.api.types.is_numeric_dtype(df[name]):
            continue
        bad = [k for k in labels if not isinstance(k, (int, float))]
        if bad:
            dropped[name] = [f"{k}: {labels[k]}" for k in bad]
            value_labels[name] = {k: v for k, v in labels.items() if k not in bad}
    return value_labels, dropped


def drop_temporal_value_labels(
    df: pd.DataFrame, value_labels: dict
) -> tuple[dict, list[str]]:
    """Remove value labels attached to a date or time column.

    Neither SPSS nor Stata will take them -- the label's key is a number and the
    column is a time -- and they carry nothing: Afrobarometer uses them only to
    mark -3600 as "Missing" on the interview start and end times, and the reader
    has already turned that into a time of day.
    """
    dropped = []
    for name in list(value_labels):
        if name not in df.columns:
            continue
        present = df[name].dropna()
        if len(present) and isinstance(
            present.iloc[0], (datetime.date, datetime.time, datetime.datetime)
        ):
            del value_labels[name]
            dropped.append(name)
    return value_labels, dropped


def is_blank(s: pd.Series) -> pd.Series:
    """Missing, for either kind of release: NaN, or an empty string."""
    if pd.api.types.is_numeric_dtype(s):
        return s.isna()
    return s.isna() | (s.astype(str).str.strip() == "")


def read_pooled(spec: dict, raw_dir: Path) -> tuple[pd.DataFrame, dict, dict, list[str]]:
    """Return the pooled release plus its variable labels, value labels and
    the columns that should be typed numeric."""
    fmt = spec.get("source_format", "sav")
    stem = spec["raw_file_stem"]

    if fmt == "sav":
        src = raw_dir / f"{stem}.sav"
        require(src)
        df, meta = pyreadstat.read_sav(str(src), user_missing=True)
        var_labels = {c: (meta.column_names_to_labels.get(c) or "") for c in df.columns}
        value_labels = {
            var: clean_value_labels(labels)
            for var, labels in meta.variable_value_labels.items()
            if var in df.columns
        }
        return df, var_labels, value_labels, []

    if fmt == "dta":
        src = raw_dir / f"{stem}.dta"
        require(src)
        df, meta = pyreadstat.read_dta(str(src), user_missing=True)
        var_labels = {c: (meta.column_names_to_labels.get(c) or "") for c in df.columns}
        value_labels = {
            var: clean_value_labels(labels)
            for var, labels in meta.variable_value_labels.items()
            if var in df.columns
        }
        return df, var_labels, value_labels, []

    if fmt == "csv-labels":
        src = raw_dir / f"{stem}.csv"
        require(src)
        # Everything is read as text so that nothing is coerced on the way in;
        # keep_default_na=False keeps an empty cell an empty string rather than
        # letting pandas turn strings like "NA" into missing values.
        df = pd.read_csv(src, dtype=str, keep_default_na=False, low_memory=False)
        # Decide numeric typing on the whole release rather than on the Tunisia
        # subset: which columns are numeric is a property of the instrument, and
        # deciding it per country would give a different schema for each.
        numeric = []
        for col in df.columns:
            values = df[col][df[col] != ""]
            if values.empty:
                continue
            try:
                pd.to_numeric(values)
            except (ValueError, TypeError):
                continue
            numeric.append(col)
        return df, {c: "" for c in df.columns}, {}, numeric

    if fmt == "xlsx-headers":
        src = raw_dir / f"{stem}.xlsx"
        require(src)
        frame = pd.read_excel(src, sheet_name=spec.get("sheet", 0))
        names, labels = [], {}
        for header in frame.columns:
            name, _, label = str(header).partition(":")
            name = name.strip()
            labels[name] = label.strip()
            names.append(name)
        if len(set(names)) != len(names):
            raise SystemExit(f"{src.name}: duplicate variable names after splitting headers")
        frame.columns = names
        # The spreadsheet edition ships codes without the value labels for them.
        return frame, labels, {}, []

    raise SystemExit(f"unknown source_format {fmt!r} for wave {spec['slug']}")


def require(src: Path) -> None:
    if not src.exists():
        raise SystemExit(
            f"missing input {src}\n"
            "Place the pooled Arab Barometer release files in data/raw/ first "
            "(see docs/provenance.md)."
        )


def apply_numeric_types(df: pd.DataFrame, numeric: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in numeric:
        out[col] = pd.to_numeric(out[col].where(out[col] != ""), errors="raise")
    return out


def build_codebook(df: pd.DataFrame, var_labels: dict, value_labels: dict) -> list[dict]:
    rows = []
    for pos, col in enumerate(df.columns, start=1):
        s = df[col]
        blank = is_blank(s)
        present = s[~blank]
        row = {
            "position": pos,
            "variable": col,
            "label": var_labels.get(col, ""),
            "storage_type": str(s.dtype),
            "n_valid": int((~blank).sum()),
            "n_missing": int(blank.sum()),
            "n_distinct": int(present.nunique()),
            "value_labels": json.dumps(value_labels[col], ensure_ascii=False)
            if col in value_labels
            else "",
            # Where the release defines no value labels there is still something
            # useful to record for a categorical variable: what actually appears
            # in it. This is the only description a csv-labels wave has.
            "observed_values": "",
        }
        if col not in value_labels and not pd.api.types.is_numeric_dtype(s):
            distinct = sorted(present.astype(str).unique())
            if 0 < len(distinct) <= MAX_OBSERVED_VALUES:
                row["observed_values"] = json.dumps(distinct, ensure_ascii=False)
        # Negative values in a coded variable are sentinels, not measurements --
        # WVS uses -1 to -5 for the kinds of non-answer, Arab Barometer Wave V uses
        # -8 and -9 -- and a release that ships no value labels gives no other clue
        # that they are there.
        row["sentinel_codes"] = ""
        if pd.api.types.is_numeric_dtype(s) and row["n_valid"]:
            row["min"] = float(present.min())
            row["max"] = float(present.max())
            negatives = sorted({float(v) for v in present.unique() if v < 0})
            if negatives:
                row["sentinel_codes"] = json.dumps(
                    [int(v) if float(v).is_integer() else v for v in negatives]
                )
        else:
            row["min"] = ""
            row["max"] = ""
        rows.append(row)
    return rows


def scan_csv_na_collisions(df: pd.DataFrame) -> dict[str, list[str]]:
    """Find answers that a default CSV reader would silently turn into missing."""
    hits: dict[str, list[str]] = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
        values = {str(v) for v in df[col].dropna().unique()}
        bad = sorted(v for v in values if v.strip() and v.strip() in CSV_NA_STRINGS)
        if bad:
            hits[col] = bad
    return hits


def parse_fieldwork_dates(values: pd.Series, fmt: str | None) -> pd.Series:
    """Interview dates from whatever the release stores them as.

    Shared with the coverage figure. It used to be written out twice, which is how the
    Life in Transition release's Stata dates were handled in one place and not the
    other, and a survey with 75 dated days was drawn as though it recorded only a year.
    """
    if fmt == "spss-seconds":
        # SPSS counts seconds from 1582-10-14, the start of the Gregorian calendar.
        # The Arab Transformations release stores the interview date that way but
        # gives the column an F9.0 format, so it arrives as a bare number rather than
        # a date and nothing downstream would guess. pandas cannot hold 1582 as an
        # origin at nanosecond resolution, so the arithmetic is done in datetime.
        epoch = datetime.date(1582, 10, 14)
        parsed = values.dropna().map(
            lambda v: epoch + datetime.timedelta(seconds=float(v))
        )
        return pd.to_datetime(pd.Series(list(parsed), index=parsed.index), errors="coerce").dropna()
    if fmt == "stata-tc":
        # Stata's %tc is milliseconds since 1960-01-01. pyreadstat hands it back as a
        # raw number here rather than a datetime, and reading it as epoch nanoseconds
        # -- which is what a bare to_datetime does -- lands every interview in 1970.
        return pd.to_datetime(
            values, unit="ms", origin=pd.Timestamp("1960-01-01"), errors="coerce"
        ).dropna()
    if fmt:
        # WVS stores the interview date as the integer 20190515, which only reads as a
        # date if the format is given.
        values = values.astype("Int64").astype(str)
    return pd.to_datetime(values, format=fmt, errors="coerce").dropna()


def interview_dates(df: pd.DataFrame, spec: dict) -> pd.Series:
    """Every interview date a release records, however it stores them.

    Three shapes so far: one column the reader already returns as a date, one column
    holding a number that encodes a date, and -- SAHWA -- three columns holding the
    day, the month and the year apart. Shared with the coverage figure so a release
    cannot be dated one way in the catalogue and another way in the chart.
    """
    parts = spec.get("fieldwork_date_parts")
    if parts:
        # The EU Neighbourhood Barometer records the day and the month of an
        # interview and not the year, because a wave is one year by construction.
        # An integer here is that year, supplied from the wave rather than the file;
        # a string is a column name. The year is only ever safe as a constant when
        # the wave's Tunisian fieldwork sits inside one calendar year, which is
        # checked below rather than assumed.
        def part(key):
            value = parts[key]
            return pd.Series(value, index=df.index) if isinstance(value, int) else df[value]

        frame = pd.DataFrame(
            {"year": part("year"), "month": part("month"), "day": part("day")}
        ).dropna()
        if isinstance(parts["year"], int) and not frame.empty:
            months = sorted(frame["month"].astype(int).unique())
            if 1 in months and 12 in months:
                raise SystemExit(
                    f"fieldwork spans a new year (months {months}) but the year is "
                    f"given as the constant {parts['year']}; record the year per row"
                )
        return pd.to_datetime(frame.astype(int), errors="coerce").dropna()
    var = spec.get("fieldwork_date_var")
    if not var or var not in df.columns:
        return pd.Series(dtype="datetime64[ns]")
    return parse_fieldwork_dates(df[var], spec.get("fieldwork_date_format"))


def date_columns(spec: dict) -> list[str]:
    """The columns interview_dates needs, for a reader that loads only some of them."""
    parts = spec.get("fieldwork_date_parts")
    if parts:
        return [parts[k] for k in ("year", "month", "day") if isinstance(parts[k], str)]
    var = spec.get("fieldwork_date_var")
    return [var] if var else []


def fieldwork_window(df: pd.DataFrame, spec: dict) -> str | None:
    # Some releases record no interview date but do carry the month fieldwork
    # started and ended, as YYYYMM constants.
    pair = spec.get("fieldwork_month_vars")
    if spec.get("fieldwork_tunisia") == "derive" and pair:
        start, end = (df[v].dropna().astype("Int64").astype(str) for v in pair)
        if start.empty or end.empty:
            return None
        first = pd.to_datetime(start.min(), format="%Y%m")
        last = pd.to_datetime(end.max(), format="%Y%m")
        return f"{first:%B %Y} to {last:%B %Y}"

    if spec.get("fieldwork_tunisia") != "derive":
        return None
    if any(c not in df.columns for c in date_columns(spec)):
        return None
    dates = interview_dates(df, spec)
    if dates.empty:
        return None
    return f"{dates.min():%Y-%m-%d} to {dates.max():%Y-%m-%d}"


def process_wave(spec: dict, series: dict, raw_dir: Path, out_dir: Path) -> dict:
    fmt = spec.get("source_format", "sav")
    country_var = spec["country_var"]
    country_value = spec.get("country_value", series["country_variable_values"]["tunisia"])

    print(f"[{spec['slug']}] reading {spec['raw_file_stem']} ({fmt}) ...")
    pooled, var_labels, value_labels, numeric = read_pooled(spec, raw_dir)
    n_pooled = len(pooled)
    # Counting distinct values of the country variable only means something when the
    # variable is a country code. Afrobarometer ships country files with no country
    # column and is matched on the prefix of RESPNO, a per-respondent id, so counting
    # its distinct values gave "1,200 countries" in every Afrobarometer README.
    n_countries = (
        int(pooled[country_var].nunique())
        if spec.get("country_match", "equals") == "equals"
        else None
    )

    df = select_country(pooled, spec, country_value).reset_index(drop=True)
    del pooled
    if df.empty:
        raise SystemExit(
            f"no rows with {country_var} == {country_value!r} in {spec['raw_file_stem']}"
        )
    df = apply_numeric_types(df, numeric)
    retyped = 0
    if fmt == "dta":
        df, retyped = settle_object_types(df)
        if retyped:
            print(f"[{spec['slug']}] typed {retyped} untyped columns from their own values")
    df, renamed = sanitise_names(df)
    for before, after in renamed.items():
        var_labels[after] = var_labels.pop(before, "")
        if before in value_labels:
            value_labels[after] = value_labels.pop(before)
        print(f"[{spec['slug']}] renamed {before} -> {after} (not a valid SPSS/Stata name)")
    value_labels, temporal_labels_dropped = drop_temporal_value_labels(df, value_labels)
    value_labels, extended_missing_labels_dropped = drop_extended_missing_labels(df, value_labels)
    for name in temporal_labels_dropped:
        print(f"[{spec['slug']}] dropped value labels on {name}: it is a date or time column")
    print(f"[{spec['slug']}] Tunisia: {len(df):,} of {n_pooled:,} rows, {df.shape[1]} variables")

    dest = out_dir / spec["series"] / spec["slug"]
    dest.mkdir(parents=True, exist_ok=True)
    stem = f"{spec['series']}-{wave_tag(spec)}-tunisia"

    # SPSS.
    pyreadstat.write_sav(
        df,
        str(dest / f"{stem}.sav"),
        column_labels=[var_labels.get(c, "") for c in df.columns],
        variable_value_labels=value_labels,
        file_label=f"{series['name']} {spec['wave_label']} - Tunisia",
    )

    # Stata: same content, variable labels truncated to the format's limit.
    stata_labels = [
        (lbl[: STATA_LABEL_MAX - 3] + "...") if len(lbl) > STATA_LABEL_MAX else lbl
        for lbl in (var_labels.get(c, "") for c in df.columns)
    ]
    pyreadstat.write_dta(
        df,
        str(dest / f"{stem}.dta"),
        column_labels=stata_labels,
        variable_value_labels=value_labels,
        version=14,
    )

    if writes_codes(fmt):
        df.to_csv(dest / f"{stem}-codes.csv", index=False)
    else:
        # The release is label text already; there are no codes to write.
        (dest / f"{stem}-codes.csv").unlink(missing_ok=True)

    if value_labels or not writes_codes(fmt):
        labelled = df.copy()
        for var, labels in value_labels.items():
            labelled[var] = labelled[var].map(
                lambda v: labels.get(int(v) if isinstance(v, float) and v.is_integer() else v, v)
            )
        labelled.to_csv(dest / f"{stem}-labels.csv", index=False)
    else:
        # Codes with no value labels to substitute: a labelled CSV would just be a
        # second copy of the codes.
        (dest / f"{stem}-labels.csv").unlink(missing_ok=True)
        labelled = df

    na_collisions = scan_csv_na_collisions(labelled)
    for var, values in na_collisions.items():
        print(f"[{spec['slug']}] warning: {var} answers {values} read as missing by default")

    codebook = build_codebook(df, var_labels, value_labels)
    n_with_data = sum(1 for r in codebook if r["n_valid"] > 0)
    pd.DataFrame(codebook).to_csv(dest / "codebook.csv", index=False)
    (dest / "codebook.json").write_text(
        json.dumps(codebook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    suffix = {"sav": "sav", "dta": "dta", "csv-labels": "csv", "xlsx-headers": "xlsx"}[fmt]
    src = raw_dir / f"{spec['raw_file_stem']}.{suffix}"
    entry = {
        "series": spec["series"],
        "series_name": series["name"],
        "series_prefix": series["prefix"],
        "key": f"{series['prefix']}-{wave_tag(spec)}",
        "wave": spec["wave"],
        "part": spec.get("part"),
        "wave_label": spec["wave_label"],
        "tag": wave_tag(spec),
        "slug": spec["slug"],
        "country": "Tunisia",
        "country_value": country_value,
        "country_match": spec.get("country_match", "equals"),
        "renamed_variables": renamed,
        "columns_retyped_from_values": retyped,
        "value_labels_dropped_on_temporal_columns": temporal_labels_dropped,
        "value_labels_dropped_on_extended_missings": extended_missing_labels_dropped,
        "n_respondents": int(len(df)),
        "n_variables": int(df.shape[1]),
        "n_variables_with_data": n_with_data,
        "n_respondents_pooled_release": n_pooled,
        "n_countries_pooled_release": n_countries,
        # Every row in the release is Tunisia: either the country column says so, or
        # the release is a country file whose rows all carry the country's prefix.
        "is_country_file": n_pooled == len(df),
        "fieldwork_years_series": spec["fieldwork_years_series"],
        "fieldwork_tunisia": fieldwork_window(df, spec),
        "fieldwork_source": spec["fieldwork_source"],
        "language": spec.get("language", "English (translated instrument and labels)"),
        "source_format": fmt,
        "has_numeric_codes": writes_codes(fmt),
        "has_value_labels": bool(value_labels),
        "has_question_text": bool([v for v in var_labels.values() if v.strip()]),
        "source_file": src.name,
        "source_sha256": sha256(src),
        "csv_answers_read_as_missing": na_collisions,
        "path": str(dest.relative_to(ROOT)),
        "files": {},
        "notes": spec.get("notes", ""),
    }
    for f in sorted(dest.iterdir()):
        if f.name == "README.md":
            continue
        entry["files"][f.name] = {"bytes": f.stat().st_size, "sha256": sha256(f)}

    (dest / "README.md").write_text(render_wave_readme(entry, series), encoding="utf-8")
    return entry


def render_wave_readme(e: dict, series: dict) -> str:
    fw = e["fieldwork_tunisia"] or (
        f"not recorded in the data file (series fieldwork {e['fieldwork_years_series']})"
    )
    lines = [
        f"# {e['series_name']} {e['wave_label']} — Tunisia",
        "",
        "| | |",
        "|---|---|",
        f"| Respondents | {e['n_respondents']:,} |",
        (
            f"| Variables | {e['n_variables']:,} |"
            if e["n_variables"] == e["n_variables_with_data"]
            else f"| Variables | {e['n_variables']:,} "
            f"({e['n_variables_with_data']:,} with at least one non-missing answer in Tunisia) |"
        ),
        f"| Fieldwork (Tunisia) | {fw} |",
        f"| Language | {e['language']} |",
        (
            f"| Source release | Tunisia country file, {e['n_respondents_pooled_release']:,} respondents |"
            if e["is_country_file"]
            else f"| Pooled release | {e['n_respondents_pooled_release']:,} respondents "
            f"across {e['n_countries_pooled_release']} countries |"
        ),
        f"| Source file | `{e['source_file']}` |",
        f"| Publisher | {series['publisher']} |",
        "",
        "## Files",
        "",
        "| File | Size | SHA-256 (first 16) |",
        "|---|---:|---|",
    ]
    for name, info in e["files"].items():
        lines.append(f"| `{name}` | {info['bytes'] / 1_048_576:.2f} MB | `{info['sha256'][:16]}` |")

    empty = e["n_variables"] - e["n_variables_with_data"]
    if empty:
        lines += [
            "",
            "The pooled release carries items asked in only some countries, so "
            f"{empty:,} of the {e['n_variables']:,} variables are entirely missing in the",
            "Tunisia sub-sample. They are kept so that column positions line up with the",
            "pooled release; `codebook.csv` reports `n_valid` for each.",
            "",
        ]
    else:
        lines += [
            "",
            "Every variable carries data for at least one respondent.",
            "",
        ]

    if e["source_format"] in ("sav", "dta"):
        lines += [
            "`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`",
            "substitutes the value label wherever the release defines one. The `.sav` carries",
            "full variable and value labels; the `.dta` is identical except that variable",
            "labels longer than 80 characters are truncated, which Stata's format requires.",
            "Consult `codebook.csv` for the untruncated labels.",
        ]
    elif e["source_format"] == "xlsx-headers":
        lines += [
            "## Derived from the spreadsheet edition",
            "",
            "The publisher ships this as an Excel file whose header row carries",
            "`NAME: question text` in a single cell. The header is split into the variable",
            "name and its label, so the question text survives into every format here.",
            "",
            "What does not survive is the response options: the spreadsheet carries the",
            "numeric codes and no value labels for them. There is therefore no",
            "`-labels.csv` — it would be a second copy of `-codes.csv` — and the `.sav` and",
            "`.dta` hold bare codes. Read the response options from the publisher's codebook.",
            "",
            "Negative codes are non-response sentinels rather than measurements.",
            "`codebook.csv` lists the ones each variable actually uses in `sentinel_codes`,",
            "and `docs/missing-value-codes.md` collects them per survey. What each one means",
            "is in the publisher's codebook; this archive does not guess.",
            "",
            "Supplying the SPSS release for this survey and switching `source_format` to",
            "`sav` would add the value labels with no other change.",
        ]
    else:
        lines += [
            "## Derived from a label-only CSV release",
            "",
            "Arab Barometer distributes this wave as a CSV of label text, with no SPSS or",
            "Stata release alongside it. Two things follow, and they are limitations of the",
            "source rather than of this extract:",
            "",
            "- **No numeric codes.** Answers exist only as text, so there is no `-codes.csv`,",
            "  and the `.sav` and `.dta` hold strings rather than coded categoricals. In Stata,",
            "  `encode` them; in R, `haven::as_factor()` has nothing to do because the labels",
            "  are already the values.",
            "- **No question text.** The CSV carries variable names but no variable labels, so",
            "  the `label` column of `codebook.csv` is empty. In its place the codebook records",
            "  `observed_values`, the distinct answers each variable actually takes. For the",
            "  question wording, use the questionnaire on the Arab Barometer site.",
            "",
            "Columns that parse as numeric across the whole pooled release are typed numeric;",
            "the rest are left as text. `codebook.csv` reports the storage type of each.",
            "",
            "Dropping the SPSS release for this wave into `data/raw/`, setting",
            "`source_format` to `sav` in `catalog/sources.json` and re-running the scripts",
            "upgrades this folder to a full extract with codes and question text.",
        ]

    if e["csv_answers_read_as_missing"]:
        listed = ", ".join(
            f"`{var}` ({', '.join(repr(v) for v in values)})"
            for var, values in e["csv_answers_read_as_missing"].items()
        )
        lines += [
            "",
            "## Reading the CSV",
            "",
            f"{listed} — these are substantive answers spelled the way most CSV readers",
            "spell a missing value. `pandas.read_csv` and friends will turn them into",
            "missing unless you say otherwise:",
            "",
            "```python",
            "pd.read_csv(path, keep_default_na=False)   # then treat \"\" as missing",
            "```",
            "",
            "The `.sav` and `.dta` are unaffected.",
        ]

    lines += ["", "Regenerate with `python3 scripts/extract_tunisia.py`."]
    if e["value_labels_dropped_on_temporal_columns"]:
        listed = ", ".join(f"`{v}`" for v in e["value_labels_dropped_on_temporal_columns"])
        lines += [
            "",
            f"Value labels on {listed} are not carried over. They are date or time columns,",
            "which neither SPSS nor Stata will attach value labels to, and the labels only",
            "marked a sentinel the reader has already parsed as a time of day.",
        ]

    if e.get("value_labels_dropped_on_extended_missings"):
        dropped = e["value_labels_dropped_on_extended_missings"]
        listed = ", ".join(f"`{v}`" for v in sorted(dropped))
        example = sorted(dropped)[0]
        lines += [
            "",
            f"{len(dropped)} variables carry a value label keyed on a Stata extended missing",
            f"(`.a` to `.z`) rather than on a number — {listed if len(dropped) <= 6 else example + ' among them'}.",
            "SPSS will not attach a label to a non-numeric key, so those labels are dropped;",
            f"in {example} the dropped label was {dropped[example][0]!r}. No code and no answer",
            "is lost, only the label on a missing marker no Tunisian row carries.",
        ]

    if e["renamed_variables"]:
        lines += [
            "",
            "## Renamed variables",
            "",
            "The release uses names SPSS and Stata will not accept, so they are rewritten",
            "here. Nothing else about them changes.",
            "",
            "| In the release | Here |",
            "|---|---|",
        ]
        for before, after in e["renamed_variables"].items():
            lines.append(f"| `{before}` | `{after}` |")

    if e["notes"]:
        lines += ["", f"Note: {e['notes']}"]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=ROOT / "data" / "raw", type=Path)
    ap.add_argument("--out", default=ROOT / "data", type=Path)
    ap.add_argument("--manifest", default=ROOT / "catalog" / "sources.json", type=Path)
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    entries = [
        process_wave(spec, manifest["series"][spec["series"]], args.raw, args.out)
        for spec in manifest["waves"]
    ]

    catalog = {
        "generated": date.today().isoformat(),
        "country": "Tunisia",
        "surveys": entries,
    }
    (ROOT / "catalog" / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    pd.DataFrame(
        [{k: v for k, v in e.items() if k != "files"} for e in entries]
    ).to_csv(ROOT / "catalog" / "catalog.csv", index=False)
    print(f"\nwrote catalog/catalog.json and catalog/catalog.csv ({len(entries)} surveys)")


if __name__ == "__main__":
    main()
