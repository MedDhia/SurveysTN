#!/usr/bin/env python3
"""Download any release file that is missing from ``data/raw/``.

Almost every release is committed, so this is usually a no-op. Two are not: GitHub
refuses a file over 100 MB, and the Arab Opinion Index rounds for 2019/2020 and
2024/2025 are 132 MB and 202 MB. Those are fetched from the publisher instead,
which costs nothing to do -- the Arab Opinion Index publishes at a direct URL with
no registration -- and the alternative was either Git LFS for the whole archive or
an inconsistent rule about which sources it carries.

Each download is checked against the SHA-256 recorded in ``catalog/catalog.json``,
so a file that arrives truncated or changed upstream is rejected rather than
silently extracted from. Their server is slow and does not support resuming, so a
failed transfer restarts.

Usage:  python3 scripts/fetch_raw.py [--force]
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

from extract_tunisia import ROOT, sha256

CHUNK = 1 << 20
ATTEMPTS = 4


def expected_checksums() -> dict[str, str]:
    catalog = json.loads((ROOT / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    return {s["source_file"]: s["source_sha256"] for s in catalog["surveys"]}


def download(url: str, dest: Path) -> None:
    part = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as response, part.open("wb") as out:
        total = int(response.headers.get("Content-Length") or 0)
        got = 0
        while chunk := response.read(CHUNK):
            out.write(chunk)
            got += len(chunk)
            if total:
                print(f"\r  {got / 1e6:.0f} of {total / 1e6:.0f} MB", end="", flush=True)
    print()
    if total and got != total:
        part.unlink(missing_ok=True)
        raise OSError(f"got {got} bytes, expected {total}")
    part.replace(dest)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="re-download even if present")
    args = ap.parse_args()

    manifest = json.loads((ROOT / "catalog" / "sources.json").read_text(encoding="utf-8"))
    checksums = expected_checksums()
    raw = ROOT / "data" / "raw"
    missing, fetched = 0, 0

    for spec in manifest["waves"]:
        url = spec.get("download_url")
        if not url:
            continue
        suffix = {"sav": "sav", "csv-labels": "csv", "xlsx-headers": "xlsx"}[
            spec.get("source_format", "sav")
        ]
        dest = raw / f"{spec['raw_file_stem']}.{suffix}"
        if dest.exists() and not args.force:
            continue

        missing += 1
        print(f"{dest.name}: fetching from {url}")
        for attempt in range(1, ATTEMPTS + 1):
            try:
                download(url, dest)
                break
            except Exception as exc:  # noqa: BLE001 - report and retry whatever it is
                print(f"  attempt {attempt} failed: {exc}")
                if attempt == ATTEMPTS:
                    raise SystemExit(f"could not download {dest.name}")

        want = checksums.get(dest.name)
        if want and sha256(dest) != want:
            dest.unlink()
            raise SystemExit(
                f"{dest.name} does not match the SHA-256 in catalog/catalog.json; "
                "the upstream file has changed or the transfer was corrupted"
            )
        print(f"  ok, checksum matches" if want else "  ok (no checksum recorded yet)")
        fetched += 1

    if not missing:
        print("every release is already in data/raw/")
    else:
        print(f"\nfetched {fetched} of {missing}")


if __name__ == "__main__":
    main()
