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


def shorten(texts: list[str]) -> tuple[list[str], list[str]]:
    """Label a battery by the clause that differs, not by its first 70 characters.

    Ten of these questions open with the same twelve words and close with the same
    five, so a truncated label prints ten identical rows. Where several questions
    share a long opening, the shared stem is hoisted out and returned as a note; each
    row then carries only the words that distinguish it. Questions that share nothing
    keep their own wording.
    """
    stems: dict[tuple[str, ...], list[int]] = {}
    for i, text in enumerate(texts):
        key = tuple(w.lower() for w in text.split()[:4])
        stems.setdefault(key, []).append(i)

    labels = list(texts)
    notes: list[str] = []
    for members in stems.values():
        if len(members) < 2:
            continue
        family = [texts[i] for i in members]
        lead, tail = _runs(family)
        if lead < 4:
            continue
        words = family[0].split()
        stem = " ".join(words[:lead])
        close = " ".join(words[len(words) - tail:]) if tail else ""
        for i, text in zip(members, family):
            middle = text.split()[lead : len(text.split()) - tail or None]
            clause = " ".join(middle) or text
            labels[i] = clause[0].upper() + clause[1:]
        notes.append(
            f"{len(members)} rows share the stem “{stem} … {close}”" if close
            else f"{len(members)} rows share the stem “{stem} …”"
        )
    return labels, notes


def clip(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1].rstrip() + "…"


def header(fig, title: str, lines: list[str]) -> float:
    """Title and standfirst at fixed inch offsets from the top edge.

    These figures vary in height with their row count, so a header placed in figure
    fractions crowds on the tall ones and floats on the short ones. Returns the
    fraction the plotting area should stop at.
    """
    inches = fig.get_figheight()
    fig.suptitle(title, x=0.012, y=1 - 0.28 / inches, ha="left", va="top",
                 fontsize=15, fontweight="bold", color=INK)
    offset = 0.62
    for i, line in enumerate(lines):
        fig.text(0.012, 1 - offset / inches, line, ha="left", va="top",
                 fontsize=9.6 if i == 0 else 8.6, color=INK_SOFT if i == 0 else INK_FAINT)
        offset += 0.26 if i == 0 else 0.21
    return 1 - (offset + 0.12) / inches


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
    labels, notes = shorten([tidy(q) for q in order["question"]])

    height = max(4.5, 0.44 * len(order) + 3)
    fig, ax = plt.subplots(figsize=(13.5, height), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    present, ticks = set(), []
    for i, (cluster, meta) in enumerate(order.iterrows()):
        y = len(order) - i
        members = rows[rows["cluster"] == cluster]
        years = sorted({year_of(surveys[s]) for s in members["survey"]})
        ax.plot([min(years), max(years)], [y, y], color=GRID, lw=1.4, zorder=1)
        for survey in members["survey"]:
            series = surveys[survey]["series"]
            present.add(series)
            ax.scatter(
                year_of(surveys[survey]), y, s=64, zorder=3,
                color=SERIES_COLOUR[series], edgecolor=SURFACE, linewidth=1.2,
            )
        ticks.append((y, clip(labels[i], 64), int(meta["n"]), meta["scale"]))

    span = sorted({year_of(surveys[s]) for s in rows["survey"]})
    first, last = min(span), max(span)
    ax.set_xlim(first - 0.9, last + 0.9)
    ax.set_xticks([y for y in range(first, last + 1) if y % 2 == first % 2])
    ax.set_ylim(0.3, len(order) + 0.7)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)

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
        "that can be built; the archive has no run that changes colour."
    ]
    if notes:
        lines.append("Rows carry the clause that differs, not the first words of the question:")
        lines += [f"    · {note}" for note in notes]
    top = header(fig, "Inequality questions asked in more than two surveys", lines)
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-coverage.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"coverage: {len(order)} questions")


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


def distribution_figure(rows: pd.DataFrame, surveys: dict) -> None:
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
    if not panels:
        print("distributions: nothing with an identical scale")
        return

    labels, notes = shorten([tidy(q) for _, q, _, _ in panels])
    reversed_any = False

    cols = 3
    grid_rows = int(np.ceil(len(panels) / cols))
    fig, axes = plt.subplots(grid_rows, cols, figsize=(15.5, 3.75 * grid_rows), facecolor=SURFACE)
    axes = np.atleast_1d(axes).ravel()

    for panel, (_, _, points, scale) in enumerate(panels):
        ax = axes[panel]
        ax.set_facecolor(SURFACE)
        codes, flipped = orient(scale)
        reversed_any |= flipped
        colours = [
            DIVERGING[i] if len(codes) == 4
            else LinearSegmentedColormap.from_list("d", DIVERGING)(i / max(len(codes) - 1, 1))
            for i in range(len(codes))
        ]

        years = [p[0] for p in points]
        bottom = np.zeros(len(points))
        for i, code in enumerate(codes):
            values = np.array([p[1][code] for p in points])
            ax.bar(years, values, bottom=bottom, width=0.82, color=colours[i],
                   edgecolor=SURFACE, linewidth=1.2, label=clip(scale[code], 30))
            bottom += values

        ax.set_xticks(years)
        ax.set_xticklabels(years, rotation=45, ha="right", fontsize=7.6)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["0%", "50%", "100%"], fontsize=7.6)
        frame_style(ax)
        ax.set_title(clip(labels[panel], 66), fontsize=8.8, color=INK, loc="left", pad=6)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=2, frameon=False,
                  fontsize=7.2, labelcolor=INK_SOFT, handlelength=1.1, handleheight=1.1,
                  columnspacing=1.1, borderpad=0)

    for ax in axes[len(panels):]:
        ax.axis("off")

    lines = [
        "Weighted shares of substantive answers; don't-know and refused are dropped rather than counted. Stacked "
        "proportions, not densities — these are four-point ordinal items, and a smoothed curve would invent shape "
        "between points that do not exist.",
        "Each panel carries its own scale: the releases do not share one, and they do not all run the same way. "
        "Bars read affirmative (dark blue) to negative (dark red) in every panel"
        + (", which reverses the code order of the Afrobarometer items." if reversed_any else "."),
    ]
    if notes:
        lines += [f"    · {note}" for note in notes]
    top = header(fig, "How Tunisians answered the recurring inequality questions", lines)
    fig.tight_layout(rect=(0, 0, 1, top), h_pad=3.4)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-distributions.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"distributions: {len(panels)} questions")


def correlation_figure(surveys: dict) -> None:
    topic = pd.read_csv(TOPIC)
    counts = topic["survey"].value_counts()
    key = counts.index[0]
    survey = surveys[key]
    items = topic[topic["survey"] == key]

    scales = {v: substantive(survey, v) for v in items["variable"]}
    ordinal = {
        v: s for v, s in scales.items() if s and 3 <= len(s) <= 7
    }  # a rank correlation wants an ordered scale, not a nominal list
    if len(ordinal) < 3:
        print("correlations: too few ordinal items")
        return

    data = load(survey, list(ordinal))
    frame = pd.DataFrame(
        {v: data[v].where(data[v].isin(scales[v].keys())) for v in ordinal if v in data}
    )
    frame = frame.loc[:, frame.notna().sum() >= 100]
    matrix = frame.corr(method="spearman", min_periods=100)

    grid = matrix.to_numpy(dtype=float).copy()
    np.fill_diagonal(grid, np.nan)
    finite = grid[np.isfinite(grid)]
    unmeasured = int(np.isnan(grid).sum() - len(grid))

    # A correlation runs to ±1, but nothing here comes near it: drawn on the full range
    # every cell washes to white and the figure says nothing. The scale is set to the
    # strongest pair present, symmetrically, and the limit is stated on the bar.
    limit = max(0.2, float(np.ceil(np.abs(finite).max() * 10) / 10))

    labels = []
    for v in matrix.columns:
        text = tidy(items.loc[items["variable"] == v, "question_text"].iloc[0])
        labels.append(f"{v} · {clip(text, 52)}")

    size = max(7.5, 0.52 * len(matrix) + 3)
    fig, ax = plt.subplots(figsize=(size + 4.5, size), facecolor=SURFACE)
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
            ax.text(j, i, text.replace("-.", "−."), ha="center", va="center", fontsize=6.6,
                    color="#ffffff" if abs(value) > 0.62 * limit else INK_SOFT)

    ax.set_xticks(range(len(matrix)))
    ax.set_yticks(range(len(matrix)))
    ax.set_xticklabels(matrix.columns, rotation=90, fontsize=7.4, color=INK_SOFT)
    ax.set_yticklabels(labels, fontsize=7.4, color=INK)
    ax.set_xticks(np.arange(len(matrix) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(matrix) + 1) - 0.5, minor=True)
    ax.grid(which="minor", color=SURFACE, lw=1.4)
    ax.tick_params(which="both", length=0)
    for side in ax.spines.values():
        side.set_visible(False)

    bar = fig.colorbar(image, ax=ax, shrink=0.5, pad=0.02, ticks=[-limit, 0, limit])
    bar.set_label(f"Spearman ρ (scale ends at ±{limit:g}, the strongest pair here)",
                  fontsize=8.4, color=INK_SOFT)
    bar.ax.tick_params(labelsize=8, colors=INK_SOFT)
    bar.outline.set_visible(False)

    strongest = matrix.where(~np.eye(len(matrix), dtype=bool)).stack().idxmax()
    peak = matrix.loc[strongest]
    label = f"{SHORT[survey['series']]} {survey['wave_label']}"
    lines = [
        f"Spearman rank correlations among {len(matrix)} ordinal inequality items, "
        f"{survey['n_respondents']:,} respondents, don't-know and refused set missing. Within one survey "
        "only: other surveys are other people, so there is no cross-survey correlation to compute.",
        f"Almost nothing here moves together — the strongest pair, {strongest[0]} and {strongest[1]}, "
        f"reaches ρ = {peak:.2f}, and most cells sit inside ±0.1. Grey on the diagonal is a variable "
        "against itself"
        + (f"; the {unmeasured // 2} hatched pairs were never put to the same respondents, "
           "which is not the same as no relationship." if unmeasured else "."),
    ]
    top = header(fig, f"Inequality items barely move together — {label}", lines)
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-correlations.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"correlations: {len(matrix)} items from {key}, peak {peak:.2f}, {unmeasured // 2} blank pairs")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    surveys = catalog()
    rows = recurring()
    coverage_figure(rows, surveys)
    distribution_figure(rows, surveys)
    correlation_figure(surveys)


if __name__ == "__main__":
    main()
