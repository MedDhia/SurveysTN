#!/usr/bin/env python3
"""Check every extracted file against the pooled release it came from.

For each wave this re-reads the pooled release in ``data/raw/``, re-derives the
Tunisia subset, and compares it cell by cell with the ``.sav``, ``.dta`` and
``-codes.csv`` in the repository, then checks that ``-labels.csv`` resolves to
the same codes. Exits non-zero on the first mismatch.

Requires the pooled releases in ``data/raw/`` (see docs/provenance.md); the
checksums recorded in ``catalog/catalog.json`` are verified first.

``--offline`` skips the pooled releases and checks only what is committed: that
every file named in the catalog is present and matches its recorded SHA-256, and
that each codebook still describes its own data file. That is the check to run
when you have a clone but not the 300 MB of source releases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
TOL = 1e-9


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
            # cell that is empty either way counts as a match. SPSS stores both;
            # only the .sav and .dta round-trips preserve the distinction.
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
            elif sha256(f) != info["sha256"]:
                errors.append(f"{tag}: {name} does not match the recorded SHA-256")
            elif f.stat().st_size != info["bytes"]:
                errors.append(f"{tag}: {name} is not the recorded size")

        stem = folder / f"{s['series']}-w{s['wave']:02d}-tunisia"
        sav = stem.with_suffix(".sav")
        if not sav.exists():
            continue
        df, meta = pyreadstat.read_sav(str(sav), user_missing=True)
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
                if int(df[row["variable"]].notna().sum()) != row["n_valid"]:
                    errors.append(f"{tag}: codebook n_valid wrong for {row['variable']}")
                    break
        print(f"{tag}: checked {len(df):,} rows x {df.shape[1]} variables against the catalog")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--offline",
        action="store_true",
        help="check only the committed files, not the pooled releases in data/raw/",
    )
    args = ap.parse_args()

    catalog = json.loads((ROOT / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    if args.offline:
        errors = check_offline(catalog)
        if errors:
            print("\nFAILED:")
            for e in errors:
                print(f"  - {e}")
            return 1
        print("\nall committed files match the catalog")
        return 0

    manifest = json.loads((ROOT / "catalog" / "sources.json").read_text(encoding="utf-8"))
    specs = {(s["series"], s["wave"]): s for s in manifest["waves"]}
    errors: list[str] = []

    for s in catalog["surveys"]:
        spec = specs[(s["series"], s["wave"])]
        tag = f"{s['series']} w{s['wave']:02d}"
        raw = ROOT / "data" / "raw" / s["source_file"]
        if not raw.exists():
            errors.append(f"{tag}: pooled release {s['source_file']} not in data/raw/")
            continue
        if sha256(raw) != s["source_sha256"]:
            errors.append(f"{tag}: {s['source_file']} does not match the recorded SHA-256")
            continue

        pooled, meta = pyreadstat.read_sav(str(raw), user_missing=True)
        expect = pooled[pooled[spec["country_var"]] == s["country_code"]].reset_index(drop=True)
        del pooled

        stem = ROOT / s["path"] / f"{s['series']}-w{s['wave']:02d}-tunisia"
        for name, info in s["files"].items():
            f = ROOT / s["path"] / name
            if not f.exists():
                errors.append(f"{tag}: missing {name}")
            elif sha256(f) != info["sha256"]:
                errors.append(f"{tag}: {name} does not match the recorded SHA-256")

        got_sav, _ = pyreadstat.read_sav(str(stem.with_suffix(".sav")), user_missing=True)
        same_frame(expect, got_sav, f"{tag} .sav", errors)

        got_dta, _ = pyreadstat.read_dta(str(stem.with_suffix(".dta")))
        same_frame(expect, got_dta, f"{tag} .dta", errors)

        got_csv = pd.read_csv(f"{stem}-codes.csv", low_memory=False)
        same_frame(expect, got_csv, f"{tag} -codes.csv", errors)

        labelled = pd.read_csv(f"{stem}-labels.csv", low_memory=False, dtype=str)
        if len(labelled) != len(expect):
            errors.append(f"{tag} -labels.csv: {len(labelled)} rows vs {len(expect)}")
        else:
            for var, labels in meta.variable_value_labels.items():
                if var not in expect.columns:
                    continue
                # A label can be attached to more than one code -- Wave V's party
                # variables label both 0 and 150000 "no party" -- so the reverse
                # map holds every code that carries the text, not just the last.
                back: dict[str, set[float]] = {}
                for code, label in labels.items():
                    back.setdefault(str(label), set()).add(float(code))
                for i, raw_val in expect[var].items():
                    seen = labelled.at[i, var]
                    if pd.isna(raw_val) or pd.isna(seen):
                        continue
                    if str(raw_val) in {seen, f"{seen}.0"}:
                        continue
                    if not any(abs(c - raw_val) <= TOL for c in back.get(seen, ())):
                        errors.append(f"{tag} -labels.csv: {var} row {i} is {seen!r}")
                        break
        print(f"{tag}: checked {len(expect):,} rows x {expect.shape[1]} variables")

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nall extracts match their pooled releases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
