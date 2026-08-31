#!/usr/bin/env python3
"""Extract the Tunisia sub-sample from pooled Arab Barometer releases.

Reads the pooled, multi-country release files placed in ``data/raw/`` and writes
one harmonised folder per wave under ``data/<series>/<wave-slug>/``:

    <stem>.sav           SPSS, full variable + value labels
    <stem>.dta           Stata 14, variable labels truncated to Stata's 80 chars
    <stem>-codes.csv     numeric codes as stored in the release
    <stem>-labels.csv    value labels substituted wherever the release defines them
    codebook.csv         one row per variable
    codebook.json        same, machine readable
    README.md            wave-level provenance note

The SPSS release is the authoritative input: it carries both the variable labels
and the value labels, so every output below is derived from it. That keeps the
three waves consistent with each other even though the upstream CSVs are not
(Wave II ships label text, Waves V and VIII ship numeric codes).

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


def build_codebook(df: pd.DataFrame, meta, value_labels: dict) -> list[dict]:
    rows = []
    for pos, col in enumerate(df.columns, start=1):
        s = df[col]
        row = {
            "position": pos,
            "variable": col,
            "label": meta.column_names_to_labels.get(col) or "",
            "storage_type": str(s.dtype),
            "n_valid": int(s.notna().sum()),
            "n_missing": int(s.isna().sum()),
            "n_distinct": int(s.nunique(dropna=True)),
            "value_labels": json.dumps(value_labels.get(col, {}), ensure_ascii=False)
            if col in value_labels
            else "",
        }
        if pd.api.types.is_numeric_dtype(s) and row["n_valid"]:
            row["min"] = float(s.min())
            row["max"] = float(s.max())
        else:
            row["min"] = ""
            row["max"] = ""
        rows.append(row)
    return rows


def fieldwork_window(df: pd.DataFrame, spec: dict) -> str | None:
    var = spec.get("fieldwork_date_var")
    if spec.get("fieldwork_tunisia") != "derive" or not var or var not in df.columns:
        return None
    dates = pd.to_datetime(df[var], errors="coerce").dropna()
    if dates.empty:
        return None
    return f"{dates.min():%Y-%m-%d} to {dates.max():%Y-%m-%d}"


def process_wave(spec: dict, series: dict, raw_dir: Path, out_dir: Path) -> dict:
    stem_in = spec["raw_file_stem"]
    src = raw_dir / f"{stem_in}.sav"
    if not src.exists():
        raise SystemExit(
            f"missing input {src}\n"
            "Place the pooled Arab Barometer release files in data/raw/ first "
            "(see docs/provenance.md)."
        )

    country_var = spec["country_var"]
    country_code = series["country_variable_values"]["tunisia"]

    print(f"[{spec['slug']}] reading {src.name} ...")
    df, meta = pyreadstat.read_sav(str(src), user_missing=True)
    n_pooled = len(df)
    countries_pooled = sorted(df[country_var].dropna().unique().tolist())

    df = df[df[country_var] == country_code].reset_index(drop=True)
    if df.empty:
        raise SystemExit(f"no rows with {country_var} == {country_code} in {src.name}")
    print(f"[{spec['slug']}] Tunisia: {len(df):,} of {n_pooled:,} rows, {df.shape[1]} variables")

    value_labels = {
        var: clean_value_labels(labels)
        for var, labels in meta.variable_value_labels.items()
        if var in df.columns
    }
    var_labels = {c: (meta.column_names_to_labels.get(c) or "") for c in df.columns}

    dest = out_dir / spec["series"] / spec["slug"]
    dest.mkdir(parents=True, exist_ok=True)
    stem = f"{spec['series']}-w{spec['wave']:02d}-tunisia"

    # SPSS: full fidelity.
    pyreadstat.write_sav(
        df,
        str(dest / f"{stem}.sav"),
        column_labels=[var_labels[c] for c in df.columns],
        variable_value_labels=value_labels,
        file_label=f"{series['name']} {spec['wave_label']} - Tunisia",
    )

    # Stata: same content, variable labels truncated to the format's limit.
    stata_labels = [
        (lbl[: STATA_LABEL_MAX - 3] + "...") if len(lbl) > STATA_LABEL_MAX else lbl
        for lbl in (var_labels[c] for c in df.columns)
    ]
    pyreadstat.write_dta(
        df,
        str(dest / f"{stem}.dta"),
        column_labels=stata_labels,
        variable_value_labels=value_labels,
        version=14,
    )

    # CSV, numeric codes.
    df.to_csv(dest / f"{stem}-codes.csv", index=False)

    # CSV, value labels applied wherever the release defines them.
    labelled = df.copy()
    for var, labels in value_labels.items():
        labelled[var] = labelled[var].map(
            lambda v: labels.get(int(v) if isinstance(v, float) and v.is_integer() else v, v)
        )
    labelled.to_csv(dest / f"{stem}-labels.csv", index=False)

    # Codebook.
    codebook = build_codebook(df, meta, value_labels)
    n_with_data = sum(1 for r in codebook if r["n_valid"] > 0)
    pd.DataFrame(codebook).to_csv(dest / "codebook.csv", index=False)
    (dest / "codebook.json").write_text(
        json.dumps(codebook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    entry = {
        "series": spec["series"],
        "series_name": series["name"],
        "wave": spec["wave"],
        "wave_label": spec["wave_label"],
        "slug": spec["slug"],
        "country": "Tunisia",
        "country_code": country_code,
        "n_respondents": int(len(df)),
        "n_variables": int(df.shape[1]),
        "n_variables_with_data": n_with_data,
        "n_respondents_pooled_release": n_pooled,
        "n_countries_pooled_release": len(countries_pooled),
        "fieldwork_years_series": spec["fieldwork_years_series"],
        "fieldwork_tunisia": fieldwork_window(df, spec),
        "fieldwork_source": spec["fieldwork_source"],
        "language": "English (translated instrument and labels)",
        "source_file": src.name,
        "source_sha256": sha256(src),
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
    fw = e["fieldwork_tunisia"] or f"not recorded in the data file (series fieldwork {e['fieldwork_years_series']})"
    lines = [
        f"# {e['series_name']} {e['wave_label']} — Tunisia",
        "",
        "| | |",
        "|---|---|",
        f"| Respondents | {e['n_respondents']:,} |",
        f"| Variables | {e['n_variables']:,} ({e['n_variables_with_data']:,} with at least one non-missing answer in Tunisia) |",
        f"| Fieldwork (Tunisia) | {fw} |",
        f"| Language | {e['language']} |",
        f"| Pooled release | {e['n_respondents_pooled_release']:,} respondents across {e['n_countries_pooled_release']} countries |",
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
    lines += [
        "",
        f"The pooled release carries items asked in only some countries, so "
        f"{e['n_variables'] - e['n_variables_with_data']:,} of the {e['n_variables']:,} variables are",
        "entirely missing in the Tunisia sub-sample. They are kept so that column positions",
        "line up with the pooled release; `codebook.csv` reports `n_valid` for each.",
        "",
        "`-codes.csv` holds the numeric codes as stored in the release; `-labels.csv`",
        "substitutes the value label wherever the release defines one. The `.sav` carries",
        "full variable and value labels; the `.dta` is identical except that variable",
        "labels longer than 80 characters are truncated, which Stata's format requires.",
        "Consult `codebook.csv` for the untruncated labels.",
        "",
        "Regenerate with `python3 scripts/extract_tunisia.py`.",
    ]
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
