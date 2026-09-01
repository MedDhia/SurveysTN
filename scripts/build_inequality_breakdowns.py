#!/usr/bin/env python3
"""Who says inequality, and where — the inequality questions cut by respondent.

The figures in ``build_inequality_figures.py`` treat a question as the unit: which
recur, how they moved, how they were answered, whether they hang together. These
four take the respondent as the unit instead, and one steps back to the archive.

**By dimension** — pooled over eight Arab Opinion Index rounds, the share saying
equality is applied, ranked, with confidence intervals. The ordering is the finding.

**By region** — the same, by Tunisia's seven statistical regions. The interior and
the coast are the country's central material cleavage, and the question is whether
perceived equality tracks it.

**By group** — by household income adequacy, education, age and sex. Three of those
four turn out to be near-nulls, which is drawn rather than dropped.

**Archive map** — every inequality variable in the archive by facet and survey, not
just the recurring ones, so a reader can see what is and is not covered.

Intervals are 95% and use Kish's effective sample size, so the weighting is paid for.
No release here carries the stratum and PSU a full design correction would want, so
they are narrower than a properly design-based interval would be.
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

from build_inequality_figures import (
    FIGURES, GRID, INK, INK_FAINT, INK_SOFT, ROOT, SHORT, SURFACE, TOPIC,
    catalog, clip, frame_style, header, year_of,
)

REGIONS = ROOT / "catalog" / "tunisia-regions.json"
PRIMARY, SECOND = "#2a78d6", "#eb6834"

# The battery is asked as "is equality applied regardless of X"; X is the dimension.
DIMENSIONS = {
    "Q422_1": "Wealth", "Q422_2": "Gender/sex", "Q422_3": "Religion",
    "Q422_4": "Social status", "Q422_5": "Cultural/ethnic/linguistic",
    "Q422_6": "Political influence", "Q422_7": "Geographic area",
    "Q422_8": "Religious sect", "Q422_9": "Tribe",
    "Q422_12": "Class of citizenship", "Q422_13": "Social background",
    "Q422_14": "Skin colour",
}
GROUPS = {
    "Q1206": ("Education", {1: "Illiterate or limited", 2: "Less than secondary",
                            3: "Secondary", 4: "Higher than secondary"}),
    "Q1211": ("Household income", {1: "Meets needs, able to save",
                                   2: "Meets needs, cannot save",
                                   3: "Does not cover needs"}),
    "Q1201": ("Age", {1: "18–24", 2: "25–34", 3: "35–44", 4: "45–54", 5: "55 or older"}),
    "Q1202": ("Sex", {1: "Male", 2: "Female"}),
}


def region_map() -> tuple[dict[str, str], set[str], dict[str, str]]:
    spec = json.loads(REGIONS.read_text(encoding="utf-8"))
    by_governorate = {
        g: name for name, block in spec["regions"].items() for g in block["governorates"]
    }
    coastal = {name for name, block in spec["regions"].items() if block["coastal"]}
    return by_governorate, coastal, spec["spelling_variants"]


def pooled() -> pd.DataFrame:
    """One row per Arab Opinion Index respondent, with the battery and the demographics.

    The 2011 round is left out: it codes location by region rather than governorate, on
    codes that the release's shared multi-country label map names for another country
    entirely. It carries none of this battery either, so nothing is lost.
    """
    by_governorate, coastal, variants = region_map()
    frames = []
    for key, survey in catalog().items():
        if survey["series"] != "arab-opinion-index" or key == "aoi-2011":
            continue
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, meta = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        if "Q3" not in upper or "WEIGHT" not in upper:
            continue

        governorate = data[upper["Q3"]].map(meta.variable_value_labels.get(upper["Q3"], {}))
        governorate = governorate.astype("string").str.strip()
        governorate = governorate.replace(variants)
        block = pd.DataFrame({
            "survey": key,
            "year": year_of(survey),
            "weight": data[upper["WEIGHT"]],
            "governorate": governorate,
            "region": governorate.map(by_governorate),
        })
        block["coastal"] = block["region"].isin(coastal).where(block["region"].notna())
        for variable, (name, _) in GROUPS.items():
            block[name] = data[upper[variable]] if variable in upper else np.nan
        for variable, dimension in DIMENSIONS.items():
            if variable in upper:
                answer = data[upper[variable]]
                # 1-2 are the two affirmative answers, 3-4 the two negative ones;
                # everything else is don't-know, refused or not asked.
                block[dimension] = np.where(
                    answer.isin([1, 2]), 1.0, np.where(answer.isin([3, 4]), 0.0, np.nan)
                )
        frames.append(block)

    pool = pd.concat(frames, ignore_index=True)
    asked = [d for d in DIMENSIONS.values() if d in pool and pool[d].notna().any()]
    pool["index"] = pool[asked].mean(axis=1)
    pool.attrs["dimensions"] = asked
    return pool


def share(frame: pd.DataFrame, column: str) -> tuple[float, float, int]:
    """Weighted mean, its 95% half-width, and Kish's effective sample size.

    The spread is the weighted sample variance, not the binomial ``p(1-p)``. For a
    single yes/no dimension the two agree, but the index is a mean of eight of them and
    is far less variable than a coin at the same rate: using ``p(1-p)`` there would
    print an interval roughly twice as wide as the data warrant.
    """
    keep = frame[column].notna()
    weight, value = frame.loc[keep, "weight"], frame.loc[keep, column]
    if not len(weight) or weight.sum() <= 0:
        return np.nan, np.nan, 0
    mean = float((value * weight).sum() / weight.sum())
    variance = float((weight * (value - mean) ** 2).sum() / weight.sum())
    effective = float(weight.sum() ** 2 / (weight**2).sum())
    return mean, float(1.96 * np.sqrt(max(variance, 1e-12) / effective)), int(effective)


def dots(ax, rows: list[tuple[str, float, float, int]], colour: str = PRIMARY,
         offset: float = 0.0, label: str | None = None, annotate: bool = True) -> None:
    ys = [len(rows) - i + offset for i in range(len(rows))]
    for y, (_, mean, half, _) in zip(ys, rows):
        ax.plot([mean - half, mean + half], [y, y], color=colour, lw=2.4, solid_capstyle="round",
                alpha=0.45, zorder=2)
    ax.scatter([r[1] for r in rows], ys, s=62, color=colour, edgecolor=SURFACE, linewidth=1.2,
               zorder=3, label=label)
    if annotate:
        for y, (_, mean, _, _) in zip(ys, rows):
            ax.annotate(f"{mean:.0%}", (mean, y), textcoords="offset points", xytext=(0, 10),
                        ha="center", fontsize=8, color=INK, fontweight="bold")


def dimension_figure(pool: pd.DataFrame) -> None:
    rows = sorted(
        ((d, *share(pool, d)) for d in pool.attrs["dimensions"]),
        key=lambda r: r[1], reverse=True,
    )
    rows = [r for r in rows if r[3] >= 100]

    fig, ax = plt.subplots(figsize=(11.5, 0.46 * len(rows) + 3.4), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    dots(ax, rows)
    ax.set_yticks([len(rows) - i for i in range(len(rows))])
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.4, color=INK)
    ax.set_xlim(0, 0.78)
    ax.set_xticks(np.arange(0, 0.8, 0.1))
    ax.set_xticklabels([f"{x:.0%}" for x in np.arange(0, 0.8, 0.1)], fontsize=8.4)
    ax.set_ylim(0.3, len(rows) + 0.8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    for y, row in zip([len(rows) - i for i in range(len(rows))], rows):
        ax.text(1.012, y, f"n = {row[3]:,}", transform=ax.get_yaxis_transform(), va="center",
                fontsize=8, color=INK_FAINT)

    top = header(fig, "Which kinds of equality Tunisians think are applied", [
        "Share saying equality is applied completely or to some extent, pooled over eight Arab Opinion "
        f"Index rounds, {len(pool):,} respondents, 2012 to 2025. Weighted; bars are 95% intervals on "
        "Kish's effective sample size, so the weighting is paid for.",
        "The ordering is the finding. Equality is reported to hold across the lines people are born on — "
        "skin colour, religion, gender — and to fail across the lines of money and power: wealth, "
        "political influence, social status. The two ends are about 38 points apart, far outside these "
        "intervals. No release here carries the stratum and PSU a full design correction wants, so the "
        "intervals are narrower than a design-based one would be.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-by-dimension.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"by-dimension: {len(rows)} dimensions, {len(pool):,} respondents")


def region_figure(pool: pd.DataFrame) -> None:
    known = pool[pool["region"].notna()]
    rows = sorted(
        ((r, *share(g, "index")) for r, g in known.groupby("region")),
        key=lambda r: r[1],
    )
    geographic = {r: share(g, "Geographic area")[:2] for r, g in known.groupby("region")}
    _, coastal, _ = region_map()

    fig, ax = plt.subplots(figsize=(12.5, 0.62 * len(rows) + 3.8), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    dots(ax, rows, PRIMARY, 0.16, "All eight dimensions (index)")
    second = [(r[0], *geographic[r[0]], 0) for r in rows]
    dots(ax, second, SECOND, -0.16, "Equality regardless of geographic area", annotate=False)

    ax.set_yticks([len(rows) - i for i in range(len(rows))])
    ax.set_yticklabels(
        [f"{r[0]}  ·  {'littoral' if r[0] in coastal else 'interior'}" for r in rows],
        fontsize=9.4, color=INK,
    )
    ax.set_xlim(0.18, 0.55)
    ax.set_xticks(np.arange(0.20, 0.56, 0.05))
    ax.set_xticklabels([f"{x:.0%}" for x in np.arange(0.20, 0.56, 0.05)], fontsize=8.4)
    ax.set_ylim(0.3, len(rows) + 0.8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    for y, row in zip([len(rows) - i for i in range(len(rows))], rows):
        ax.text(1.012, y, f"n = {row[3]:,}", transform=ax.get_yaxis_transform(), va="center",
                fontsize=8, color=INK_FAINT)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.004), ncol=2, frameon=False,
              fontsize=8.8, labelcolor=INK_SOFT)

    bottom, top_region = rows[0], rows[-1]
    lines = [
        "Share saying equality is applied, by the seven statistical regions Tunisia uses for regional "
        f"accounts, pooled over eight Arab Opinion Index rounds, {len(known):,} respondents. Weighted, "
        "with 95% intervals on Kish's effective sample size.",
        f"{bottom[0]} — Kairouan, Kasserine and Sidi Bouzid, the poorest region and where the 2010 "
        f"uprising began — is lowest on both measures, at {bottom[1]:.0%} against {top_region[1]:.0%} in "
        f"{top_region[0]}. But poverty does not order the rest: {top_region[0]} is interior too and ranks "
        "highest, and Grand Tunis sits below both southern regions. The littoral/interior line, marked "
        "against each row, does not by itself explain this ranking, and the intervals overlap across "
        "most adjacent pairs.",
        "The grouping is not in any release. It is applied here from "
        "catalog/tunisia-regions.json, which names its source and can be changed without touching code.",
    ]
    top = header(fig, "Where Tunisians think equality is applied", lines)
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-by-region.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"by-region: {len(rows)} regions, {len(known):,} respondents")


def group_figure(pool: pd.DataFrame) -> None:
    panels = []
    for _, (name, labels) in GROUPS.items():
        if name not in pool:
            continue
        rows = [(text, *share(pool[pool[name] == code], "index")) for code, text in labels.items()]
        rows = [r for r in rows if r[3] >= 100]
        if len(rows) >= 2:
            panels.append((name, rows))
    if not panels:
        return

    overall = share(pool, "index")[0]
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 8.2), facecolor=SURFACE)
    axes = np.atleast_1d(axes).ravel()
    verdicts = []
    for panel, (name, rows) in enumerate(panels):
        ax = axes[panel]
        ax.set_facecolor(SURFACE)
        ax.axvline(overall, color=INK_FAINT, lw=1, ls=(0, (4, 3)), zorder=1)
        dots(ax, rows)
        spread = max(r[1] for r in rows) - min(r[1] for r in rows)
        # Separated when the best group's interval clears the worst group's — a plain
        # test the reader can run off the figure. Monotone is a separate claim: a
        # difference between the ends says nothing about the order of the middle.
        low = min(rows, key=lambda r: r[1])
        high = max(rows, key=lambda r: r[1])
        separated = high[1] - high[2] > low[1] + low[2]
        # Ordered up to noise: a step backwards smaller than the panel's own tightest
        # interval is not a reversal, and calling a 0.2-point wobble "not ordered"
        # would say more than the data do.
        means = [r[1] for r in rows]
        tolerance = min(r[2] for r in rows)
        steps = [y - x for x, y in zip(means, means[1:])]
        monotone = len(means) > 2 and (
            all(d >= -tolerance for d in steps) or all(d <= tolerance for d in steps)
        )
        verdicts.append((name, spread, separated, monotone))
        ax.set_yticks([len(rows) - i for i in range(len(rows))])
        ax.set_yticklabels([clip(r[0], 26) for r in rows], fontsize=8.8, color=INK)
        ax.set_xlim(0.30, 0.52)
        ax.set_xticks([0.30, 0.35, 0.40, 0.45, 0.50])
        ax.set_xticklabels(["30%", "35%", "40%", "45%", "50%"], fontsize=8)
        ax.set_ylim(0.3, len(rows) + 0.9)
        ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
        frame_style(ax)
        verdict = "ends separated" if separated else "ends overlap"
        if separated and monotone:
            verdict += ", and ordered"
        elif separated:
            verdict += ", but not ordered"
        ax.set_title(f"{name}   ·   {spread * 100:.1f} point spread, {verdict}",
                     fontsize=9.4, color=INK, loc="left", pad=8)

    for ax in axes[len(panels):]:
        ax.axis("off")

    ordered = [v for v in verdicts if v[2] and v[3]]
    unordered = [v for v in verdicts if v[2] and not v[3]]
    flat = [v for v in verdicts if not v[2]]
    story = []
    if ordered:
        story.append("Ordered top to bottom: " + ", ".join(
            f"{n.lower()} ({s * 100:.0f} points)" for n, s, _, _ in ordered) + ".")
    if unordered:
        story.append("Separated at the ends but not ordered through the middle: "
                     + ", ".join(n.lower() for n, *_ in unordered) + ".")
    if flat:
        story.append("No reliable difference at all: " + ", ".join(n.lower() for n, *_ in flat) + ".")

    top = header(fig, "Who thinks equality is applied", [
        "The index is the share of the eight dimensions a respondent says equality is applied to, pooled "
        f"over eight Arab Opinion Index rounds, {len(pool):,} respondents. Weighted, with 95% intervals "
        "on Kish's effective sample size. The dashed line is the pooled mean.",
        " ".join(story) + " Separation is read off the figure: a panel's ends count as separated when the "
        "highest group's interval clears the lowest group's. Being separated is not the same as being "
        "ordered — education differs end to end while running down and back up in between. Panels that "
        "come out flat are drawn rather than dropped, because a null across 15,000 respondents is a "
        "result and not an empty panel.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top), h_pad=3.0, w_pad=3.0)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-by-group.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"by-group: {len(panels)} groupings")


def archive_figure() -> None:
    """Every inequality variable in the archive, by facet and survey — not just recurring ones."""
    topic = pd.read_csv(TOPIC)
    surveys = catalog()
    facets = json.loads((ROOT / "catalog" / "topics.json").read_text(encoding="utf-8"))
    titles = {k: v["title"] for k, v in facets["topics"]["inequality"]["facets"].items()}

    spread = topic.assign(facet=topic["facets"].str.split(";")).explode("facet")
    counts = spread.pivot_table(index="facet", columns="survey", values="variable",
                                aggfunc="count", fill_value=0)
    order = sorted(surveys, key=lambda k: (year_of(surveys[k]), k))
    counts = counts.reindex(columns=order, fill_value=0)
    counts = counts.reindex(index=counts.sum(axis=1).sort_values(ascending=False).index)

    fig, ax = plt.subplots(figsize=(0.46 * len(counts.columns) + 6.5, 0.5 * len(counts) + 4.2),
                           facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    grid = counts.to_numpy(dtype=float)
    shown = np.where(grid > 0, grid, np.nan)
    ramp = matplotlib.colors.LinearSegmentedColormap.from_list(
        "blues", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"])
    ramp.set_bad("#f4f3f0")
    image = ax.imshow(shown, cmap=ramp, norm=matplotlib.colors.LogNorm(1, max(grid.max(), 2)))
    for i in range(len(counts)):
        for j in range(len(counts.columns)):
            if grid[i, j]:
                ax.text(j, i, int(grid[i, j]), ha="center", va="center", fontsize=7.6,
                        color="#ffffff" if grid[i, j] > 12 else INK)

    ax.set_xticks(range(len(counts.columns)))
    ax.set_xticklabels(
        [f"{SHORT[surveys[k]['series']]} {surveys[k]['wave_label']}" for k in counts.columns],
        rotation=90, fontsize=7.8, color=INK_SOFT)
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels([titles.get(f, f) for f in counts.index], fontsize=8.8, color=INK)
    ax.set_xticks(np.arange(len(counts.columns) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(counts) + 1) - 0.5, minor=True)
    ax.grid(which="minor", color=SURFACE, lw=1.6)
    ax.tick_params(which="both", length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    bar = fig.colorbar(image, ax=ax, shrink=0.42, pad=0.015, fraction=0.03)
    bar.set_label("Variables (log scale)", fontsize=8.4, color=INK_SOFT)
    bar.ax.tick_params(labelsize=8, colors=INK_SOFT)
    bar.outline.set_visible(False)

    empty = int((grid.sum(axis=0) == 0).sum())
    top = header(fig, "What the archive holds on inequality, and what it does not", [
        f"All {len(topic):,} inequality variables across the {len(surveys)} surveys, by facet and by "
        "survey in fieldwork order — every matched variable, not only the ones that recur. A variable "
        "matching two facets is counted in both. Blank is nothing, not a small number.",
        "Coverage is uneven enough that the facet decides which programme you can use: the Arab Opinion "
        "Index carries the equality-as-a-principle and gender items, Afrobarometer and Arab Barometer "
        "Wave VIII carry the discrimination items, and wasta appears only in Arab Barometer. "
        f"{empty} of the {len(surveys)} surveys carry nothing on inequality at all. Counts are on a log "
        "scale, so a dark cell is many times a pale one, not a few more.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"inequality-archive-map.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"archive-map: {len(counts)} facets x {len(counts.columns)} surveys")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    pool = pooled()
    dimension_figure(pool)
    region_figure(pool)
    group_figure(pool)
    archive_figure()


if __name__ == "__main__":
    main()
