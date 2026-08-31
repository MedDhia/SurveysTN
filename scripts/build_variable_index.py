#!/usr/bin/env python3
"""Build a cross-wave variable index.

Arab Barometer keeps question numbering broadly stable across waves but changes
the case of variable names between releases (``country`` in Waves II and V,
``COUNTRY`` in Wave VIII). The index therefore matches on the upper-cased name
and records the name as spelled in each wave, so a variable can be traced from
one wave to the next.

Writes ``docs/variable-index.csv``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    catalog = json.loads((ROOT / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    surveys = catalog["surveys"]

    index: dict[str, dict] = {}
    for s in surveys:
        wave = f"w{s['wave']:02d}"
        sav = ROOT / s["path"] / f"{s['series']}-{wave}-tunisia.sav"
        _, meta = pyreadstat.read_sav(str(sav), metadataonly=True)
        for name in meta.column_names:
            row = index.setdefault(name.upper(), {"variable": name.upper()})
            row[f"{wave}_name"] = name
            row[f"{wave}_label"] = meta.column_names_to_labels.get(name) or ""

    waves = [f"w{s['wave']:02d}" for s in surveys]
    cols = ["variable"] + [f"{w}_{k}" for w in waves for k in ("name", "label")]
    df = pd.DataFrame([{c: r.get(c, "") for c in cols} for r in index.values()])
    df["n_waves"] = sum((df[f"{w}_name"] != "").astype(int) for w in waves)
    df = df.sort_values(["n_waves", "variable"], ascending=[False, True])

    out = ROOT / "docs" / "variable-index.csv"
    out.parent.mkdir(exist_ok=True)
    df.to_csv(out, index=False)

    counts = df["n_waves"].value_counts().sort_index(ascending=False)
    print(f"wrote {out.relative_to(ROOT)}: {len(df):,} distinct variables")
    for n, c in counts.items():
        print(f"  present in {n} wave(s): {c:,}")


if __name__ == "__main__":
    main()
