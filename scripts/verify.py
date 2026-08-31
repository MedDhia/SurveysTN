#!/usr/bin/env python3
"""Check every extracted file against the pooled release it came from.

For each wave this re-reads the pooled release in ``data/raw/``, re-derives the
Tunisia subset, and compares it cell by cell with the files in the repository.
Exits non-zero on the first mismatch per file.

Requires the pooled releases in ``data/raw/`` (see docs/provenance.md); the
checksum recorded in ``catalog/catalog.json`` for each release is verified first.

``--offline`` skips the pooled releases and checks only what is committed: that
every file named in the catalog is present and matches its recorded SHA-256, and
that each codebook still describes its own data file. That is the check to run
when you have a clone but not the source releases.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

from extract_tunisia import ROOT, apply_numeric_types, is_blank, read_pooled, sha256, wave_tag

TOL = 1e-9


def same_frame(a: pd.DataFrame, b: pd.DataFrame, what: str, errors: list[str]) -> None:
    if list(a.columns) != list(b.columns):
        errors.append(f"{what}: column names differ")
        return
    if len(a) != len(b):
        errors.append(f"{what}: {len(a)} rows vs {len(b)}")
        return
    for col in a.columns:
        x, y = a[col], b[col]
        numeric = pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y)
        if not numeric:
            # CSV cannot tell an empty string from a missing value, so a string
            # cell that is empty either way counts as a match. SPSS and Stata
            # preserve the distinction; CSV does not.
            x = x.fillna("").astype(str).str.strip()
            y = y.fillna("").astype(str).str.strip()
            if not x.equals(y):
                errors.append(f"{what}: values differ in {col}")
                return
            continue
        if x.isna().to_numpy().tolist() != y.isna().to_numpy().tolist():
            errors.append(f"{what}: missingness differs in {col}")
            return
        x, y = x.dropna(), y.dropna()
        if not ((x.to_numpy() - y.to_numpy()).__abs__() <= TOL).all():
            errors.append(f"{what}: values differ in {col}")
            return


def check_labels_csv(
    expect: pd.DataFrame, path: Path, value_labels: dict, tag: str, errors: list[str]
) -> None:
    """Check that every labelled cell resolves back to the code it stands for."""
    # keep_default_na=False so an answer spelled "None" or "NA" is compared as
    # the answer it is rather than as a missing value.
    labelled = pd.read_csv(path, low_memory=False, dtype=str, keep_default_na=False)
    if len(labelled) != len(expect):
        errors.append(f"{tag} -labels.csv: {len(labelled)} rows vs {len(expect)}")
        return
    for var, labels in value_labels.items():
        if var not in expect.columns:
            continue
        # A label can be attached to more than one code -- Wave V's party
        # variables label both 0 and 150000 "no party" -- so the reverse map
        # holds every code carrying the text, not just the last one seen.
        back: dict[str, set[float]] = {}
        for code, label in labels.items():
            back.setdefault(str(label), set()).add(float(code))
        for i, raw_val in expect[var].items():
            seen = labelled.at[i, var]
            if pd.isna(raw_val) or seen == "":
                continue
            if str(raw_val) in {seen, f"{seen}.0"}:
                continue
            if not any(abs(c - raw_val) <= TOL for c in back.get(seen, ())):
                errors.append(f"{tag} -labels.csv: {var} row {i} is {seen!r}")
                return


def check_wave06_merge(errors: list[str]) -> None:
    """Check the stacked Wave VI file against the three rounds it was built from.

    This reads the committed files rather than re-running the merge, so it would
    catch a merge that no longer matches its inputs as well as one that was never
    rebuilt.
    """
    report_path = ROOT / "catalog" / "wave-06-merge-report.json"
    if not report_path.exists():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    folder = ROOT / report["path"]
    tag = "wave-06 merge"

    for name, info in report["files"].items():
        f = folder / name
        if not f.exists():
            errors.append(f"{tag}: missing {name}")
        elif sha256(f) != info["sha256"]:
            errors.append(f"{tag}: {name} does not match the recorded SHA-256")

    merged, _ = pyreadstat.read_sav(str(folder / f"{report['stem']}.sav"), user_missing=True)
    split = set(report["split_variables"])

    for n in (1, 2, 3):
        part, _ = pyreadstat.read_sav(
            str(ROOT / f"data/arab-barometer/wave-06-part-{n}/arab-barometer-w06p{n}-tunisia.sav"),
            user_missing=True,
        )
        rows = merged[merged["PART"] == n].reset_index(drop=True)
        if len(rows) != len(part):
            errors.append(f"{tag}: part {n} contributes {len(rows)} rows, the round has {len(part)}")
            continue
        for col in part.columns:
            target = f"{col}__P{n}" if col in split else col
            if target not in rows.columns:
                errors.append(f"{tag}: part {n} column {col} is missing from the merge")
                continue
            a, b = part[col], rows[target]
            if col == "DATE":  # normalised to text on the way in
                a = a.map(lambda v: "" if pd.isna(v) else str(v)[:10])
            if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
                if a.isna().to_numpy().tolist() != b.isna().to_numpy().tolist():
                    errors.append(f"{tag}: part {n} {col} missingness changed")
                    break
                if not ((a.dropna().to_numpy() - b.dropna().to_numpy()).__abs__() <= TOL).all():
                    errors.append(f"{tag}: part {n} {col} values changed")
                    break
            elif not a.fillna("").astype(str).str.strip().equals(
                b.fillna("").astype(str).str.strip()
            ):
                errors.append(f"{tag}: part {n} {col} values changed")
                break

        # A column another round asked but this one did not must be empty here.
        for col in rows.columns:
            base = col.split("__P")[0]
            if col in ("PART", "MERGE_ID") or base in part.columns or "__P" in col:
                continue
            if not is_blank(rows[col]).all():
                errors.append(f"{tag}: {col} has values for part {n}, which never asked it")
                break

    if merged["MERGE_ID"].duplicated().any():
        errors.append(f"{tag}: MERGE_ID is not unique")
    print(f"{tag}: checked {len(merged):,} rows x {merged.shape[1]} variables against the three rounds")


def check_offline(catalog: dict) -> list[str]:
    """Check the committed files against the catalog, without the pooled releases."""
    errors: list[str] = []
    for s in catalog["surveys"]:
        tag = f"{s['series']} {s['tag']}"
        folder = ROOT / s["path"]
        for name, info in s["files"].items():
            f = folder / name
            if not f.exists():
                errors.append(f"{tag}: missing {name}")
            elif f.stat().st_size != info["bytes"]:
                errors.append(f"{tag}: {name} is not the recorded size")
            elif sha256(f) != info["sha256"]:
                errors.append(f"{tag}: {name} does not match the recorded SHA-256")

        sav = folder / f"{s['series']}-{s['tag']}-tunisia.sav"
        if not sav.exists():
            continue
        df, _ = pyreadstat.read_sav(str(sav), user_missing=True)
        if len(df) != s["n_respondents"] or df.shape[1] != s["n_variables"]:
            errors.append(
                f"{tag}: .sav is {len(df)}x{df.shape[1]}, catalog says "
                f"{s['n_respondents']}x{s['n_variables']}"
            )
        codebook = json.loads((folder / "codebook.json").read_text(encoding="utf-8"))
        if [r["variable"] for r in codebook] != list(df.columns):
            errors.append(f"{tag}: codebook variables do not match the .sav")
        else:
            for row in codebook:
                if int((~is_blank(df[row["variable"]])).sum()) != row["n_valid"]:
                    errors.append(f"{tag}: codebook n_valid wrong for {row['variable']}")
                    break
        print(f"{tag}: checked {len(df):,} rows x {df.shape[1]} variables against the catalog")
    return errors


def check_against_release(s: dict, spec: dict, series: dict, errors: list[str]) -> None:
    tag = f"{s['series']} {s['tag']}"
    raw_dir = ROOT / "data" / "raw"
    src = raw_dir / s["source_file"]
    if not src.exists():
        errors.append(f"{tag}: pooled release {s['source_file']} not in data/raw/")
        return
    if sha256(src) != s["source_sha256"]:
        errors.append(f"{tag}: {s['source_file']} does not match the recorded SHA-256")
        return

    pooled, _, value_labels, numeric = read_pooled(spec, raw_dir)
    country_value = spec.get("country_value", series["country_variable_values"]["tunisia"])
    expect = pooled[pooled[spec["country_var"]] == country_value].reset_index(drop=True)
    del pooled
    expect = apply_numeric_types(expect, numeric)

    folder = ROOT / s["path"]
    for name, info in s["files"].items():
        f = folder / name
        if not f.exists():
            errors.append(f"{tag}: missing {name}")
        elif sha256(f) != info["sha256"]:
            errors.append(f"{tag}: {name} does not match the recorded SHA-256")

    stem = folder / f"{s['series']}-{s['tag']}-tunisia"
    got_sav, _ = pyreadstat.read_sav(f"{stem}.sav", user_missing=True)
    same_frame(expect, got_sav, f"{tag} .sav", errors)

    got_dta, _ = pyreadstat.read_dta(f"{stem}.dta")
    same_frame(expect, got_dta, f"{tag} .dta", errors)

    if s["has_numeric_codes"]:
        got_csv = pd.read_csv(f"{stem}-codes.csv", low_memory=False)
        same_frame(expect, got_csv, f"{tag} -codes.csv", errors)
        if s["has_value_labels"]:
            check_labels_csv(expect, Path(f"{stem}-labels.csv"), value_labels, tag, errors)
        elif Path(f"{stem}-labels.csv").exists():
            errors.append(f"{tag}: -labels.csv exists but the release defines no value labels")
    else:
        # A label-only release has no codes, so -labels.csv is the data itself
        # and is compared directly rather than resolved back through the labels.
        got_csv = pd.read_csv(
            f"{stem}-labels.csv", low_memory=False, dtype=str, keep_default_na=False
        )
        for col in numeric:
            got_csv[col] = pd.to_numeric(got_csv[col], errors="coerce")
        same_frame(expect, got_csv, f"{tag} -labels.csv", errors)

    print(f"{tag}: checked {len(expect):,} rows x {expect.shape[1]} variables")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--offline",
        action="store_true",
        help="check only the committed files, not the pooled releases in data/raw/",
    )
    args = ap.parse_args()

    catalog = json.loads((ROOT / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "catalog" / "sources.json").read_text(encoding="utf-8"))
    specs = {(s["series"], wave_tag(s)): s for s in manifest["waves"]}

    if args.offline:
        errors = check_offline(catalog)
        check_wave06_merge(errors)
        label = "all committed files match the catalog"
    else:
        errors = []
        for s in catalog["surveys"]:
            spec = specs[(s["series"], s["tag"])]
            check_against_release(s, spec, manifest["series"][s["series"]], errors)
        check_wave06_merge(errors)
        label = "all extracts match their pooled releases"

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\n{label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
