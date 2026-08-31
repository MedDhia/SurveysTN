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
import hashlib
import json
from datetime import date
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
STATA_LABEL_MAX = 80  # Stata's hard limit on a variable label
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
    """
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


def writes_codes(fmt: str) -> bool:
    """Does the release store answers as numeric codes rather than as label text?"""
    return fmt in ("sav", "xlsx-headers")


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


def fieldwork_window(df: pd.DataFrame, spec: dict) -> str | None:
    var = spec.get("fieldwork_date_var")
    if spec.get("fieldwork_tunisia") != "derive" or not var or var not in df.columns:
        return None
    # WVS stores the interview date as the integer 20190515, which only reads as a
    # date if the format is given.
    fmt = spec.get("fieldwork_date_format")
    values = df[var].astype("Int64").astype(str) if fmt else df[var]
    dates = pd.to_datetime(values, format=fmt, errors="coerce").dropna()
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
    n_countries = int(pooled[country_var].nunique())

    df = pooled[pooled[country_var] == country_value].reset_index(drop=True)
    del pooled
    if df.empty:
        raise SystemExit(
            f"no rows with {country_var} == {country_value!r} in {spec['raw_file_stem']}"
        )
    df = apply_numeric_types(df, numeric)
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

    suffix = {"sav": "sav", "csv-labels": "csv", "xlsx-headers": "xlsx"}[fmt]
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
        "n_respondents": int(len(df)),
        "n_variables": int(df.shape[1]),
        "n_variables_with_data": n_with_data,
        "n_respondents_pooled_release": n_pooled,
        "n_countries_pooled_release": n_countries,
        "is_country_file": n_countries == 1 and n_pooled == len(df),
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

    if e["source_format"] == "sav":
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
