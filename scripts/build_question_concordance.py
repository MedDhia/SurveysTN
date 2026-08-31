#!/usr/bin/env python3
"""Find the same question asked in more than one survey, across every series.

``docs/crosswalk.csv`` matches variables by name and only within a series, which is
right for tracing one programme through its own waves and useless for asking what
Arab Barometer and Afrobarometer both asked. This does the other thing: it ignores
names entirely and groups variables by the question they carry, anywhere in the
archive.

Two tiers, and nothing looser:

``identical``
    The wording matches exactly once the variable-name prefix, bracketed fieldwork
    directives, case and punctuation are stripped.

``near``
    Content words overlap at a Jaccard of 0.85 or better and one wording's words are
    at least 80% contained in the other's. That admits the register difference this
    archive is full of -- Arab Barometer's "Q1015. Monthly household income in local
    currency" against the Arab Opinion Index's "Q1210. How much is the monthly
    household income in the local currency" -- without admitting a question stem
    matched to one of its own sub-items, which is what a containment test alone
    does.

Both tiers are lexical. Two questions that ask the same thing in different words --
"How would you evaluate the current economic situation?" against "In general, how
would you describe the present economic condition of this country?" -- will not be
found here, and their absence is not evidence that the archive lacks them.

Writes ``docs/question-concordance.csv`` and ``docs/question-concordance.md``.
"""

from __future__ import annotations

import collections
import itertools
import json
import re
from pathlib import Path

import pandas as pd

from extract_tunisia import ROOT

NAME_PREFIX = re.compile(r"^\s*[A-Za-z]{0,5}\d{1,4}[A-Za-z0-9_]*[.:]?\s*")
DIRECTIVE = re.compile(r"\[[^\]]*\]")

SHORT = {
    "arab-barometer": "AB",
    "arab-opinion-index": "AOI",
    "afrobarometer": "Afro",
    "world-values-survey": "WVS",
}

JACCARD_FLOOR = 0.85
CONTAINMENT_FLOOR = 0.8
# Exact wording is strong evidence however short it is: "employment status" is two
# content words and matches across ten surveys. The minimum applies only to the near
# tier, where a short wording would pair on too little.
MIN_NORMALISED_CHARS = 12
MIN_CONTENT_WORDS_FOR_NEAR = 3
# A word this common carries no information about which question it belongs to, and
# pairing every variable that shares one would be most of the archive.
MAX_POSTINGS = 400

# Negation is deliberately absent from this list. Dropping it as noise makes
# "Democratic systems are not effective at maintaining order" and "Non-democratic
# systems are not effective at maintaining order" look like the same question, and
# they are opposites -- Arab Barometer Wave VIII asks both.
STOPWORDS = set(
    """a an the of in on at to for with and or is are was were be been being do does
    did how what which who whom whose you your yours i we they he she it its this that
    these those please read out yes if then than as by from about would could
    should will can may much many any some all very more most other others don t s so
    have has had there their them our us me my""".split()
)
NEGATIONS = frozenset({"not", "no", "never", "nor", "non", "without", "none", "cannot"})


def normalise(text: str) -> str:
    text = DIRECTIVE.sub(" ", str(text))
    text = NAME_PREFIX.sub("", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def content_words(text: str) -> frozenset[str]:
    return frozenset(w for w in normalise(text).split() if w not in STOPWORDS and len(w) > 2)


def numbers(text: str) -> list[str]:
    return re.findall(r"\d+", normalise(text))


class Union:
    """Union-find, to grow pairs into groups."""

    def __init__(self) -> None:
        self.parent: dict[int, int] = {}

    def find(self, x: int) -> int:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def join(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def load_items() -> list[dict]:
    frame = pd.read_csv(ROOT / "docs" / "crosswalk.csv", keep_default_na=False)
    tags = [
        c[: -len("_text")]
        for c in frame.columns
        if c.endswith("_text") and f"{c[: -len('_text')]}_name" in frame.columns
    ]
    items = []
    for _, row in frame.iterrows():
        for tag in tags:
            name, text = row[f"{tag}_name"], row[f"{tag}_text"]
            if not name or not text:
                continue
            normalised = normalise(text)
            if len(normalised) < MIN_NORMALISED_CHARS:
                continue
            words = content_words(text)
            items.append(
                {
                    "series": row["series"],
                    "survey": tag,
                    "variable": name,
                    "question_text": text,
                    "normalised": normalised,
                    "words": words,
                    "numbers": numbers(text),
                    "negations": frozenset(words & NEGATIONS),
                }
            )
    return items


def link(items: list[dict]) -> tuple[Union, dict[tuple[int, int], float]]:
    union = Union()
    strength: dict[tuple[int, int], float] = {}

    # Exact wording first: cheap, and the strongest evidence there is.
    by_text: dict[str, list[int]] = collections.defaultdict(list)
    for i, item in enumerate(items):
        by_text[item["normalised"]].append(i)
    for shared in by_text.values():
        for a, b in itertools.pairwise(shared):
            union.join(a, b)
            strength[(min(a, b), max(a, b))] = 1.0

    # Then near wording, over pairs that share at least one informative word.
    postings: dict[str, list[int]] = collections.defaultdict(list)
    for i, item in enumerate(items):
        if len(item["words"]) < MIN_CONTENT_WORDS_FOR_NEAR:
            continue
        for word in item["words"]:
            postings[word].append(i)

    counts: collections.Counter = collections.Counter()
    for holders in postings.values():
        if len(holders) > MAX_POSTINGS:
            continue
        for a, b in itertools.combinations(holders, 2):
            counts[(a, b)] += 1

    accepted = []
    for (a, b), shared in counts.items():
        first, second = items[a], items[b]
        if first["survey"] == second["survey"]:
            continue  # a survey asking itself twice is not a concordance
        if first["numbers"] != second["numbers"]:
            continue  # "Household 5" is not "Household 2"
        if first["negations"] != second["negations"]:
            continue  # a negated question is a different question, not a near one
        jaccard = shared / len(first["words"] | second["words"])
        containment = shared / min(len(first["words"]), len(second["words"]))
        if jaccard >= JACCARD_FLOOR and containment >= CONTAINMENT_FLOOR:
            accepted.append((jaccard, a, b))

    # Groups are grown from pairs, so a chain of near-matches can end up holding two
    # questions that were never compared with each other. The tell is a group that
    # holds two different wordings from the same survey: a survey does not ask one
    # question twice, so "attend a campaign rally" and "attend a campaign meeting"
    # landing together means the chain has drifted. Such a join is refused, and the
    # strongest pairs are considered first so the refusal falls on the weakest link.
    wordings: dict[int, dict[str, set[str]]] = {}
    for i, item in enumerate(items):
        root = union.find(i)
        wordings.setdefault(root, {}).setdefault(item["survey"], set()).add(item["normalised"])

    for jaccard, a, b in sorted(accepted, reverse=True):
        ra, rb = union.find(a), union.find(b)
        if ra == rb:
            continue
        merged = {s: set(v) for s, v in wordings.get(ra, {}).items()}
        for survey, texts in wordings.get(rb, {}).items():
            merged.setdefault(survey, set()).update(texts)
        if any(len(texts) > 1 for texts in merged.values()):
            continue
        union.join(a, b)
        wordings[union.find(a)] = merged
        strength[(min(a, b), max(a, b))] = round(jaccard, 3)
    return union, strength


def main() -> None:
    items = load_items()
    union, strength = link(items)

    clusters: dict[int, list[int]] = collections.defaultdict(list)
    for i in range(len(items)):
        if i in union.parent:
            clusters[union.find(i)].append(i)

    records, summaries = [], []
    for n, (_, members) in enumerate(
        sorted(clusters.items(), key=lambda kv: -len({items[i]["survey"] for i in kv[1]})), 1
    ):
        surveys = {items[i]["survey"] for i in members}
        if len(surveys) < 2:
            continue
        series = {items[i]["series"] for i in members}
        texts = {items[i]["normalised"] for i in members}
        tier = "identical" if len(texts) == 1 else "near"

        # How loosely the group is held together, over every pair inside it.
        weakest = 1.0
        for a, b in itertools.combinations(sorted(members), 2):
            first, second = items[a], items[b]
            both = first["words"] | second["words"]
            if both:
                weakest = min(weakest, len(first["words"] & second["words"]) / len(both))

        canonical = max((items[i]["question_text"] for i in members), key=len)
        cluster_id = f"Q{n:04d}"
        summaries.append(
            {
                "cluster": cluster_id,
                "tier": tier,
                "n_surveys": len(surveys),
                "n_series": len(series),
                "series": ";".join(sorted(series)),
                "surveys": ";".join(sorted(surveys)),
                "weakest_overlap": round(weakest, 3),
                "question_text": canonical,
            }
        )
        for i in sorted(members, key=lambda i: (items[i]["series"], items[i]["survey"])):
            records.append(
                {
                    "cluster": cluster_id,
                    "tier": tier,
                    "n_surveys": len(surveys),
                    "n_series": len(series),
                    "series": items[i]["series"],
                    "survey": items[i]["survey"],
                    "variable": items[i]["variable"],
                    "question_text": items[i]["question_text"],
                }
            )

    members = pd.DataFrame(records)
    summary = pd.DataFrame(summaries)
    members.to_csv(ROOT / "docs" / "question-concordance.csv", index=False)
    summary.to_csv(ROOT / "docs" / "question-concordance-groups.csv", index=False)
    (ROOT / "docs" / "question-concordance.md").write_text(render(summary), encoding="utf-8")

    cross = summary[summary["n_series"] >= 2]
    print(f"variables with question text: {len(items):,}")
    print(f"question groups spanning 2+ surveys: {len(summary):,}")
    print(f"   identical wording: {(summary['tier'] == 'identical').sum():,}")
    print(f"   near wording:      {(summary['tier'] == 'near').sum():,}")
    print(f"   spanning 2+ series: {len(cross):,}")
    print(f"wrote docs/question-concordance.csv ({len(members):,} rows) and .md")


def render(summary: pd.DataFrame) -> str:
    cross = summary[summary["n_series"] >= 2].sort_values(
        ["n_series", "n_surveys"], ascending=False
    )
    lines = [
        "# Question concordance",
        "",
        "The same question, asked in more than one survey. Generated by",
        "`scripts/build_question_concordance.py`. The full table is",
        "[`question-concordance.csv`](question-concordance.csv), one row per variable, with",
        "[`question-concordance-groups.csv`](question-concordance-groups.csv) one row per",
        "group and a `weakest_overlap` to sort by.",
        "",
        "This is the counterpart to [`crosswalk.md`](crosswalk.md). The crosswalk matches",
        "variables by name and only within a series, which traces one programme through",
        "its own waves. This ignores names entirely and groups by the question itself, so",
        "it can answer what two different programmes both asked.",
        "",
        f"**{len(summary):,} question groups span two or more surveys.** "
        f"{(summary['tier'] == 'identical').sum():,} are word-for-word identical and "
        f"{(summary['tier'] == 'near').sum():,} are near-identical. "
        f"**{len(cross):,} span more than one series** — those are the ones that make a",
        "cross-programme comparison possible at all.",
        "",
        "## Across series",
        "",
        "| Question | Series | Surveys |",
        "|---|---|---:|",
    ]
    for _, r in cross.iterrows():
        text = r["question_text"][:96] + ("…" if len(r["question_text"]) > 96 else "")
        badges = ", ".join(sorted(SHORT.get(s, s) for s in r["series"].split(";")))
        lines.append(f"| {text} | {badges} | {r['n_surveys']} |")

    lines += [
        "",
        "## What this does not find",
        "",
        "Both tiers are lexical. Two questions that ask the same thing in different words",
        "are not matched, and there is no way to read their absence as evidence the",
        "archive lacks them — Arab Barometer's \"How would you evaluate the current",
        "economic situation in your country?\" and a programme asking after \"the present",
        "economic condition of this country\" share barely a content word.",
        "",
        "A looser test was tried and rejected. Requiring only that one wording's words be",
        "contained in the other's finds 804 more cross-series pairs, and they are mostly a",
        "question stem matched to one of its own sub-items — Arab Barometer's \"I will name",
        "a number of institutions...\" against a single trust item. Containment alone",
        "cannot tell a stem from the thing it introduces, so both tiers here require the",
        "wordings to overlap symmetrically as well.",
        "",
        "Three things a bag of words gets wrong are guarded against explicitly.",
        "",
        "**Negation.** Arab Barometer Wave VIII asks both \"Democratic systems are not",
        "effective at maintaining order and stability\" and \"**Non**-democratic systems are",
        "not effective...\". Those differ by one word out of eleven and are opposites, so",
        "negation words are kept rather than dropped as noise, and a pair whose negations",
        "differ is refused.",
        "",
        "**Numbering.** \"Household 5\" and \"Household 2\" differ by a character. A pair must",
        "agree on the numbers in its wording.",
        "",
        "**Chaining.** Groups grow from pairs, so a chain can end up holding two questions",
        "that were never compared with each other. The tell is a group holding two",
        "different wordings from the same survey, since a survey does not ask one question",
        "twice — which is how \"attend a campaign rally\" and \"attend a campaign meeting\"",
        "first landed together. A join that would do that is refused, strongest pairs",
        "first. `weakest_overlap` still reports the loosest pair inside each group; a group",
        "sitting near the floor is one to read before trusting.",
        "",
        "## Before you compare",
        "",
        "A shared question is not a shared measurement. This compares wording only, and",
        "says nothing about the response options behind it — a four-point scale in one",
        "survey and a five-point scale in another are the same question and not the same",
        "variable. Check `codebook.csv` in each survey's folder for the scale, and",
        "`docs/missing-value-codes.md` for how each marks a non-answer, before putting two",
        "of these side by side.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
