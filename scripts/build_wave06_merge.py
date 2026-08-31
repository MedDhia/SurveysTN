#!/usr/bin/env python3
"""Stack the three Wave VI rounds into one file.

Arab Barometer fielded Wave VI as three telephone rounds -- July 2020, October
2020, March 2021 -- with separate samples and separate questionnaires. They are
not a panel and cannot be joined; what they can be is stacked, giving 3,207
Tunisian respondents across three points in the pandemic with a ``PART`` column
saying which round each came from.

Stacking is where a merge quietly goes wrong, because the three rounds do not
agree with each other. 188 variables appear across the three, only 41 in all
three. Worse, a numeric code can mean different things from one round to the
next: ``Q1012A`` code 7 is "Sunni" in Part 2 and "Shafi'i'" in Part 3, because the
sect list was recoded between rounds. Appending that column would silently
produce a variable that means two things.

So every code carried by more than one round is compared before anything is
stacked, and the differences are sorted into two kinds:

reconcilable
    The rounds label the same code the same thing in different words -- "Other"
    against "Other, specify: ___", "Corruption" against "Financial and
    administrative corruption", or any of the ways a round writes "refused". The
    column is merged, and the fullest label kept.

unresolved
    The rounds disagree about what the code means. The column is **not** merged:
    it is split into ``<NAME>__P1``, ``<NAME>__P2``, ``<NAME>__P3`` so each round
    keeps its own codes and labels, and nothing is reconciled behind your back.

Every difference of either kind is written to ``catalog/wave-06-merge-report.json``
so the judgement can be reviewed rather than taken on trust.

Writes ``data/arab-barometer/wave-06-merged/``.
"""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

import pandas as pd
import pyreadstat

from extract_tunisia import ROOT, is_blank, sha256, build_codebook, STATA_LABEL_MAX

PARTS = (1, 2, 3)
SLUG = "wave-06-merged"
STEM = "arab-barometer-w06-tunisia-merged"
SIMILARITY_FLOOR = 0.6

# Codes for "no answer" and "something else" are relabelled freely between rounds
# without changing what they mean, so a difference in their wording is not a
# difference in the data.
NON_RESPONSE = re.compile(
    r"refus|declin|don.?t know|do not know|not applicable|^na\b|no answer|"
    r"does not happen|respondent refused",
    re.I,
)
CATCH_ALL = re.compile(r"^\s*(other|something else|none of)", re.I)

# Codes the automatic test flags but a person has read and judged equivalent.
# Part 1 abbreviates response options that Parts 2 and 3 spell out, and no string
# comparison recovers "Healthcare system can't handle" from "Inability of the
# healthcare system to handle COVID-19 cases". Each entry is a deliberate
# decision, listed so it can be argued with; a code not listed here stays split
# however obvious it looks. Q1012A is deliberately absent: its sect list really
# was recoded between rounds.
REVIEWED_EQUIVALENT = {
    ("Q2061A", 15): "Part 1 'COVID-19' abbreviates 'The spread of the coronavirus'",
    ("Q2ACOVID19", 1): "Part 1 abbreviates 'Having a member of your family get very ill or die'",
    ("Q2ACOVID19", 4): "Part 1 abbreviates 'Inability of the healthcare system to handle COVID-19 cases'",
    ("Q2ACOVID19", 5): "Part 1 abbreviates 'The government's response has not been adequate'",
    ("Q2BCOVID19", 1): "Part 1 abbreviates 'The health threat posed by the coronavirus is exaggerated'",
    ("Q2BCOVID19", 4): "Part 1 abbreviates 'The country's healthcare infrastructure can handle coronavirus cases'",
    ("Q2BCOVID19", 5): "Part 1 abbreviates 'The government's response has been adequate to stop the spread'",
}


def flatten(text: str) -> str:
    text = re.sub(r"\[[^\]]*\]", " ", str(text))
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def same_meaning(a: str, b: str) -> bool:
    """Do two labels for one code say the same thing?"""
    if NON_RESPONSE.search(a) and NON_RESPONSE.search(b):
        return True
    if CATCH_ALL.match(a) and CATCH_ALL.match(b):
        return True
    x, y = flatten(a), flatten(b)
    if not x or not y:
        return False
    if x in y or y in x:  # one round spells out what the other abbreviates
        return True
    return difflib.SequenceMatcher(None, x, y).ratio() >= SIMILARITY_FLOOR


def load_parts() -> dict[int, tuple[pd.DataFrame, object]]:
    out = {}
    for n in PARTS:
        path = ROOT / f"data/arab-barometer/wave-06-part-{n}/arab-barometer-w06p{n}-tunisia.sav"
        df, meta = pyreadstat.read_sav(str(path), user_missing=True)
        # Part 3 stores the interview date as a string and the others as dates;
        # one text form serves all three and survives every output format.
        df["DATE"] = df["DATE"].map(lambda v: "" if pd.isna(v) else str(v)[:10])
        out[n] = (df, meta)
    return out


def compare_codes(parts: dict) -> tuple[dict[str, list], dict[str, list]]:
    """Split the code differences between rounds into reconcilable and unresolved."""
    reconcilable: dict[str, list] = {}
    unresolved: dict[str, list] = {}
    names = sorted({c for df, _ in parts.values() for c in df.columns})

    for name in names:
        present = [n for n in PARTS if name in parts[n][0].columns]
        if len(present) < 2:
            continue
        maps = {n: (parts[n][1].variable_value_labels.get(name) or {}) for n in present}
        for code in sorted({c for m in maps.values() for c in m}):
            seen = {n: maps[n][code] for n in present if code in maps[n]}
            if len(seen) < 2:
                continue
            labels = list(seen.values())
            key = (name, int(code) if float(code).is_integer() else code)
            reviewed = REVIEWED_EQUIVALENT.get(key)
            if reviewed or all(
                same_meaning(a, b)
                for i, a in enumerate(labels)
                for b in labels[i + 1 :]
            ):
                if len({flatten(v) for v in labels}) > 1:
                    difference = {"code": code, "labels": {str(n): v for n, v in seen.items()}}
                    if reviewed:
                        difference["resolved_by_review"] = reviewed
                    reconcilable.setdefault(name, []).append(difference)
            else:
                unresolved.setdefault(name, []).append(
                    {"code": code, "labels": {str(n): v for n, v in seen.items()}}
                )
    return reconcilable, unresolved


def main() -> None:
    parts = load_parts()
    reconcilable, unresolved = compare_codes(parts)
    split = sorted(unresolved)
    print(f"code differences: {len(reconcilable)} reconcilable, {len(unresolved)} unresolved")
    for name in split:
        print(f"  splitting {name}: {len(unresolved[name])} codes disagree between rounds")

    # Rename the columns that must not be merged, before anything is stacked.
    frames = []
    for n in PARTS:
        df, meta = parts[n]
        df = df.rename(columns={c: f"{c}__P{n}" for c in split if c in df.columns})
        df.insert(0, "PART", n)
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True, sort=False)

    # ID restarts from a low number in each round and does not identify a person
    # across rounds, so the merged file gets a key of its own.
    merged.insert(1, "MERGE_ID", [f"w06p{p}-{int(i)}" for p, i in zip(merged["PART"], merged["ID"])])

    ordered = ["PART", "MERGE_ID"]
    for n in PARTS:
        for c in parts[n][0].columns:
            c = f"{c}__P{n}" if c in split else c
            if c not in ordered:
                ordered.append(c)
    merged = merged[ordered]

    # Labels: take the fullest wording any round gives, since the rounds abbreviate
    # inconsistently and the code meanings have already been checked to agree.
    var_labels, value_labels = {"PART": "Wave VI round (1, 2 or 3)", "MERGE_ID": "Row key: round and within-round ID"}, {}
    value_labels["PART"] = {1: "Part 1 (July 2020)", 2: "Part 2 (October 2020)", 3: "Part 3 (March 2021)"}
    for col in merged.columns:
        if col in var_labels:
            continue
        candidates, codes = [], {}
        for n in PARTS:
            src = col[:-4] if col.endswith(f"__P{n}") else col
            if col.endswith("__P") or (col.endswith(f"__P{n}") is False and "__P" in col):
                continue
            if src in parts[n][0].columns:
                candidates.append((parts[n][1].column_names_to_labels.get(src) or "").strip())
                for code, label in (parts[n][1].variable_value_labels.get(src) or {}).items():
                    key = int(code) if float(code).is_integer() else code
                    if key not in codes or len(label) > len(codes[key]):
                        codes[key] = label
        var_labels[col] = max(candidates, key=len, default="")
        if codes:
            value_labels[col] = codes

    dest = ROOT / "data" / "arab-barometer" / SLUG
    dest.mkdir(parents=True, exist_ok=True)

    pyreadstat.write_sav(
        merged,
        str(dest / f"{STEM}.sav"),
        column_labels=[var_labels[c] for c in merged.columns],
        variable_value_labels=value_labels,
        file_label="Arab Barometer Wave VI Parts 1-3 stacked - Tunisia",
    )
    pyreadstat.write_dta(
        merged,
        str(dest / f"{STEM}.dta"),
        column_labels=[
            (v[: STATA_LABEL_MAX - 3] + "...") if len(v) > STATA_LABEL_MAX else v
            for v in (var_labels[c] for c in merged.columns)
        ],
        variable_value_labels=value_labels,
        version=14,
    )
    merged.to_csv(dest / f"{STEM}-codes.csv", index=False)
    labelled = merged.copy()
    for var, labels in value_labels.items():
        labelled[var] = labelled[var].map(
            lambda v: labels.get(int(v) if isinstance(v, float) and v.is_integer() else v, v)
        )
    labelled.to_csv(dest / f"{STEM}-labels.csv", index=False)

    codebook = build_codebook(merged, var_labels, value_labels)
    # Which rounds actually asked each variable is the first thing to know here.
    for row in codebook:
        col = row["variable"]
        asked = [
            str(n)
            for n in PARTS
            if (col[:-4] if col.endswith(f"__P{n}") else col) in parts[n][0].columns
            and ("__P" not in col or col.endswith(f"__P{n}"))
        ]
        row["asked_in_parts"] = ";".join(asked)
        sub = merged.loc[merged["PART"].isin(int(a) for a in asked), col] if asked else merged[col]
        row["n_valid_where_asked"] = int((~is_blank(sub)).sum()) if asked else 0
    pd.DataFrame(codebook).to_csv(dest / "codebook.csv", index=False)
    (dest / "codebook.json").write_text(
        json.dumps(codebook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    entry = {
        "kind": "derived",
        "built_by": "scripts/build_wave06_merge.py",
        "series": "arab-barometer",
        "label": "Arab Barometer Wave VI Parts 1-3, stacked",
        "slug": SLUG,
        "stem": STEM,
        "path": f"data/arab-barometer/{SLUG}",
        "country": "Tunisia",
        "n_respondents": int(len(merged)),
        "n_respondents_by_part": {str(n): int((merged["PART"] == n).sum()) for n in PARTS},
        "n_variables": int(merged.shape[1]),
        "sources": [f"data/arab-barometer/wave-06-part-{n}" for n in PARTS],
        "split_variables": split,
        "unresolved_code_differences": unresolved,
        "reconciled_code_differences": reconcilable,
        "files": {},
    }
    for f in sorted(dest.iterdir()):
        if f.name != "README.md":
            entry["files"][f.name] = {"bytes": f.stat().st_size, "sha256": sha256(f)}

    (ROOT / "catalog" / "wave-06-merge-report.json").write_text(
        json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (dest / "README.md").write_text(render_readme(entry, merged, codebook), encoding="utf-8")
    print(f"\nwrote {dest.relative_to(ROOT)}: {len(merged):,} rows x {merged.shape[1]} variables")


def render_readme(e: dict, merged: pd.DataFrame, codebook: list[dict]) -> str:
    by_part = e["n_respondents_by_part"]
    in_all = sum(1 for r in codebook if r["asked_in_parts"] == "1;2;3")
    in_one = sum(1 for r in codebook if len(r["asked_in_parts"].split(";")) == 1 and r["asked_in_parts"])

    lines = [
        "# Arab Barometer Wave VI — Tunisia, three rounds stacked",
        "",
        "Derived, not a release. Built from the three Wave VI folders by",
        "`scripts/build_wave06_merge.py`; regenerate rather than edit.",
        "",
        "| | |",
        "|---|---|",
        f"| Respondents | {e['n_respondents']:,} ({by_part['1']} + {by_part['2']} + {by_part['3']}) |",
        f"| Variables | {e['n_variables']:,} — {in_all} asked in all three rounds, {in_one} in one |",
        "| Rounds | Part 1 Jul 2020, Part 2 Oct 2020, Part 3 Mar 2021 |",
        "",
        "## Read this before using it",
        "",
        "**These are three samples, not three interviews with the same people.** The",
        "rounds share no respondents that can be identified as shared: their `ID` values",
        "overlap, but on the overlapping values sex agrees at chance and age almost never,",
        "so the IDs are per-round sequence numbers. `MERGE_ID` gives each row a key that is",
        "unique in this file; nothing links a row in one round to a row in another. Treat",
        "the file as three pooled cross-sections and put `PART` in your model.",
        "",
        "**Most variables were not asked in every round.** `codebook.csv` carries",
        "`asked_in_parts` and `n_valid_where_asked` for each. A variable that is blank for",
        "two thirds of the file is usually a variable those rounds never asked, not",
        "non-response — check the column before reading a missingness pattern into it.",
        "",
        "**The weights are per round.** Each round's `WT` is scaled to its own sample, so",
        "the three sets of weights sum to three separate populations. Weighting the stacked",
        "file with `WT` as it stands gives each round equal total weight only by accident of",
        "its sample size. What to do depends on the estimand: for a pooled estimate treating",
        "the rounds as equally informative, rescale within round so each contributes the",
        "same total; for a round-by-round comparison, which is what these rounds are for,",
        "weight and estimate within `PART` and compare. No pooled weight is supplied here,",
        "because the right one is not a property of the data.",
        "",
    ]

    if e["split_variables"]:
        lines += [
            "## Variables held apart",
            "",
            "These carry a code that means different things in different rounds, so they are",
            "**not** merged into one column. Each round keeps its own in `<NAME>__P<n>`:",
            "",
            "| Variable | What disagrees |",
            "|---|---|",
        ]
        for name in e["split_variables"]:
            diffs = e["unresolved_code_differences"][name]
            first = diffs[0]
            shown = ", ".join(f"P{n} “{v}”" for n, v in first["labels"].items())
            more = f" (+{len(diffs) - 1} more codes)" if len(diffs) > 1 else ""
            lines += [f"| `{name}` | code {int(first['code'])}: {shown}{more} |"]
        lines += [
            "",
            "`Q1012A` is the clear case: the religious-sect list was recoded between rounds,",
            "so code 7 is \"Sunni\" in Part 2 and \"Shafi'i'\" in Part 3. It happens to be empty",
            "for every Tunisian respondent in all three rounds — the question was not asked in",
            "Tunisia — so nothing is lost here in practice, but the column is split anyway",
            "rather than merged on the assumption that it stays empty.",
            "",
        ]

    lines += [
        "## Where the rounds only differed in wording",
        "",
        f"{len(e['reconciled_code_differences'])} variables label a shared code differently",
        "without meaning anything different — \"Other\" against \"Other, specify: ___\",",
        "\"Corruption\" against \"Financial and administrative corruption\", the several ways a",
        "round writes \"refused\". Those columns are merged and the fullest label kept. Every",
        "one is listed in [`../../../catalog/wave-06-merge-report.json`](../../../catalog/wave-06-merge-report.json)",
        "with the wording each round used, so the call can be checked.",
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
        "`scripts/verify.py` rebuilds this file from the three round folders and compares it",
        "cell by cell, so it cannot drift from the rounds it came from.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
