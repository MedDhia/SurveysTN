#!/usr/bin/env python3
"""Match variables across waves, and attach the question each one asked.

Arab Barometer keeps question numbering broadly stable across waves but changes
the case of variable names between releases (``country`` in Wave II, ``COUNTRY``
in Wave VIII), so variables are matched on the upper-cased name. A matching name
is weak evidence on its own, though: over thirteen years the same number is
sometimes reused for a different question. The crosswalk therefore carries the
question text alongside each name and flags where it drifts.

Question text comes from two places, in this order:

1. The variable label in the release, where the release has one.
2. The wave's questionnaire PDF in ``docs/questionnaires/``, parsed by question
   number. This is the only source for Wave IV, whose release carries no labels,
   and it fills gaps elsewhere.

A variable like ``Q127_1A`` is a sub-item of question ``Q127``; where no exact
number matches, the parser falls back to the stem and the match is recorded as
``questionnaire (stem)`` so it is never mistaken for the item's own wording.

The parse is checked rather than trusted: for every wave whose release does carry
labels, the parsed text is compared with the label, and the agreement rate is
written to ``catalog/crosswalk-report.json`` along with the per-wave counts.

Writes ``docs/crosswalk.csv``, ``docs/crosswalk.md`` and
``catalog/crosswalk-report.json``.
"""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

import pandas as pd
import pyreadstat
import pypdf

ROOT = Path(__file__).resolve().parent.parent

# An identifier is a short alphabetic prefix followed by a number: q101, Q127,
# aid1a, t302, eg3041. Extraction of the Wave IV PDF reverses some of them --
# "101q" for "q101", a bidi artifact of the bilingual original -- so that form is
# matched too and put back the right way round.
QUESTION_START = re.compile(r"^\s*([A-Za-z]{1,5}\d{1,4}[A-Za-z0-9_]*)[.:]?\s+(\S.*)$")
QUESTION_START_REVERSED = re.compile(r"^\s*(\d{1,4}[A-Za-z0-9_]*)([Qq])[.:]?\s+(\S.*)$")
RESPONSE_OPTION = re.compile(r"^\s*-?\d{1,3}[.)]\s")
PAGE_NOISE = re.compile(r"^\s*(www\.arabbarometer\.org|\d+|Page \d+.*)\s*$")
# Only fieldwork directives are dropped. A bracket carrying part of the question
# -- "[your country]", "[the President]" -- is kept, or the wording loses its object.
DIRECTIVE_BRACKETS = re.compile(
    r"\[\s*(PROGRAMMER|INTERVIEWER|ENUMERATOR|SPLIT|SKIP|NOTE|READ|DO NOT READ|IF)\b[^\]]*\]",
    re.I,
)
SQUARE_BRACKETS = re.compile(r"\[[^\]]*\]")
NAME_PREFIX = re.compile(r"^\s*[Qq]\d{1,4}[A-Za-z0-9_]*[.:]?\s*")

AGREEMENT_FLOOR = 0.6  # difflib ratio above which two wordings count as the same

# In some questionnaires the response options extract onto the same line as the
# question ("Gender 1. Male2. Female"), so a parsed stem is cut at the first one.
GLUED_OPTIONS = re.compile(r"(\s+-?\d{1,3}[.)]\s*[A-Z_]|_{3,})")


def tidy(text: str) -> str:
    text = DIRECTIVE_BRACKETS.sub(" ", text)
    text = re.sub(r"\(\s*Read\s*\)\s*:?", " ", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip(" :.\t")


def trim_options(text: str) -> str:
    """Drop response options that extracted onto the question's own line."""
    cut = GLUED_OPTIONS.search(text)
    return (text[: cut.start()] if cut else text).strip(" :.,\t")


def informative(label: str) -> bool:
    """Is a release label more than a restatement of the variable name?

    Some labels are just the number -- Wave VIII stores "Q1." for the governorate
    -- and the questionnaire wording is worth more than that.
    """
    return len(normalise(label)) >= 3


def normalise(text: str) -> str:
    """Reduce a wording to comparable form: no variable-name prefix, no punctuation."""
    text = SQUARE_BRACKETS.sub(" ", str(text))
    text = NAME_PREFIX.sub("", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def agree(a: str, b: str) -> float:
    a, b = normalise(a), normalise(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def parse_questionnaire(pdf: Path) -> dict[str, str]:
    """Pull question number -> question text out of a questionnaire PDF.

    A question runs from the line its number appears on until the first response
    option, blank line, page furniture, or the next question number.
    """
    reader = pypdf.PdfReader(str(pdf))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)

    questions: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current, buffer
        # First occurrence wins: a question number reappearing later is usually a
        # routing instruction or a grid header referring back to it.
        if current and current not in questions:
            body = tidy(" ".join(buffer))
            body = trim_options(body)
            if len(body) > 8:
                questions[current] = body
        current, buffer = None, []

    for line in text.split("\n"):
        reversed_match = QUESTION_START_REVERSED.match(line)
        match = QUESTION_START.match(line)
        if reversed_match:
            flush()
            current = f"{reversed_match.group(2)}{reversed_match.group(1)}".upper()
            buffer = [reversed_match.group(3)]
            continue
        if match:
            flush()
            current, buffer = match.group(1).upper(), [match.group(2)]
            continue
        if current is None:
            continue
        if RESPONSE_OPTION.match(line) or PAGE_NOISE.match(line) or not line.strip():
            flush()
            continue
        buffer.append(line.strip())
    flush()
    return questions


def stem_candidates(name: str) -> list[str]:
    """Plausible parent question numbers for a sub-item like Q127_1A or Q201B."""
    seen, out = {name}, []
    for cut in (
        re.sub(r"_.*$", "", name),
        re.sub(r"[A-Z]+$", "", name),
        re.sub(r"_.*$", "", re.sub(r"[A-Z]+$", "", name)),
    ):
        if cut and cut not in seen:
            seen.add(cut)
            out.append(cut)
    return out


def load_wave(survey: dict, questions: dict[str, str]) -> dict:
    """Variable names and best-available question text for one wave."""
    sav = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
    _, meta = pyreadstat.read_sav(str(sav), metadataonly=True)

    names, label_text, sheet_text, text, source = {}, {}, {}, {}, {}
    for col in meta.column_names:
        key = col.upper()
        names[key] = col

        label = (meta.column_names_to_labels.get(col) or "").strip()
        if label and informative(label):
            label_text[key] = tidy(label)

        if key in questions:
            sheet_text[key] = questions[key]
        else:
            for parent in stem_candidates(key):
                if parent in questions:
                    sheet_text[key] = questions[parent]
                    source[key] = f"questionnaire (stem {parent})"
                    break

        # The release label is what the publisher attached to the column, so it
        # wins where it exists; the questionnaire fills the gaps.
        if key in label_text:
            text[key] = label_text[key]
            source[key] = "release label"
        elif key in sheet_text:
            text[key] = sheet_text[key]
            source.setdefault(key, "questionnaire")

    return {
        "names": names,
        "label_text": label_text,
        "sheet_text": sheet_text,
        "text": text,
        "source": source,
        "labelled": meta,
    }


def check_parse(wave: dict, questions: dict[str, str]) -> dict:
    """Compare parsed question text with the release's own labels, where it has them."""
    meta = wave["labelled"]
    labels = {
        c.upper(): (meta.column_names_to_labels.get(c) or "").strip()
        for c in meta.column_names
    }
    labels = {k: v for k, v in labels.items() if v}
    shared = [k for k in labels if k in questions]
    ratios = [agree(labels[k], questions[k]) for k in shared]
    agreeing = sum(1 for r in ratios if r >= AGREEMENT_FLOOR)
    return {
        "variables_with_labels": len(labels),
        "questions_parsed": len(questions),
        "compared": len(shared),
        "agreeing": agreeing,
        "agreement_rate": round(agreeing / len(shared), 3) if shared else None,
    }


def main() -> None:
    catalog = json.loads((ROOT / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "catalog" / "sources.json").read_text(encoding="utf-8"))
    specs = {
        (w["series"], f"w{w['wave']:02d}" + (f"p{w['part']}" if w.get("part") else "")): w
        for w in manifest["waves"]
    }

    surveys = catalog["surveys"]
    tags = [s["tag"] for s in surveys]
    waves, report = {}, {}

    for s in surveys:
        spec = specs[(s["series"], s["tag"])]
        questionnaire = spec.get("questionnaire")
        questions = (
            parse_questionnaire(ROOT / questionnaire["file"]) if questionnaire else {}
        )
        waves[s["tag"]] = load_wave(s, questions)
        entry = {
            "wave_label": s["wave_label"],
            "questionnaire": questionnaire["file"] if questionnaire else None,
        }
        entry.update(
            check_parse(waves[s["tag"]], questions)
            if questions
            else {"questions_parsed": 0, "compared": 0, "agreeing": 0, "agreement_rate": None}
        )
        report[s["tag"]] = entry
        print(
            f"{s['tag']}: parsed {entry['questions_parsed']:>3} questions | "
            f"compared {entry['compared']:>3} against release labels | "
            f"agreement {entry['agreement_rate'] if entry['agreement_rate'] is not None else 'n/a'}"
        )

    every_name = sorted({n for w in waves.values() for n in w["names"]})
    rows = []
    for name in every_name:
        present = [t for t in tags if name in waves[t]["names"]]
        texts = {t: waves[t]["text"][t2] for t in present for t2 in [name] if t2 in waves[t]["text"]}
        from_questionnaire = [
            t for t in present if waves[t]["source"].get(name, "").startswith("questionnaire")
        ]

        # Does the wording hold across the waves that carry this name? Compare
        # like with like: questionnaire text against questionnaire text where two
        # or more waves have it, because a release label is often a terse tag
        # ("Age") where the questionnaire spells the question out ("How old are
        # you?"), and comparing the two forms would read as drift that is not there.
        sheet = [waves[t]["sheet_text"][name] for t in present if name in waves[t]["sheet_text"]]
        labels = [waves[t]["label_text"][name] for t in present if name in waves[t]["label_text"]]
        if len(sheet) >= 2:
            wordings, basis = sheet, "questionnaire"
        elif len(labels) >= 2:
            wordings, basis = labels, "release labels"
        else:
            wordings, basis = [], ""
        if len(wordings) >= 2:
            worst = min(
                agree(a, b)
                for i, a in enumerate(wordings)
                for b in wordings[i + 1 :]
            )
            varies = "yes" if worst < AGREEMENT_FLOOR else "no"
        else:
            worst, varies = None, "unknown"

        candidates = [
            (waves[t]["text"][name], f"{t} {waves[t]['source'][name]}")
            for t in present
            if name in waves[t]["text"]
        ]
        best_text, best_source = max(candidates, key=lambda c: len(c[0]), default=("", ""))

        row = {
            "variable": name,
            "n_waves": len(present),
            "waves": ";".join(present),
            "first_wave": present[0],
            "last_wave": present[-1],
            # The fullest wording available anywhere, which is not always the
            # release label: Arab Barometer's own Wave VIII label for Q101 is
            # truncated to "...the current economic situation in?", where the
            # questionnaire has the whole question.
            "question_text": best_text,
            "question_text_source": best_source,
            "text_varies_across_waves": varies,
            "comparison_basis": basis,
            "compared_wordings": len(wordings),
            "lowest_text_agreement": round(worst, 3) if worst is not None else "",
            "text_from_questionnaire": ";".join(from_questionnaire),
        }
        for t in tags:
            row[f"{t}_name"] = waves[t]["names"].get(name, "")
            row[f"{t}_text"] = texts.get(t, "")
        rows.append(row)

    df = pd.DataFrame(rows).sort_values(["n_waves", "variable"], ascending=[False, True])
    df.to_csv(ROOT / "docs" / "crosswalk.csv", index=False)

    (ROOT / "catalog" / "crosswalk-report.json").write_text(
        json.dumps(
            {
                "waves": report,
                "variables": len(df),
                "with_question_text": int((df["question_text"] != "").sum()),
                "in_every_wave": int((df["n_waves"] == len(tags)).sum()),
                "wording_drifts": int((df["text_varies_across_waves"] == "yes").sum()),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    (ROOT / "docs" / "crosswalk.md").write_text(render_summary(df, tags, report), encoding="utf-8")
    print(
        f"\nwrote docs/crosswalk.csv: {len(df):,} variables, "
        f"{(df['question_text'] != '').sum():,} with question text"
    )


def render_summary(df: pd.DataFrame, tags: list[str], report: dict) -> str:
    counts = df["n_waves"].value_counts().sort_index(ascending=False)
    core = df[(df["n_waves"] == len(tags)) & (df["text_varies_across_waves"] == "no")]

    lines = [
        "# Cross-wave crosswalk",
        "",
        "Generated by `scripts/build_crosswalk.py`. The full table is",
        "[`crosswalk.csv`](crosswalk.csv): one row per variable, the name it takes in",
        "each wave, the question each wave asked, and whether the wording held.",
        "",
        "## How many waves each variable spans",
        "",
        "| Waves | Variables |",
        "|---:|---:|",
    ]
    for n, c in counts.items():
        lines.append(f"| {n} | {c:,} |")

    lines += [
        "",
        f"{(df['text_varies_across_waves'] == 'yes').sum():,} variables carry a name in more",
        "than one wave but wording that does not match between them. That is the column",
        "worth checking before pooling: `text_varies_across_waves`, with the weakest",
        "pairwise agreement in `lowest_text_agreement`.",
        "",
        f"## Present in all {len(tags)} surveys with stable wording",
        "",
        f"{len(core)} variables. These are the safest to stack, and even here confirm the",
        "response scale in each wave's `codebook.csv` — the crosswalk compares question",
        "wording, not answer options.",
        "",
        "| Variable | Question |",
        "|---|---|",
    ]
    for _, r in core.iterrows():
        text = r["question_text"][:110] + ("…" if len(r["question_text"]) > 110 else "")
        lines.append(f"| `{r['variable']}` | {text} |")

    lines += [
        "",
        "## Where the question text comes from",
        "",
        "The release's own variable labels where it has them, otherwise the wave's",
        "questionnaire PDF parsed by question number. Wave IV has no labels at all, so",
        "everything it contributes is parsed. The parse is validated against the waves",
        "that do carry labels:",
        "",
        "| Wave | Questions parsed | Compared with labels | Agreement |",
        "|---|---:|---:|---:|",
    ]
    for tag, r in report.items():
        rate = "—" if r["agreement_rate"] is None else f"{r['agreement_rate']:.0%}"
        lines.append(
            f"| {r['wave_label']} | {r['questions_parsed']} | {r['compared']} | {rate} |"
        )
    lines += [
        "",
        "Agreement is the share of comparable variables where the parsed text and the",
        "release label match at a difflib ratio of 0.6 or better. It is a check on the",
        "parser, not on the data: the two should say the same thing, and where they",
        "disagree the release label is the one that is used.",
        "",
        "Text taken from a questionnaire is marked per wave in `text_from_questionnaire`.",
        "A sub-item such as `Q127_1A` inherits the wording of its parent question `Q127`",
        "where no exact number matches, so treat those as the question stem rather than",
        "the item's own wording.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
