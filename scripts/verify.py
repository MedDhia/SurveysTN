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

from extract_tunisia import ROOT, apply_numeric_types, is_blank, read_pooled, sha256

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


def check_offline(catalog: dict) -> list[str]:
    """Check the committed files against the catalog, without the pooled releases."""
    errors: list[str] = []
    for s in catalog["surveys"]:
        tag = f"{s['series']} w{s['wave']:02d}"
        folder = ROOT / s["path"]
        for name, info in s["files"].items():
            f = folder / name
            if not f.exists():
                errors.append(f"{tag}: missing {name}")
            elif f.stat().st_size != info["bytes"]:
                errors.append(f"{tag}: {name} is not the recorded size")
            elif sha256(f) != info["sha256"]:
                errors.append(f"{tag}: {name} does not match the recorded SHA-256")

        sav = folder / f"{s['series']}-w{s['wave']:02d}-tunisia.sav"
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
    tag = f"{s['series']} w{s['wave']:02d}"
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

    stem = folder / f"{s['series']}-w{s['wave']:02d}-tunisia"
    got_sav, _ = pyreadstat.read_sav(f"{stem}.sav", user_missing=True)
    same_frame(expect, got_sav, f"{tag} .sav", errors)

    got_dta, _ = pyreadstat.read_dta(f"{stem}.dta")
    same_frame(expect, got_dta, f"{tag} .dta", errors)

    if s["source_format"] == "sav":
        got_csv = pd.read_csv(f"{stem}-codes.csv", low_memory=False)
        same_frame(expect, got_csv, f"{tag} -codes.csv", errors)
        check_labels_csv(expect, Path(f"{stem}-labels.csv"), value_labels, tag, errors)
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
    specs = {(s["series"], s["wave"]): s for s in manifest["waves"]}

    if args.offline:
        errors = check_offline(catalog)
        label = "all committed files match the catalog"
    else:
        errors = []
        for s in catalog["surveys"]:
            spec = specs[(s["series"], s["wave"])]
            check_against_release(s, spec, manifest["series"][s["series"]], errors)
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
