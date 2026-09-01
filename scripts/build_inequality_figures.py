#!/usr/bin/env python3
"""Figures for the inequality questions: coverage, distributions, correlations.

Three things, each with a limit worth stating before it is read.

**Coverage** — every inequality question asked in more than two surveys, and the
years it was asked in. This is the answer to what can actually be followed over
time, and it is drawn from the concordance, so a row is a question rather than a
variable name.

**Distributions** — how Tunisians answered, for the questions that recur with an
identical response scale. Drawn as stacked proportions, not densities: these are
four- and five-point ordinal items, and a smoothed density over four categories
invents shape between points that do not exist. Weighted by each survey's own design
weight, with don't-know and refused removed rather than counted as an answer.

**Correlations** — Spearman rank correlations among the inequality items of a single
survey. Only within one survey: different surveys are different respondents, so
there is no cross-survey correlation to compute and a matrix spanning them would be
an artefact of the layout rather than a finding.
"""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat
from matplotlib.colors import LinearSegmentedColormap

from build_question_concordance import substantive_scale
from extract_tunisia import ROOT

FIGURES = ROOT / "main" / "figures"
TOPIC = ROOT / "docs" / "topics" / "inequality.csv"

SERIES_COLOUR = {
    "arab-barometer": "#2a78d6",
    "world-values-survey": "#eb6834",
    "afrobarometer": "#1baf7a",
    "arab-opinion-index": "#4a3aa7",
}
SHORT = {
    "arab-barometer": "AB",
    "world-values-survey": "WVS",
    "afrobarometer": "Afro",
    "arab-opinion-index": "AOI",
}
INK, INK_SOFT, INK_FAINT = "#0b0b0b", "#52514e", "#8a8984"
SURFACE, GRID = "#fcfcfb", "#e4e3df"

WEIGHTS = ("wt", "WT", "W_WEIGHT", "withinwt", "withinwt_hh", "Weight")


def catalog() -> dict[str, dict]:
    data = json.loads((ROOT / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    return {s["key"]: s for s in data["surveys"]}


def year_of(survey: dict) -> int:
    window = survey.get("fieldwork_tunisia") or str(survey["fieldwork_years_series"])
    return int(re.findall(r"\d{4}", window)[0])


def tidy(text: str) -> str:
    text = re.sub(r"^\s*[A-Za-z]{0,6}[\d_]+[A-Za-z0-9_]*[.:]?\s*", "", str(text))
    return re.sub(r"\s+", " ", text).strip()


def load(survey: dict, columns: list[str]) -> pd.DataFrame:
    path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
    frame, _ = pyreadstat.read_sav(str(path), user_missing=True)
    keep = [c for c in columns if c in frame.columns]
    weight = next((w for w in WEIGHTS if w in frame.columns), None)
    out = frame[keep].copy()
    out["_w"] = frame[weight] if weight else 1.0
    return out


def substantive(survey: dict, variable: str) -> dict | None:
    codebook = json.loads(
        (ROOT / survey["path"] / "codebook.json").read_text(encoding="utf-8")
    )
    for row in codebook:
        if row["variable"].upper() == variable.upper():
            return substantive_scale(row["value_labels"])
    return None


def recurring(minimum: int = 3) -> pd.DataFrame:
    """Inequality questions asked in more than two surveys."""
    topic = pd.read_csv(TOPIC)
    groups = pd.read_csv(ROOT / "docs" / "question-concordance-groups.csv").set_index("cluster")
    members = pd.read_csv(ROOT / "docs" / "question-concordance.csv")
    wanted = set(topic.loc[topic["concordance_group"] != "", "concordance_group"])
    rows = members[members["cluster"].isin(wanted)].copy()
    counts = rows.groupby("cluster")["survey"].nunique()
    rows = rows[rows["cluster"].isin(counts[counts >= minimum].index)]
    rows["scale"] = rows["cluster"].map(groups["scale"])
    rows["question"] = rows["cluster"].map(groups["question_text"])
    return rows


def _runs(texts: list[str]) -> tuple[int, int]:
    """Words shared at the start and at the end of every text, case-insensitively."""
    words = [t.split() for t in texts]
    shortest = min(len(w) for w in words)
    lead = 0
    while lead < shortest and len({w[lead].lower() for w in words}) == 1:
        lead += 1
    tail = 0
    while tail < shortest - lead and len({w[-1 - tail].lower() for w in words}) == 1:
        tail += 1
    return lead, tail


# Phrases that ask a question without saying what it is about. Only these come off
# the front of a shared stem; whatever follows is the subject and has to survive.
BOILERPLATE = (
    "to what extent do you believe that the",
    "to what extent do you believe that",
    "to what extent do you think that the",
    "to what extent do you think that",
    "please indicate your level of personal agreement/disagreement with each of this",
    "please indicate your level of personal agreement/disagreement with each of these",
    "do you think the availability of",
    "how would you evaluate the",
)


def strip_boilerplate(stem: str) -> str:
    low = stem.lower()
    for phrase in sorted(BOILERPLATE, key=len, reverse=True):
        if low.startswith(phrase):
            return stem[len(phrase):].strip()
    return stem


class Family:
    """A battery: several questions sharing an opening, and the subject they share."""

    def __init__(self, subject: str | None, members: list[int]) -> None:
        self.subject, self.members = subject, members


def shorten(texts: list[str]) -> tuple[list[str], list[Family]]:
    """Split a battery into the subject it shares and the clause each item varies.

    Thirteen of these questions open with the same words and close with the same
    words, so a label truncated at the front prints thirteen identical rows. But the
    shared part is not boilerplate — it is the substance. ``the Equality of all
    citizens regardless of … is applied in your country`` is the entire reason these
    items belong to a page about inequality, and a row reading only ``religion`` has
    lost what was being measured.

    So the stem is not deleted, it is promoted: returned as a *subject* for the
    caller to draw as a heading over the rows it covers. Only a leading interrogative
    phrase is dropped from it. A family whose stem is nothing but boilerplate — ``please
    indicate your level of personal agreement/disagreement with each of this`` — gets
    no subject, because its items already say what they are about.
    """
    stems: dict[tuple[str, ...], list[int]] = {}
    for i, text in enumerate(texts):
        key = tuple(w.lower() for w in text.split()[:4])
        stems.setdefault(key, []).append(i)

    labels = list(texts)
    families: list[Family] = []
    for members in sorted(stems.values(), key=min):
        if len(members) < 2:
            families.append(Family(None, members))
            continue
        group = [texts[i] for i in members]
        lead, tail = _runs(group)
        if lead < 4:
            families.append(Family(None, members))
            continue
        words = group[0].split()
        stem = strip_boilerplate(" ".join(words[:lead]))
        close = " ".join(words[len(words) - tail:]) if tail else ""
        for i, text in zip(members, group):
            middle = text.split()[lead : len(text.split()) - tail or None]
            clause = " ".join(middle) or text
            labels[i] = clause[0].upper() + clause[1:]
        subject = f"{stem} … {close}".strip(" …") if (stem or close) else ""
        if subject:
            subject = subject[0].upper() + subject[1:]
        families.append(Family(subject or None, members))
    return labels, families


def clip(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1].rstrip() + "…"


def header(fig, title: str, lines: list[str]) -> float:
    """Title and standfirst at fixed inch offsets from the top edge.

    These figures vary in height with their row count, so a header placed in figure
    fractions crowds on the tall ones and floats on the short ones. Lines are wrapped
    to the figure's own width: an unwrapped one does not overflow, it drags the saved
    figure out to the width of the text, because these are saved with a tight bounding
    box. Returns the fraction the plotting area should stop at.
    """
    inches = fig.get_figheight()
    fig.suptitle(title, x=0.012, y=1 - 0.28 / inches, ha="left", va="top",
                 fontsize=15, fontweight="bold", color=INK)
    offset = 0.62
    for i, line in enumerate(lines):
        size = 9.6 if i == 0 else 8.6
        room = max(40, int(fig.get_figwidth() * 72 / (size * 0.52)))
        for piece in textwrap.wrap(line, width=room) or [""]:
            fig.text(0.012, 1 - offset / inches, piece, ha="left", va="top",
                     fontsize=size, color=INK_SOFT if i == 0 else INK_FAINT)
            offset += 0.21 if i == 0 else 0.185
        offset += 0.05
    return 1 - (offset + 0.10) / inches


def frame_style(ax) -> None:
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0, colors=INK_SOFT, labelsize=8.6)


def coverage_figure(rows: pd.DataFrame, surveys: dict) -> None:
    order = (
        rows.groupby("cluster")
        .agg(n=("survey", "nunique"), question=("question", "first"), scale=("scale", "first"))
        .sort_values("n", ascending=False)
    )
    clusters = list(order.index)
    labels, families = shorten([tidy(q) for q in order["question"]])

    # A battery is drawn as a block under its own heading, so the rows stay contiguous
    # and the subject they share is on screen next to them.
    families.sort(key=lambda f: -max(order["n"].iloc[i] for i in f.members))
    entries: list[tuple] = []
    for family in families:
        members = sorted(family.members, key=lambda i: -order["n"].iloc[i])
        if family.subject:
            entries.append(("head", family.subject, len(members)))
        for i in members:
            entries.append(("row", i))

    height = max(4.5, 0.42 * len(entries) + 3)
    fig, ax = plt.subplots(figsize=(13.5, height), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    present, ticks, heads = set(), [], []
    for position, entry in enumerate(entries):
        y = len(entries) - position
        if entry[0] == "head":
            heads.append((y, entry[1], entry[2]))
            continue
        i = entry[1]
        cluster, meta = clusters[i], order.iloc[i]
        members = rows[rows["cluster"] == cluster]
        years = sorted({year_of(surveys[s]) for s in members["survey"]})
        ax.plot([min(years), max(years)], [y, y], color=GRID, lw=1.4, zorder=2)
        for survey in members["survey"]:
            series = surveys[survey]["series"]
            present.add(series)
            ax.scatter(year_of(surveys[survey]), y, s=64, zorder=3,
                       color=SERIES_COLOUR[series], edgecolor=SURFACE, linewidth=1.2)
        ticks.append((y, clip(labels[i], 60), int(meta["n"]), meta["scale"]))

    span = sorted({year_of(surveys[s]) for s in rows["survey"]})
    first, last = min(span), max(span)
    ax.set_xlim(first - 0.9, last + 0.9)
    ax.set_xticks([y for y in range(first, last + 1) if y % 2 == first % 2])
    ax.set_ylim(0.3, len(entries) + 0.9)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)

    for y, subject, count in heads:
        ax.axhspan(y - count - 0.5, y + 0.45, color="#f3f2ef", zorder=0, lw=0)
        ax.text(-0.012, y - 0.15, subject, transform=ax.get_yaxis_transform(), ha="right",
                va="center", fontsize=8.8, fontweight="bold", color=INK)
        ax.text(1.012, y - 0.15, f"{count} items", transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=8, color=INK_FAINT)

    ax.set_yticks([y for y, *_ in ticks])
    ax.set_yticklabels([t for _, t, *_ in ticks], fontsize=8.6, color=INK)
    for y, _, n, scale in ticks:
        ax.text(1.012, y, f"{n} surveys · {scale}", transform=ax.get_yaxis_transform(),
                va="center", fontsize=8, color=INK_SOFT if scale == "identical" else INK_FAINT)

    handles = [
        plt.Line2D([], [], marker="o", ls="", color=SERIES_COLOUR[s], label=SHORT[s], markersize=7)
        for s in SERIES_COLOUR
        if s in present
    ]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.004), ncol=len(handles),
              frameon=False, fontsize=8.8, labelcolor=INK_SOFT)

    lines = [
        f"{len(order)} questions, and the years each was asked. A run of dots in one colour is a series "
        "that can be built; the archive has no run that changes colour.",
        "A shaded block is one battery: the heading carries the wording its items share, and each row "
        "beneath it carries only the clause that varies.",
    ]
    top = header(fig, "Inequality questions asked in more than two surveys", lines)
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-coverage.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"coverage: {len(order)} questions, {sum(1 for f in families if f.subject)} batteries")


POSITIVE = {"good", "well", "applied", "agree", "satisfied", "fair", "equal", "always", "often"}
NEGATIVE = {"bad", "badly", "poor", "disagree", "unequal", "never", "rarely", "not", "no", "none"}

# Two poles per arm, blue to red. Validated on the light surface: worst adjacent CVD
# ΔE 18.4 (protan), normal-vision 24.4, chroma floor clear. The two middle steps sit
# under 3:1 against the surface, so every panel carries its own labelled scale.
DIVERGING = ("#104281", "#5598e7", "#f2896f", "#ab2f2e")


def polarity(label: str) -> int:
    words = set(re.findall(r"[a-z]+", label.lower()))
    return len(words & POSITIVE) - len(words & NEGATIVE)


def orient(scale: dict) -> tuple[list, bool]:
    """Codes ordered affirmative pole first, whichever way the release numbered them.

    The scales here do not agree on direction: the Arab Opinion Index codes ``applied
    completely`` as 1, while Afrobarometer codes ``very badly`` as 1. Colouring by code
    order would paint one panel's best answer the same shade as another's worst. Falls
    back to code order when the two ends score alike, which is the ambiguous case.
    """
    codes = sorted(scale)
    first, last = polarity(scale[codes[0]]), polarity(scale[codes[-1]])
    return (codes[::-1], True) if last > first else (codes, False)


def panel_data(rows: pd.DataFrame, cluster: str, surveys: dict) -> tuple | None:
    members = rows[rows["cluster"] == cluster]
    points, scale = [], None
    for _, member in members.iterrows():
        survey = surveys[member["survey"]]
        scale = scale or substantive(survey, member["variable"])
        if not scale:
            continue
        data = load(survey, [member["variable"]])
        if member["variable"] not in data:
            continue
        values = data[member["variable"]]
        keep = values.isin(scale.keys())
        values, weights = values[keep], data["_w"][keep]
        if values.empty:
            continue
        total = weights.sum()
        points.append(
            (year_of(survey), {code: weights[values == code].sum() / total for code in scale})
        )
    if not points or not scale:
        return None
    points.sort()
    return points, scale


def built_panels(rows: pd.DataFrame, surveys: dict) -> list[tuple]:
    usable = rows[rows["scale"] == "identical"]
    order = (
        usable.groupby("cluster")
        .agg(n=("survey", "nunique"), question=("question", "first"))
        .sort_values("n", ascending=False)
        .head(12)
    )
    panels = []
    for cluster, meta in order.iterrows():
        built = panel_data(rows, cluster, surveys)
        if built:
            panels.append((cluster, meta["question"], *built))
    return panels


def panel_grid(panels: list, per_panel: float) -> tuple:
    cols = 3
    grid_rows = int(np.ceil(len(panels) / cols))
    fig, axes = plt.subplots(grid_rows, cols, figsize=(15.5, per_panel * grid_rows),
                             facecolor=SURFACE)
    return fig, np.atleast_1d(axes).ravel()


def titles(panels: list) -> tuple[list[str], dict[int, str]]:
    labels, families = shorten([tidy(q) for _, q, _, _ in panels])
    return labels, {i: f.subject for f in families for i in f.members if f.subject}


def label_panel(ax, label: str, subject: str | None) -> None:
    ax.set_title(clip(label, 62), fontsize=8.8, color=INK, loc="left",
                 pad=20 if subject else 6)
    if subject:
        # Without this line the panel is titled "Religion", and nothing on it says
        # what was asked about religion.
        ax.text(0, 1.055, clip(subject, 74), transform=ax.transAxes, ha="left",
                va="bottom", fontsize=7.6, color=INK_SOFT)


def distribution_figure(rows: pd.DataFrame, surveys: dict) -> None:
    """The full distribution, diverging from a zero baseline rather than stacked to 100%.

    A 100%-stacked bar gives a common baseline to exactly two things: the bottom
    segment and the total. Every middle category floats on the one below it, so
    ``applied to some extent`` cannot be read across years — both its ends move — and
    that comparison is the whole point of a battery asked eight times.

    Splitting the scale at its midpoint and running the affirmative half up from zero
    and the negative half down gives *each pole* a common baseline. Nothing is
    aggregated away: all four categories are still drawn, at their real shares.
    """
    panels = built_panels(rows, surveys)
    if not panels:
        print("distributions: nothing with an identical scale")
        return
    labels, subject_of = titles(panels)
    reversed_any = False

    fig, axes = panel_grid(panels, 3.75)
    for panel, (_, _, points, scale) in enumerate(panels):
        ax = axes[panel]
        ax.set_facecolor(SURFACE)
        codes, flipped = orient(scale)
        reversed_any |= flipped
        half = len(codes) // 2
        positive, negative = codes[:half][::-1], codes[half + len(codes) % 2:]
        middle = codes[half] if len(codes) % 2 else None
        years = [p[0] for p in points]

        colours = {c: DIVERGING[i] if len(codes) == 4 else
                   LinearSegmentedColormap.from_list("d", DIVERGING)(i / max(len(codes) - 1, 1))
                   for i, c in enumerate(codes)}

        # A middle category belongs to neither pole, so it straddles the baseline.
        base_up = np.zeros(len(points))
        base_down = np.zeros(len(points))
        if middle is not None:
            share = np.array([p[1][middle] for p in points]) / 2
            ax.bar(years, share, bottom=0, width=0.82, color="#dedcd6",
                   edgecolor=SURFACE, linewidth=1.2, label=clip(scale[middle], 30))
            ax.bar(years, -share, bottom=0, width=0.82, color="#dedcd6",
                   edgecolor=SURFACE, linewidth=1.2)
            base_up, base_down = share, -share

        for code in positive:
            share = np.array([p[1][code] for p in points])
            ax.bar(years, share, bottom=base_up, width=0.82, color=colours[code],
                   edgecolor=SURFACE, linewidth=1.2, label=clip(scale[code], 30))
            base_up = base_up + share
        for code in negative:
            share = np.array([p[1][code] for p in points])
            ax.bar(years, -share, bottom=base_down, width=0.82, color=colours[code],
                   edgecolor=SURFACE, linewidth=1.2, label=clip(scale[code], 30))
            base_down = base_down - share

        ax.axhline(0, color=INK_SOFT, lw=0.9, zorder=4)
        ax.set_xticks(years)
        ax.set_xticklabels(years, rotation=45, ha="right", fontsize=7.6)
        ax.set_ylim(-1, 1)
        ax.set_yticks([-1, -0.5, 0, 0.5, 1])
        ax.set_yticklabels(["100%", "50%", "0", "50%", "100%"], fontsize=7.6)
        ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
        frame_style(ax)
        ax.spines["bottom"].set_visible(False)
        handles, names = ax.get_legend_handles_labels()
        seen = dict(zip(names, handles))
        ax.legend(seen.values(), seen.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.30),
                  ncol=2, frameon=False, fontsize=7.2, labelcolor=INK_SOFT,
                  handlelength=1.1, handleheight=1.1, columnspacing=1.1, borderpad=0)
        label_panel(ax, labels[panel], subject_of.get(panel))

    for ax in axes[len(panels):]:
        ax.axis("off")

    lines = [
        "Weighted shares of substantive answers; don't-know and refused are dropped rather than counted. "
        "Bars diverge from zero rather than stacking to 100%, so each pole keeps a common baseline and a "
        "middle category can be read across years instead of floating on the one below it.",
        "Each panel carries its own scale: the releases do not share one, and they do not all run the same "
        "way. Affirmative answers run up in blue and negative answers down in red in every panel"
        + (", which reverses the code order of the Afrobarometer items." if reversed_any else "."),
    ]
    if subject_of:
        lines.append("A panel whose title is a bare category carries the wording it shares with the rest of "
                     "its battery on the line above it.")
    top = header(fig, "How Tunisians answered the recurring inequality questions", lines)
    fig.tight_layout(rect=(0, 0, 1, top), h_pad=3.4)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-distributions.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"distributions: {len(panels)} questions, diverging")


def trend_figure(rows: pd.DataFrame, surveys: dict) -> None:
    """The affirmative share over time, one line per question against its siblings.

    The bars answer "what did the distribution look like"; they are a poor way to
    answer "did it move", because that means tracking a band whose ends both shift.
    A single share on a common baseline answers it directly, and drawing the rest of
    the battery behind each panel in grey turns "did it move" into "did it move
    differently from its siblings", which is the question a battery is for.

    The cost is stated rather than hidden: collapsing four categories into two
    discards how strongly people answered, so this figure sits beside the
    distributions rather than replacing them.
    """
    panels = built_panels(rows, surveys)
    if not panels:
        return
    labels, subject_of = titles(panels)

    series, groups = [], {}
    for panel, (_, _, points, scale) in enumerate(panels):
        codes, _ = orient(scale)
        half = len(codes) // 2
        affirmative = codes[:half]
        xs = [p[0] for p in points]
        ys = [sum(p[1][c] for c in affirmative) for p in points]
        series.append((xs, ys))
        groups.setdefault(tuple(scale.values()), []).append(panel)

    fig, axes = panel_grid(panels, 2.95)
    for panel, _ in enumerate(panels):
        ax = axes[panel]
        ax.set_facecolor(SURFACE)
        siblings = next(g for g in groups.values() if panel in g)
        for other in siblings:
            if other != panel:
                ax.plot(*series[other], color="#dcdbd6", lw=1.4, zorder=1)
        xs, ys = series[panel]
        ax.plot(xs, ys, color="#2a78d6", lw=2, zorder=3)
        ax.plot(xs, ys, "o", color="#2a78d6", ms=5, mec=SURFACE, mew=1.2, zorder=4)
        for x, y in ((xs[0], ys[0]), (xs[-1], ys[-1])):
            ax.annotate(f"{y:.0%}", (x, y), textcoords="offset points", xytext=(0, 9),
                        ha="center", fontsize=7.6, color=INK, fontweight="bold")

        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_yticklabels(["0", "", "50%", "", "100%"], fontsize=7.6)
        ax.set_xticks(xs)
        ax.set_xticklabels(xs, rotation=45, ha="right", fontsize=7.6)
        ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
        frame_style(ax)
        label_panel(ax, labels[panel], subject_of.get(panel))

    for ax in axes[len(panels):]:
        ax.axis("off")

    lines = [
        "The share giving either affirmative answer — weighted, don't-know and refused dropped. One common "
        "baseline, so the movement is readable; the grey lines behind each panel are the other questions "
        "sharing its response scale, which is what makes a panel's own line worth reading.",
        "This collapses four categories into two and so discards how strongly people answered: read it with "
        "the distributions, not instead of them. Each point is a separate cross-section, not a panel of the "
        "same respondents, and the line between two points is drawn to be followed, not measured.",
    ]
    top = header(fig, "Whether Tunisians think equality is applied, over time", lines)
    fig.tight_layout(rect=(0, 0, 1, top), h_pad=2.6)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-trends.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"trends: {len(panels)} questions in {len(groups)} scale groups")


def battery_of(variable: str) -> str:
    """The battery a variable belongs to, from its name: Q422_1 and Q422_2 are one item."""
    match = re.match(r"([A-Za-z]+\d+)", variable)
    return match.group(1) if match else variable


def eligible(survey: dict, topic: pd.DataFrame) -> list[str]:
    """Inequality items of a survey that can enter a rank correlation, from the codebook.

    Read from ``codebook.json`` rather than the data so every survey can be weighed
    without loading them all. An item qualifies if it has an ordered scale of three to
    seven substantive answers and enough respondents to correlate.
    """
    wanted = set(topic.loc[topic["survey"] == survey["key"], "variable"].str.upper())
    rows = json.loads((ROOT / survey["path"] / "codebook.json").read_text(encoding="utf-8"))
    out = []
    for row in rows:
        if row["variable"].upper() not in wanted or row["n_valid"] < 100:
            continue
        scale = substantive_scale(row["value_labels"])
        if scale and 3 <= len(scale) <= 7:
            out.append(row["variable"])
    return out


def correlation_target(surveys: dict) -> tuple[dict, list[str]]:
    """The survey whose inequality items can actually support the most comparisons.

    Not the survey with the most rows in the topic table. Arab Barometer Wave VIII
    tops that count with 43, but 28 of them are one multi-response question exploded
    into ``Q884A_*``/``Q884B_*`` dummy columns — a tally of columns, not of questions.
    Counting only the items eligible for the matrix ranks by what the figure can
    actually show.
    """
    topic = pd.read_csv(TOPIC)
    ranked = sorted(
        ((survey, eligible(survey, topic)) for survey in surveys.values()),
        key=lambda pair: (-len(pair[1]), pair[0]["key"]),
    )
    return ranked[0]


def correlation_figure(surveys: dict) -> None:
    """Whether perceived inequality is one attitude or several.

    A correlation matrix over an arbitrary handful of a survey's items answers a
    question about the questionnaire — do neighbouring items in a battery move
    together — and not one about inequality. Grouped by battery, it answers the
    question worth asking of an inequality page: does someone who sees inequality on
    one dimension see it on the others?
    """
    topic = pd.read_csv(TOPIC)
    survey, items = correlation_target(surveys)
    key = survey["key"]
    text_of = topic[topic["survey"] == key].set_index("variable")["question_text"]

    scales = {v: substantive(survey, v) for v in items}
    data = load(survey, items)
    frame = pd.DataFrame(
        {v: data[v].where(data[v].isin(scales[v].keys())) for v in items if v in data}
    )
    frame = frame.loc[:, frame.notna().sum() >= 100]
    if frame.shape[1] < 3:
        print("correlations: too few ordinal items")
        return

    # Group the matrix by battery, so within-battery blocks are visibly separate from
    # the cross-battery cells that carry the actual finding.
    batteries: dict[str, list[str]] = {}
    for v in frame.columns:
        batteries.setdefault(battery_of(v), []).append(v)
    blocks = sorted(batteries.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    columns = [v for _, members in blocks for v in members]
    frame = frame[columns]
    matrix = frame.corr(method="spearman", min_periods=100)

    labels, headings, edges = [], [], []
    at = 0
    for name, members in blocks:
        clauses, families = shorten([tidy(text_of[v]) for v in members])
        subject = families[0].subject if len(families) == 1 else None
        headings.append((at, at + len(members), name, subject))
        edges.append(at + len(members))
        labels += [f"{v} · {clip(c, 44)}" for v, c in zip(members, clauses)]
        at += len(members)

    grid = matrix.to_numpy(dtype=float).copy()
    np.fill_diagonal(grid, np.nan)
    finite = grid[np.isfinite(grid)]
    unmeasured = int(np.isnan(grid).sum() - len(grid))
    limit = max(0.2, float(np.ceil(np.abs(finite).max() * 10) / 10))

    same = np.zeros_like(grid, dtype=bool)
    for lo, hi, _, _ in headings:
        same[lo:hi, lo:hi] = True
    np.fill_diagonal(same, False)
    within = np.abs(grid[same & np.isfinite(grid)])
    between = np.abs(grid[~same & np.isfinite(grid)])

    size = max(8.0, 0.46 * len(matrix) + 3)
    fig, ax = plt.subplots(figsize=(size + 3.4, size), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    diverging = LinearSegmentedColormap.from_list(
        "diverging", ["#104281", "#5598e7", "#f4f3f0", "#f2896f", "#ab2f2e"]
    )
    diverging.set_bad("#f0efec")
    image = ax.imshow(grid, cmap=diverging, vmin=-limit, vmax=limit)

    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i == j:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color="#c9c8c3", lw=0))
                continue
            value = grid[i, j]
            if not np.isfinite(value):
                # Hatched, not pale: a pair never put to the same respondents must not
                # look like a pair that was asked and came back uncorrelated.
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="#f0efec",
                                           hatch="////", edgecolor="#c2c1bc", lw=0))
                continue
            text = f"{abs(value):.2f}"[1:] if abs(value) < 0.005 else f"{value:.2f}".replace("0.", ".")
            ax.text(j, i, text.replace("-.", "−."), ha="center", va="center", fontsize=6.4,
                    color="#ffffff" if abs(value) > 0.62 * limit else INK_SOFT)

    for edge in edges[:-1]:
        ax.axhline(edge - 0.5, color=INK, lw=1.6)
        ax.axvline(edge - 0.5, color=INK, lw=1.6)

    for lo, hi, name, subject in headings:
        middle = (lo + hi - 1) / 2
        ax.plot([-0.30, -0.30], [lo - 0.4, hi - 0.6], transform=ax.get_yaxis_transform(),
                color=INK_FAINT, lw=1.2, clip_on=False)
        # Rotated text is bounded by the block's height, and a three-row block has no
        # room for a question. The codes go here; their wording goes in the key above.
        ax.text(-0.315, middle, name, transform=ax.get_yaxis_transform(), rotation=90,
                ha="right", va="center", fontsize=8.6, fontweight="bold", color=INK)

    ax.set_xticks(range(len(matrix)))
    ax.set_yticks(range(len(matrix)))
    ax.set_xticklabels(matrix.columns, rotation=90, fontsize=7.2, color=INK_SOFT)
    ax.set_yticklabels(labels, fontsize=7.2, color=INK)
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)

    bar = fig.colorbar(image, ax=ax, shrink=0.42, pad=0.015, fraction=0.028,
                       ticks=[-limit, 0, limit])
    bar.set_label(f"Spearman ρ (scale ends at ±{limit:g}, the strongest pair here)",
                  fontsize=8.4, color=INK_SOFT)
    bar.ax.tick_params(labelsize=8, colors=INK_SOFT)
    bar.outline.set_visible(False)

    label = f"{SHORT[survey['series']]} {survey['wave_label']}"
    lines = [
        f"Spearman rank correlations among {len(matrix)} ordinal inequality items, "
        f"{survey['n_respondents']:,} respondents, don't-know and refused set missing. Within one survey "
        "only: other surveys are other people, so there is no cross-survey correlation to compute.",
        f"Inside a battery the mean |ρ| is {within.mean():.2f}; between batteries it is {between.mean():.2f}. "
        "Someone who thinks equality is not applied on one dimension is only weakly more likely to think so "
        "on another — even where two batteries measure the same thing, and the strongest pair spanning two "
        f"of them reaches only {between.max():.2f}. Part of the within-battery figure is question order and "
        "response set rather than agreement, which is why the blocks are drawn apart.",
        "Grey on the diagonal is a variable against itself"
        + (f"; the {unmeasured // 2} hatched pairs were never put to the same respondents, which is not the "
           "same as no relationship." if unmeasured else "."),
    ]
    battery_key = [f"{n} — {clip(sub, 58)}" for _, _, n, sub in headings if sub]
    if battery_key:
        width = int(fig.get_figwidth() * 72 / (8.6 * 0.56))
        lines += textwrap.wrap("Batteries:  " + "   ·   ".join(battery_key), width=width,
                               subsequent_indent="    ")
    top = header(fig, f"Perceived inequality is not one attitude — {label}", lines)
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-correlations.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"correlations: {len(matrix)} items from {key} in {len(blocks)} batteries, "
          f"within {within.mean():.2f} vs between {between.mean():.2f}")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    surveys = catalog()
    rows = recurring()
    coverage_figure(rows, surveys)
    distribution_figure(rows, surveys)
    trend_figure(rows, surveys)
    correlation_figure(surveys)


if __name__ == "__main__":
    main()
