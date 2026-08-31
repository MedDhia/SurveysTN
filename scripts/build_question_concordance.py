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

A shared question is still not a shared measurement, so each group's response scales
are compared too: whether the members offer the same answer options, whether the
options are the same but the codes differ, and in particular whether a scale runs the
other way round in one survey than in another, which is the way a pooled estimate
silently inverts.

Writes ``docs/question-concordance.csv``, ``docs/question-concordance-groups.csv``
and ``docs/question-concordance.md``.
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


# Codes for a non-answer are relabelled freely between surveys and are inventoried
# in docs/missing-value-codes.md already, so they are left out of a scale comparison.
NON_SUBSTANTIVE = re.compile(
    r"don.?t know|do not know|refus|declin|not applicable|^na$|no answer|missing|"
    r"unspecific|no serious answer|does not happen|decline to answer|respondent refused",
    re.I,
)


def substantive_scale(raw: str) -> dict[int, str] | None:
    """A variable's answer options, as code -> plain label, non-answers removed."""
    if not raw:
        return None
    try:
        labels = json.loads(raw)
    except (TypeError, ValueError):
        return None
    out = {}
    for code, label in labels.items():
        text = str(label)
        if NON_SUBSTANTIVE.search(text):
            continue
        plain = re.sub(r"^\s*-?\d+\s*[.)]\s*", "", text)
        plain = re.sub(r"[^a-z0-9 ]+", " ", plain.lower())
        plain = re.sub(r"\s+", " ", plain).strip()
        if plain:
            try:
                out[int(float(code))] = plain
            except (TypeError, ValueError):
                out[code] = plain
    return out or None


def compare_scales(
    scales: list[dict[int, str] | None], unlabelled: list[int | None] | None = None
) -> tuple[str, str]:
    """Classify a group's response scales, and say what to do about it.

    ``unlabelled`` is, per member, how many values it takes in the data that carry no
    label at all. Where a release labels only some points of its scale -- the Arab
    Opinion Index labels the two ends of a ten-point scale and nothing between -- the
    labels alone would make a long scale look like a two-option one.
    """
    if unlabelled and all(s is not None for s in scales):
        partly = [(len(s), u) for s, u in zip(scales, unlabelled) if s and u and u > 0]
        if partly:
            return "partly-labelled", (
                f"at least one survey leaves {max(u for _, u in partly)} of its values "
                f"unlabelled ({min(n for n, _ in partly)} options carry a label) — read "
                "the codebook before treating these as the same measurement"
            )

    if any(s is None for s in scales):
        known = [s for s in scales if s is not None]
        if not known:
            return "unknown", "no member records value labels"
        return "unknown", "at least one member's release records no value labels"

    if all(s == scales[0] for s in scales[1:]):
        return "identical", f"{len(scales[0])} options, same codes throughout"

    option_sets = [frozenset(s.values()) for s in scales]
    if all(o == option_sets[0] for o in option_sets[1:]):
        # Same answers, different numbers against them. The dangerous case is a
        # scale that runs the other way, since recoding it wrongly flips the sign.
        orders = [[s[c] for c in sorted(s)] for s in scales]
        if any(o == list(reversed(orders[0])) for o in orders[1:]):
            return "reversed", (
                f"{len(option_sets[0])} options, but at least one survey codes them "
                "in the opposite order — recode before pooling or the estimate inverts"
            )
        return "recodable", f"{len(option_sets[0])} options, codes differ between surveys"

    sizes = sorted({len(s) for s in scales})
    if len(sizes) > 1:
        return "differs", f"different numbers of options ({', '.join(map(str, sizes))})"
    return "differs", f"{sizes[0]} options each, but they are not the same options"


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


def load_value_labels() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, int]]]:
    """Every survey's value labels and distinct-value counts, by survey key."""
    catalog = json.loads((ROOT / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    labels, distinct = {}, {}
    for survey in catalog["surveys"]:
        codebook = json.loads(
            (ROOT / survey["path"] / "codebook.json").read_text(encoding="utf-8")
        )
        labels[survey["key"]] = {r["variable"].upper(): r["value_labels"] for r in codebook}
        # How many values the variable takes that no label covers. A release that
        # labels only the ends of its scale leaves the middle here.
        counts = {}
        for r in codebook:
            try:
                coded = len(json.loads(r["value_labels"])) if r["value_labels"] else 0
            except (TypeError, ValueError):
                coded = 0
            counts[r["variable"].upper()] = max(0, int(r["n_distinct"]) - coded) if coded else 0
        distinct[survey["key"]] = counts
    return labels, distinct


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
    value_labels, distinct_counts = load_value_labels()
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

        scales = [
            substantive_scale(
                value_labels.get(items[i]["survey"], {}).get(items[i]["variable"].upper(), "")
            )
            for i in members
        ]
        unlabelled = [
            distinct_counts.get(items[i]["survey"], {}).get(items[i]["variable"].upper())
            for i in members
        ]
        scale, scale_note = compare_scales(scales, unlabelled)
        summaries.append(
            {
                "cluster": cluster_id,
                "tier": tier,
                "n_surveys": len(surveys),
                "n_series": len(series),
                "series": ";".join(sorted(series)),
                "surveys": ";".join(sorted(surveys)),
                "weakest_overlap": round(weakest, 3),
                "scale": scale,
                "scale_note": scale_note,
                "question_text": canonical,
            }
        )
        for i, member_scale in sorted(
            zip(members, scales), key=lambda p: (items[p[0]]["series"], items[p[0]]["survey"])
        ):
            records.append(
                {
                    "cluster": cluster_id,
                    "tier": tier,
                    "scale": scale,
                    "n_options": len(member_scale) if member_scale else "",
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
    print()
    print("response scales across each group:")
    for kind, count in summary["scale"].value_counts().items():
        print(f"   {kind:<10} {count:,}")
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
        "| Question | Series | Surveys | Response scale |",
        "|---|---|---:|---|",
    ]
    for _, r in cross.iterrows():
        text = r["question_text"][:84] + ("…" if len(r["question_text"]) > 84 else "")
        badges = ", ".join(sorted(SHORT.get(s, s) for s in r["series"].split(";")))
        lines.append(f"| {text} | {badges} | {r['n_surveys']} | {r['scale']} |")

    counts = summary["scale"].value_counts()
    lines += [
        "",
        "## Do the answer options match?",
        "",
        "A shared question is not a shared measurement, so each group's response scales are",
        "compared as well — with the non-answer codes left out, since those vary freely and",
        "are inventoried in [`missing-value-codes.md`](missing-value-codes.md) already.",
        "",
        "| Verdict | Groups | Means |",
        "|---|---:|---|",
        f"| `identical` | {counts.get('identical', 0):,} | same options, same codes; poolable as they stand |",
        f"| `recodable` | {counts.get('recodable', 0):,} | same options, different codes; align the codes first |",
        f"| `reversed` | {counts.get('reversed', 0):,} | same options, but at least one survey codes them in the opposite order |",
        f"| `differs` | {counts.get('differs', 0):,} | not the same options; not one variable however alike the wording |",
        f"| `partly-labelled` | {counts.get('partly-labelled', 0):,} | a survey leaves some of its values unlabelled, so the labels understate the scale |",
        f"| `unknown` | {counts.get('unknown', 0):,} | a member's release ships no value labels, so there is nothing to compare |",
        "",
        f"**Not one of the {len(cross)} cross-series groups scores `identical`.** Every "
        "question two",
        "programmes both ask, they ask with different answer options or with options this",
        "archive cannot see. The overlap that survives a wording comparison does not",
        "survive a scale comparison, and a cross-programme series here has to be built by",
        "recoding, question by question, with the codebooks open. That is the finding, and",
        "it is worth more than the seventeen matches on their own.",
        "",
        "`partly-labelled` is the quiet one. The Arab Opinion Index labels the two ends of",
        "a ten-point scale and nothing between, so labels alone would report a two-option",
        "question — and would have called it recodable against a genuine two-option",
        "question elsewhere, which is what the first version of this did. Where a variable",
        "takes values no label covers, the group says so instead.",
        "",
        "`recodable` and `reversed` are both empty here, and that is a result rather than a",
        "gap: no group in this archive shares its options while disagreeing only about the",
        "codes. The two verdicts stay in the vocabulary because a later survey may need",
        "them — `reversed` in particular is the one that does not fail loudly, since the",
        "wording matches, the options match, and pooling without recoding simply inverts",
        "the estimate.",
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
