#!/usr/bin/env python3
"""Perception of democracy: how Tunisians rate what they have, 2011 to 2024.

Assessment, not preference. Whether people *want* democracy is a different question and
lives in ``docs/topics/regime-preference.md``; these four figures ask how democratic
people say Tunisia is, how satisfied they are with the way it works, whether the
programmes agree, and what they take the word to mean.

The period is the point. Afrobarometer fielded Round 8 between 24 February and 18 March
2020, seventeen months before Kais Saied suspended parliament on 25 July 2021, and
Round 9 between 21 February and 17 March 2022, seven months after. Round 10 followed in
February 2024. The break falls cleanly between two rounds of an identical question.

Afrobarometer renumbers between rounds while keeping the Q prefix, so both items are
matched on **question wording, never variable names**: extent of democracy is Q42, Q40,
Q35, Q36, Q30 and Q32 across the six rounds, and satisfaction Q43, Q41, Q36, Q37, Q31
and Q33 — note that Q36 is the assessment item in one round and the satisfaction item in
another.
"""

from __future__ import annotations

import json
import re

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat

from build_inequality_figures import (
    DIVERGING, FIGURES, GRID, INK, INK_FAINT, INK_SOFT, ROOT, SHORT, SURFACE, WEIGHTS,
    catalog, clip, frame_style, header, year_of,
)
from build_inequality_breakdowns import REGIONS, share

PRIMARY, SECOND, THIRD = "#2a78d6", "#eb6834", "#1baf7a"
COUP = "25 July 2021"

EXTENT = re.compile(r"extent of democracy|niveau de d[ée]mocratie$", re.I)
SATISFACTION = re.compile(r"satisfaction with democracy|satisfaction avec la d[ée]mocratie", re.I)

EXTENT_LABELS = ["Not a democracy", "A democracy with major problems",
                 "A democracy with minor problems", "A full democracy"]
SATISFACTION_LABELS = ["Not at all satisfied", "Not very satisfied",
                       "Fairly satisfied", "Very satisfied"]

# Self-rating of national democracy on a 0-to-10 or 1-to-10 scale, by survey. The two
# ranges are not the same instrument, so each is normalised on its own floor and ceiling
# and the range is printed beside every point.
RATINGS = {
    "ab-w02": ("q511", 0, 10), "ab-w03": ("q511", 0, 10), "ab-w04": ("q511", 1, 10),
    "wvs-w06": ("V141", 1, 10), "wvs-w07": ("Q251", 1, 10),
}


def afrobarometer() -> pd.DataFrame:
    """Both democracy items for every Afrobarometer round, matched on wording."""
    frames = []
    for key, survey in catalog().items():
        if survey["series"] != "afrobarometer":
            continue
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, meta = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        labels = {c: str(meta.column_names_to_labels.get(c) or "") for c in data.columns}
        extent = [c for c in data.columns if EXTENT.search(labels[c])]
        satisfaction = [c for c in data.columns if SATISFACTION.search(labels[c])]
        if len(extent) != 1 or len(satisfaction) != 1:
            raise SystemExit(f"{key}: {len(extent)} extent and {len(satisfaction)} satisfaction items")
        weight = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)

        spec = json.loads(REGIONS.read_text(encoding="utf-8"))
        governorate = {g: n for n, b in spec["regions"].items() for g in b["governorates"]}
        region = data[upper["REGION"]].map(meta.variable_value_labels.get(upper["REGION"], {}))
        region = region.astype("string").str.strip().replace(spec["spelling_variants"])
        region = region.map(lambda x: spec["region_variants"].get(x, governorate.get(x)))

        block = pd.DataFrame({
            "survey": key, "year": year_of(survey), "window": survey.get("fieldwork_tunisia") or "",
            "weight": data[weight] if weight else 1.0, "region": region,
            # 1-4; 8 and 9 are "do not understand the question" and "don't know"
            "extent": data[extent[0]].where(data[extent[0]].between(1, 4)),
            # 0 is "the country is not a democracy", which is not a point on the scale
            "satisfaction": data[satisfaction[0]].where(data[satisfaction[0]].between(1, 4)),
            "denies_democracy": (data[satisfaction[0]] == 0).astype(float).where(
                data[satisfaction[0]].between(0, 4)),
            "urban": (data[upper["URBRUR"]] == 1).astype(float).where(
                data[upper["URBRUR"]].isin([1, 2])),
        })
        for name, variable in (("education", "Q97"), ("age", "Q1")):
            found = next((upper[v] for v in (variable,) if v in upper), None)
            block[name] = data[found] if found else np.nan
        frames.append(block)
    return pd.concat(frames, ignore_index=True)


def diverging_panel(ax, points: list[tuple[int, dict]], labels: list[str]) -> None:
    """Four ordered answers, affirmative up and negative down from a common zero."""
    years = [y for y, _ in points]
    positive, negative = [3, 4], [2, 1]
    up = np.zeros(len(points))
    down = np.zeros(len(points))
    for code in positive:
        values = np.array([p[1].get(code, 0.0) for p in points])
        ax.bar(years, values, bottom=up, width=0.9, color=DIVERGING[4 - code],
               edgecolor=SURFACE, linewidth=1.2, label=labels[code - 1])
        up = up + values
    for code in negative:
        values = np.array([p[1].get(code, 0.0) for p in points])
        ax.bar(years, -values, bottom=down, width=0.9, color=DIVERGING[4 - code],
               edgecolor=SURFACE, linewidth=1.2, label=labels[code - 1])
        down = down - values
    ax.axhline(0, color=INK_SOFT, lw=0.9, zorder=4)
    ax.set_ylim(-0.85, 0.85)
    ax.set_yticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75])
    ax.set_yticklabels(["75%", "50%", "25%", "0", "25%", "50%", "75%"], fontsize=7.8)
    ax.set_xticks(years)
    ax.set_xticklabels(years, fontsize=8.2)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    ax.spines["bottom"].set_visible(False)


def distribution(frame: pd.DataFrame, column: str) -> list[tuple[int, dict]]:
    points = []
    for year, block in sorted(frame.groupby("year")):
        keep = block[column].notna()
        weight = block.loc[keep, "weight"]
        total = weight.sum()
        points.append((int(year), {int(code): float(weight[block.loc[keep, column] == code].sum() / total)
                                   for code in (1, 2, 3, 4)}))
    return points


def break_marker(ax, points: list[tuple[int, dict]]) -> None:
    """The self-coup, drawn where it falls between two rounds rather than on one."""
    years = [y for y, _ in points]
    before = max((y for y in years if y <= 2021), default=None)
    after = min((y for y in years if y > 2021), default=None)
    if before is None or after is None:
        return
    at = (before + after) / 2
    ax.axvline(at, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=5)
    ax.annotate(COUP, (at, 0.80), ha="center", va="bottom", fontsize=8.2,
                fontweight="bold", color=INK)


def timeline_figure(afro: pd.DataFrame) -> None:
    extent, satisfaction = distribution(afro, "extent"), distribution(afro, "satisfaction")
    fig, axes = plt.subplots(1, 2, figsize=(15.0, 6.4), facecolor=SURFACE)
    for ax, points, labels, title in (
        (axes[0], extent, EXTENT_LABELS, "How democratic is Tunisia?"),
        (axes[1], satisfaction, SATISFACTION_LABELS, "Satisfied with the way democracy works?"),
    ):
        ax.set_facecolor(SURFACE)
        diverging_panel(ax, points, labels)
        break_marker(ax, points)
        ax.set_title(title, fontsize=10.5, color=INK, loc="left", pad=10, fontweight="bold")
        handles, names = ax.get_legend_handles_labels()
        order = [names.index(labels[i]) for i in (3, 2, 1, 0) if labels[i] in names]
        ax.legend([handles[i] for i in order], [clip(names[i], 32) for i in order],
                  loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=2, frameon=False,
                  fontsize=8.2, labelcolor=INK_SOFT, handlelength=1.2, handleheight=1.2,
                  columnspacing=1.4, borderpad=0)

    before = dict(next(p for p in extent if p[0] == 2020)[1])
    after = dict(next(p for p in extent if p[0] == 2022)[1])
    latest = dict(extent[-1][1])
    sat = {y: v for y, v in satisfaction}
    denies = {int(y): share(b, "denies_democracy")[0] for y, b in afro.groupby("year")}

    top = header(fig, "Tunisians on their own democracy, before and after the self-coup", [
        "Weighted shares of substantive answers across six Afrobarometer rounds. Bars diverge from zero "
        "so each pole keeps a common baseline: answers calling Tunisia a democracy, or expressing "
        "satisfaction, run up; the others run down. Don't-know and 'do not understand the question' are "
        "dropped, as is the separate satisfaction answer 'the country is not a democracy', which is not a "
        f"point on that scale — it was given by {denies[2022]:.0%} of respondents in 2022, its high point.",
        f"Round 8 was in the field to 18 March 2020, seventeen months before {COUP}; Round 9 from 21 "
        "February 2022, seven months after. Across that break the share calling Tunisia a democracy with "
        f"only minor problems or better fell from {before[3] + before[4]:.0%} to {after[3] + after[4]:.0%}, "
        f"and those saying it is not a democracy at all rose from {before[1]:.0%} to {after[1]:.0%}.",
        f"Then it reversed. By 2024 both readings are the strongest in the series: "
        f"{latest[3] + latest[4]:.0%} call Tunisia a democracy with minor problems or better and "
        f"{sat[2024][3] + sat[2024][4]:.0%} are satisfied with how it works, above even the pre-coup "
        "figures. These are separate cross-sections, not the same people asked twice; and a question "
        "about how democratic a country is may not hold its meaning fixed across a change of regime, "
        "which is a reason to read the 2024 rise as a change in what respondents say rather than a "
        "measurement of what Tunisia became.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top), w_pad=3.0)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"democracy-assessment-and-satisfaction.{suffix}", dpi=200,
                    facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"timeline: 2020 democracy {before[3] + before[4]:.0%} -> 2022 {after[3] + after[4]:.0%} "
          f"-> 2024 {latest[3] + latest[4]:.0%}")


def ratings_figure(afro: pd.DataFrame) -> None:
    """Every self-rating of national democracy the archive holds, on one timeline."""
    surveys = catalog()
    rows = []
    for key, (variable, low, high) in RATINGS.items():
        survey = surveys[key]
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, _ = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        if variable.upper() not in upper:
            continue
        values = pd.to_numeric(data[upper[variable.upper()]], errors="coerce")
        values = values.where(values.between(low, high))
        weight = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)
        block = pd.DataFrame({"value": (values - low) / (high - low),
                              "weight": data[weight] if weight else 1.0})
        mean, half, effective = share(block, "value")
        if effective:
            rows.append((year_of(survey), key, survey["series"], mean, half, low, high, effective))
    rows.sort()

    fig, axes = plt.subplots(1, 2, figsize=(15.0, 6.0), facecolor=SURFACE,
                             gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    ax.set_facecolor(SURFACE)
    for year, key, series, mean, half, low, high, effective in rows:
        colour = PRIMARY if series == "arab-barometer" else SECOND
        ax.plot([year, year], [mean - half, mean + half], color=colour, lw=2.4, alpha=0.45,
                solid_capstyle="round", zorder=2)
        ax.scatter([year], [mean], s=80, color=colour, edgecolor=SURFACE, linewidth=1.3, zorder=3)
        ax.annotate(f"{mean * 100:.0f}\n{low}–{high}", (year, mean), textcoords="offset points",
                    xytext=(0, 13), ha="center", fontsize=7.8, color=INK)
    ax.set_ylim(0.18, 0.72)
    ax.set_yticks([0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
    ax.set_yticklabels(["20", "30", "40", "50", "60", "70"], fontsize=8.2)
    ax.set_xlim(2009.5, 2025.5)
    ax.set_xticks(range(2010, 2026, 2))
    ax.tick_params(labelsize=8.2)
    ax.grid(color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    ax.set_ylabel("Mean rating, rescaled to 0–100", fontsize=8.8, color=INK_SOFT, labelpad=8)
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=t, markersize=7)
               for c, t in ((PRIMARY, "Arab Barometer"), (SECOND, "World Values Survey"))]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.004), ncol=2,
              frameon=False, fontsize=8.6, labelcolor=INK_SOFT)
    ax.set_title("Numeric self-rating · four surveys, two programmes", fontsize=9.6,
                 color=INK, loc="left", pad=26)

    ax = axes[1]
    ax.set_facecolor(SURFACE)
    points = distribution(afro, "extent")
    years = [y for y, _ in points]
    ys = [p[1][3] + p[1][4] for p in points]
    ax.plot(years, ys, color="#1baf7a", lw=2.2, zorder=3)
    ax.plot(years, ys, "o", color="#1baf7a", ms=6, mec=SURFACE, mew=1.3, zorder=4)
    for year, value in zip(years, ys):
        ax.annotate(f"{value:.0%}", (year, value), textcoords="offset points", xytext=(0, 11),
                    ha="center", fontsize=8, color=INK, fontweight="bold")
    at = 2021
    ax.axvline(at, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=5)
    ax.annotate(COUP, (at, 0.60), ha="center", va="bottom", fontsize=8.2, fontweight="bold", color=INK)
    ax.set_ylim(0.18, 0.68)
    ax.set_yticks([0.2, 0.3, 0.4, 0.5, 0.6])
    ax.set_yticklabels(["20%", "30%", "40%", "50%", "60%"], fontsize=8.2)
    ax.set_xlim(2009.5, 2025.5)
    ax.set_xticks(range(2010, 2026, 2))
    ax.tick_params(labelsize=8.2)
    ax.grid(color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    ax.set_ylabel("Share saying 'minor problems' or 'full democracy'", fontsize=8.8,
                  color=INK_SOFT, labelpad=8)
    ax.set_title("Afrobarometer's four-point item · six rounds", fontsize=9.6,
                 color=INK, loc="left", pad=26)

    # Two surveys in one year is the only check available here, and it is worth reporting
    # whichever way it comes out.
    same_year = [r for r in rows if r[0] == 2013]
    if len(same_year) == 2:
        first, second = sorted(same_year, key=lambda r: -r[3])
        clash = (f"Two surveys landed in 2013, nine months apart, and that is the one check available: "
                 f"they disagree by {abs(first[3] - second[3]) * 100:.0f} points on a 0–100 rescaling — "
                 f"{SHORT[first[2]]} reads {first[3] * 100:.0f} and {SHORT[second[2]]} reads "
                 f"{second[3] * 100:.0f}. Read the levels here as programme-specific and the movement "
                 "within a programme as the thing worth comparing.")
    else:
        clash = ("No two of these surveys fall in the same year, so there is nothing here to check one "
                 "reading against another.")

    top = header(fig, "Every reading the archive holds on how democratic Tunisia is", [
        "Three programmes ask the question and none of them asks it the same way, so they are drawn "
        "apart rather than joined. On the left, numeric self-ratings rescaled to 0–100 on their own "
        "floor and ceiling, with each survey's raw range printed beside its point; on the right, "
        "Afrobarometer's four-point item, which has no numeric scale to rescale.",
        "Rescaling makes the left panel comparable in shape, not in kind: Arab Barometer Waves II and "
        "III run 0 to 10 and Wave IV and both World Values Survey waves run 1 to 10, so their floors "
        "are a step apart, and a 'don't know' is treated as missing throughout.",
        clash,
    ])
    fig.tight_layout(rect=(0, 0, 1, top), w_pad=3.5)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"democracy-rating-across-programmes.{suffix}", dpi=200,
                    facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"ratings: {len(rows)} numeric readings from {len({r[2] for r in rows})} programmes")


def who_figure(afro: pd.DataFrame) -> None:
    """Whether the swing after the coup was general or concentrated."""
    afro = afro[afro["extent"].notna()].copy()
    afro["denies"] = (afro["extent"] == 1).astype(float)
    afro["democracy"] = (afro["extent"] >= 3).astype(float)
    cuts = [
        ("Region", "region", None),
        ("Where they live", "urban", {1.0: "Urban", 0.0: "Rural"}),
    ]
    rounds = [2020, 2022, 2024]

    fig, axes = plt.subplots(1, 2, figsize=(14.5, 6.6), facecolor=SURFACE,
                             gridspec_kw={"width_ratios": [1.5, 1]})
    for ax, (title, column, mapping) in zip(axes, cuts):
        ax.set_facecolor(SURFACE)
        frame = afro[afro["year"].isin(rounds)]
        keys = (sorted(frame[column].dropna().unique(), key=str) if mapping is None
                else list(mapping))
        names = [str(k) if mapping is None else mapping[k] for k in keys]
        width = 0.26
        for i, year in enumerate(rounds):
            values, errors = [], []
            for key in keys:
                block = frame[(frame["year"] == year) & (frame[column] == key)]
                mean, half, effective = share(block, "democracy")
                values.append(mean if effective >= 40 else np.nan)
                errors.append(half if effective >= 40 else 0.0)
            offset = (i - 1) * width
            ax.bar([x + offset for x in range(len(keys))], values, width=width * 0.92,
                   color=[PRIMARY, SECOND, "#1baf7a"][i], edgecolor=SURFACE, linewidth=1.0,
                   label=str(year), zorder=2)
            ax.errorbar([x + offset for x in range(len(keys))], values, yerr=errors, fmt="none",
                        ecolor=INK_FAINT, elinewidth=1.1, capsize=2.4, zorder=3)
        ax.set_xticks(range(len(keys)))
        ax.set_xticklabels([clip(n, 13) for n in names], rotation=30, ha="right", fontsize=8.4)
        ax.set_ylim(0, 0.8)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
        ax.set_yticklabels(["0", "20%", "40%", "60%", "80%"], fontsize=8.2)
        ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
        frame_style(ax)
        ax.set_title(title, fontsize=9.8, color=INK, loc="left", pad=10, fontweight="bold")
        ax.legend(loc="upper right", frameon=False, fontsize=8.4, labelcolor=INK_SOFT, ncol=3)

    national = {y: share(afro[afro["year"] == y], "democracy")[0] for y in rounds}
    top = header(fig, "The swing was general, not local", [
        "Share saying Tunisia is a democracy with only minor problems or a full democracy, by region "
        "and by whether the respondent lives in an urban or rural area, in the round before the "
        f"self-coup and the two after. Weighted, with 95% intervals on Kish's effective sample size; a "
        "bar is drawn only where at least 40 effective respondents fall in the cell, which at this "
        "resolution is the binding constraint.",
        f"Nationally the reading went {national[2020]:.0%} in 2020, {national[2022]:.0%} in 2022 and "
        f"{national[2024]:.0%} in 2024. Every region moves the same way across the break, and so do "
        "town and country: the fall after 2021 and the recovery by 2024 are not carried by one part of "
        "the country. Region cells are small once they are split by round, so the intervals are wide "
        "and the ordering between regions within a round should not be read as a ranking.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top), w_pad=3.0)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"democracy-perception-who.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"who: {national[2020]:.0%} -> {national[2022]:.0%} -> {national[2024]:.0%}")


def meaning_figure() -> None:
    """What Tunisians pick as the essential characteristic of democracy."""
    survey = catalog()["afro-w05"]
    path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
    data, meta = pyreadstat.read_sav(str(path), user_missing=True)
    upper = {c.upper(): c for c in data.columns}
    weight = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)
    rows = []
    for variable in ("Q44", "Q45", "Q57", "Q58"):
        if variable not in upper:
            continue
        column = upper[variable]
        labels = meta.variable_value_labels.get(column, {})
        options = {c: l for c, l in labels.items()
                   if not re.search(r"missing|none of these|don.?t know|refus", str(l), re.I)}
        block = pd.DataFrame({"value": data[column].where(data[column].isin(options)),
                              "weight": data[weight] if weight else 1.0})
        for code, label in options.items():
            picked = block.assign(hit=(block["value"] == code).astype(float).where(block["value"].notna()))
            mean, half, effective = share(picked, "hit")
            if effective:
                rows.append((str(label), mean, half, variable))
    rows.sort(key=lambda r: r[1], reverse=True)

    fig, ax = plt.subplots(figsize=(12.5, 0.44 * len(rows) + 3.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ys = [len(rows) - i for i in range(len(rows))]
    for y, row in zip(ys, rows):
        ax.plot([row[1] - row[2], row[1] + row[2]], [y, y], color=PRIMARY, lw=2.4,
                alpha=0.45, solid_capstyle="round", zorder=2)
        ax.scatter([row[1]], [y], s=60, color=PRIMARY, edgecolor=SURFACE, linewidth=1.2, zorder=3)
        ax.annotate(f"{row[1]:.0%}", (row[1], y), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=7.8, color=INK, fontweight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([clip(r[0], 58) for r in rows], fontsize=8.6, color=INK)
    ax.set_xlim(0, 0.70)
    ax.set_xticks(np.arange(0, 0.61, 0.1))
    ax.set_xticklabels([f"{x:.0%}" for x in np.arange(0, 0.61, 0.1)], fontsize=8.2)
    ax.set_ylim(0.3, len(rows) + 0.8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    for y, row in zip(ys, rows):
        ax.text(1.012, y, row[3], transform=ax.get_yaxis_transform(), va="center",
                fontsize=7.8, color=INK_FAINT)

    top = header(fig, "What Tunisians call essential to democracy", [
        "Afrobarometer Round 5, 2013, 1,200 respondents, weighted, with 95% intervals. Respondents were "
        "asked four separate questions, each offering a different set of four candidates, and asked to "
        "pick the one most essential. Shares are within each question, so they compete only with the "
        "three options beside them — the code in the right margin says which question an option came "
        "from, and options from different questions are not rivals.",
        "Only Round 5 asks this, so there is nothing to trace over time. It is here because the other "
        "figures measure how democratic people say Tunisia is without establishing what they are "
        "measuring it against.",
        "What tops the list is delivery — necessities, clean politics, jobs — and what sits at the "
        "bottom is procedure: free expression, a critical press, parties competing, the right to "
        "demonstrate. If that is what the word means to a respondent, then a government judged to "
        "deliver can be called democratic by someone who would not call it liberal. That bears on the "
        "2024 reading in the other figures, but it does not establish it: this was asked in 2013 and "
        "not since, so the connection is a hypothesis the archive cannot test.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"democracy-meaning.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"meaning: {len(rows)} options across four questions")



# The three-statement forced choice: 3 is "democracy is preferable to any other kind of
# government", 2 "sometimes a non-democratic government can be preferable", 1 "it doesn't
# matter". The rejection battery runs 1 strongly disapprove to 5 strongly approve, so
# rejecting a form of rule is codes 1 and 2.
SUPPORT = re.compile(r"support for democracy|soutien à la démocratie", re.I)
REJECT = {
    "One-party rule": re.compile(r"reject one-party rule|rejet de la règle du parti unique", re.I),
    "Military rule": re.compile(r"reject military rule|rejet d'un gouvernement militaire", re.I),
    "One-man rule": re.compile(r"reject one-man rule|rejet de la dictature", re.I),
}
WVS_SYSTEMS = {
    "wvs-w06": {"V130": "A democratic political system", "V128": "Experts, not government, decide",
                "V127": "A strong leader, no parliament or elections", "V129": "The army rules"},
    "wvs-w07": {"Q238": "A democratic political system", "Q236": "Experts, not government, decide",
                "Q235": "A strong leader, no parliament or elections", "Q237": "The army rules"},
}


def weighted_share(frame: pd.DataFrame, column: str, wanted: list, universe: list) -> float:
    values, weight = frame[column], frame["weight"]
    keep = values.isin(universe)
    if not keep.any() or weight[keep].sum() <= 0:
        return float("nan")
    return float((values[keep].isin(wanted) * weight[keep]).sum() / weight[keep].sum())


def series_for(pattern, wanted, universe, programme: str) -> list[tuple[int, float]]:
    points = []
    for key, survey in catalog().items():
        if survey["series"] != programme:
            continue
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, meta = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        weight = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)
        if isinstance(pattern, str):
            column = upper.get(pattern.upper())
        else:
            labels = {c: str(meta.column_names_to_labels.get(c) or "") for c in data.columns}
            column = next((c for c in data.columns if pattern.search(labels[c])), None)
        if column is None:
            continue
        frame = pd.DataFrame({column: data[column], "weight": data[weight] if weight else 1.0})
        value = weighted_share(frame, column, wanted, universe)
        if np.isfinite(value):
            points.append((year_of(survey), value))
    return sorted(points)


def line(ax, points, colour, label, annotate=True, lift: float = 9.0) -> None:
    """One series, with its end values labelled. ``lift`` staggers those labels so that
    three lines converging on the same value do not print their numbers on top of
    each other."""
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=colour, lw=2.1, zorder=3, label=label)
    ax.plot(xs, ys, "o", color=colour, ms=5.2, mec=SURFACE, mew=1.2, zorder=4)
    if annotate:
        for x, y in ((xs[0], ys[0]), (xs[-1], ys[-1])):
            ax.annotate(f"{y:.0%}", (x, y), textcoords="offset points", xytext=(0, lift),
                        ha="center", fontsize=7.6, color=colour, fontweight="bold")


def coup_line(ax, y: float = 0.06) -> None:
    ax.axvline(2021.56, color=INK, lw=1.1, ls=(0, (4, 3)), zorder=5)
    ax.annotate(COUP, (2021.56, y), ha="center", va="bottom", fontsize=7.4,
                fontweight="bold", color=INK, rotation=90)


def time_axis(ax) -> None:
    ax.set_xlim(2009.5, 2025.8)
    ax.set_xticks(range(2011, 2026, 3))
    ax.set_ylim(0, 1.02)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0", "25%", "50%", "75%", "100%"], fontsize=7.8)
    ax.tick_params(labelsize=7.8)
    ax.grid(color=GRID, lw=0.8, zorder=0)
    frame_style(ax)


def fear_figure() -> None:
    """Test the claim that Tunisians turned against democracy, on its own terms."""
    churchill = series_for("Q405_6", [1, 2], [1, 2, 3, 4], "arab-opinion-index")
    indecisive = series_for("Q405_2", [1, 2], [1, 2, 3, 4], "arab-opinion-index")
    preferable = series_for(SUPPORT, [3], [1, 2, 3], "afrobarometer")
    wvs_democracy = series_for("Q238", [1, 2], [1, 2, 3, 4], "world-values-survey")
    wvs_democracy += series_for("V130", [1, 2], [1, 2, 3, 4], "world-values-survey")
    wvs_democracy.sort()
    rejects = {name: series_for(pattern, [1, 2], [1, 2, 3, 4, 5], "afrobarometer")
               for name, pattern in REJECT.items()}

    systems = {}
    for key, mapping in WVS_SYSTEMS.items():
        survey = catalog()[key]
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, _ = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        weight = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)
        for variable, name in mapping.items():
            if variable.upper() not in upper:
                continue
            column = upper[variable.upper()]
            frame = pd.DataFrame({column: data[column], "weight": data[weight] if weight else 1.0})
            systems.setdefault(name, {})[year_of(survey)] = weighted_share(
                frame, column, [1, 2], [1, 2, 3, 4])

    fig, axes = plt.subplots(2, 2, figsize=(15.0, 10.4), facecolor=SURFACE)
    axes = axes.ravel()

    ax = axes[0]
    ax.set_facecolor(SURFACE)
    line(ax, churchill, PRIMARY, "Arab Opinion Index · agree 'democracy has problems but remains better'")
    line(ax, preferable, SECOND, "Afrobarometer · 'democracy is preferable to any other kind of government'")
    line(ax, wvs_democracy, THIRD, "World Values Survey · 'a democratic political system' would be good")
    coup_line(ax)
    time_axis(ax)
    ax.set_title("Do Tunisians want democracy?", fontsize=10.4, color=INK, loc="left",
                 pad=10, fontweight="bold")
    ax.legend(loc="lower left", bbox_to_anchor=(0, -0.42), frameon=False, fontsize=7.8,
              labelcolor=INK_SOFT, handlelength=1.6)

    ax = axes[1]
    ax.set_facecolor(SURFACE)
    for i, (colour, (name, points)) in enumerate(zip((PRIMARY, SECOND, THIRD), rejects.items())):
        if points:
            line(ax, points, colour, name, lift=(9.0, -15.0, 9.0)[i])
    coup_line(ax)
    time_axis(ax)
    ax.set_title("Do they still reject the alternatives?", fontsize=10.4, color=INK,
                 loc="left", pad=10, fontweight="bold")
    ax.legend(loc="lower left", bbox_to_anchor=(0, -0.42), frameon=False, fontsize=7.8,
              labelcolor=INK_SOFT, handlelength=1.6, title="Share disapproving of…",
              title_fontproperties={"size": 7.8, "weight": "bold"})

    ax = axes[2]
    ax.set_facecolor(SURFACE)
    names = list(WVS_SYSTEMS["wvs-w07"].values())
    ys = [len(names) - i for i in range(len(names))]
    for y, name in zip(ys, names):
        early, late = systems[name].get(2013), systems[name].get(2019)
        if early is None or late is None:
            continue
        ax.plot([early, late], [y, y], color=INK_FAINT, lw=1.6, zorder=2)
        ax.scatter([early], [y], s=74, color=INK_FAINT, edgecolor=SURFACE, linewidth=1.2, zorder=3)
        ax.scatter([late], [y], s=84, color=PRIMARY, edgecolor=SURFACE, linewidth=1.2, zorder=4)
        ax.annotate(f"{early:.0%}", (early, y), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=7.6, color=INK_SOFT)
        ax.annotate(f"{late:.0%}", (late, y), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=7.6, color=INK, fontweight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([clip(n, 42) for n in names], fontsize=8.4, color=INK)
    ax.set_xlim(0.12, 1.0)
    ax.set_xticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=7.8)
    ax.set_ylim(0.4, len(names) + 0.8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    ax.set_title("Rated one by one — 2013 (grey) to 2019 (blue); all four fell", fontsize=10.4, color=INK,
                 loc="left", pad=10, fontweight="bold")

    ax = axes[3]
    ax.set_facecolor(SURFACE)
    line(ax, indecisive, SECOND, "Agree")
    coup_line(ax)
    time_axis(ax)
    ax.set_title("'Democracies are characterised by indecisiveness and discord'",
                 fontsize=10.4, color=INK, loc="left", pad=10, fontweight="bold")

    low_churchill = min(churchill, key=lambda p: p[1])
    low_pref = min(preferable, key=lambda p: p[1])
    one_man = rejects["One-man rule"]
    peak_ind = max(indecisive, key=lambda p: p[1])
    counted = len({y for y, _ in churchill} | {y for y, _ in preferable} | {y for y, _ in wvs_democracy})
    top = header(fig, "'Tunisians fear democracy' — what the surveys actually say", [
        f"Four ways of putting the question, across three programmes and {len(churchill) + len(preferable) + len(wvs_democracy)} "
        f"surveys covering {counted} distinct years. Weighted shares; the dashed line is 25 July 2021, "
        "when Kais Saied suspended parliament.",
        f"The claim fails on its own terms. Agreement that democracy remains better than other systems "
        f"never drops below {low_churchill[1]:.0%} in nine Arab Opinion Index rounds and stands at "
        f"{churchill[-1][1]:.0%} in 2024. On Afrobarometer's harder forced choice the floor is "
        f"{low_pref[1]:.0%}, and it came in {low_pref[0]} — before the coup, not after. Asked to rate "
        "systems one by one, Tunisians moved away from the alternatives between 2013 and 2019: a strong "
        f"leader unbothered by parliament fell from {systems['A strong leader, no parliament or elections'][2013]:.0%} "
        f"to {systems['A strong leader, no parliament or elections'][2019]:.0%}, rule by experts from "
        f"{systems['Experts, not government, decide'][2013]:.0%} to {systems['Experts, not government, decide'][2019]:.0%}.",
        f"What did change is not desire but confidence and one guardrail. Agreement that democracies are "
        f"indecisive rose from {indecisive[0][1]:.0%} in {indecisive[0][0]} to {peak_ind[1]:.0%} in "
        f"{peak_ind[0]}. And disapproval of one-man rule fell from {one_man[0][1]:.0%} in {one_man[0][0]} "
        f"to {min(one_man, key=lambda p: p[1])[1]:.0%} by {min(one_man, key=lambda p: p[1])[0]} — "
        "seventeen months before the coup — while disapproval of one-party rule barely moved. That is a "
        "population that kept wanting democracy and stopped objecting to a strongman, which is a "
        "different claim from fearing democracy and points at performance rather than principle.",
        "Read the levels as instrument-specific: the Arab Opinion Index and World Values items ask for "
        "agreement with a statement and run high, Afrobarometer forces a choice between three and runs "
        "lower. The 2022 Afrobarometer round is in French and words the third item as 'rejection of "
        "dictatorship' rather than of one-man rule. Every point is a separate cross-section.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top), h_pad=4.0, w_pad=3.0)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"democracy-fear-claim.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"fear-claim: churchill {churchill[0][1]:.0%}..{churchill[-1][1]:.0%} (min {low_churchill[1]:.0%}), "
          f"one-man rejection {one_man[0][1]:.0%} -> {min(one_man, key=lambda p: p[1])[1]:.0%}")



# Afrobarometer's paired-statement items. Statement 1 is the one named first in the
# label, coded 1-2; Statement 2 is coded 3-4; 5 is "agree with neither". Note that
# "President free to act vs obey the laws and courts" puts the STRONGMAN option first,
# the opposite way round from every other item here — coding them all alike would
# reverse that one.
CONSTRAINTS = [
    ("President limited to two terms",
     r"two term limit|mandats du président à deux", [1, 2]),
    ("President must obey laws and courts",
     r"president free to act vs\.? obey|président est libre d'agir vs doit obéir", [3, 4]),
    ("President monitored by parliament",
     r"president monitored by parliament|rend compte au parlement", [1, 2]),
    ("Parliament makes the laws, not the president",
     r"parliament makes laws|parlement fait des lois", [1, 2]),
    ("Armed forces never intervene",
     r"armed forces never intervene|forces armées n'interviennent jamais", [1, 2]),
]
ELECTIONS = (r"choose leaders through.{0,20}election|choisir les dirigeants.{0,25}élections", [1, 2])
# The three constraint items asked in every round, so the index has a fixed composition.
INDEX_ITEMS = ("President limited to two terms", "President must obey laws and courts",
               "President monitored by parliament")


def paired_series(pattern: str, wanted: list[int]) -> list[tuple[int, float]]:
    points = []
    for key, survey in catalog().items():
        if survey["series"] != "afrobarometer":
            continue
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, meta = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        labels = {c: str(meta.column_names_to_labels.get(c) or "") for c in data.columns}
        column = next((c for c in data.columns if re.search(pattern, labels[c], re.I)), None)
        if column is None:
            continue
        weight = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)
        frame = pd.DataFrame({column: data[column], "weight": data[weight] if weight else 1.0})
        value = weighted_share(frame, column, wanted, [1, 2, 3, 4, 5])
        if np.isfinite(value):
            points.append((year_of(survey), value))
    return sorted(points)


def inside_legend(ax, where: str, size: float, ncol: int = 1, handleheight: float = 0.7):
    """Legend inside the panel on an opaque patch.

    Hung below the axes it lands on the tick labels, and reserving room for it with
    tight_layout does not survive a four-panel grid.
    """
    legend = ax.legend(loc=where, frameon=True, fontsize=size, labelcolor=INK_SOFT,
                       handlelength=1.5, handleheight=handleheight, ncol=ncol,
                       borderpad=0.5, labelspacing=0.4)
    legend.get_frame().set_facecolor(SURFACE)
    legend.get_frame().set_edgecolor("none")
    legend.get_frame().set_alpha(0.92)
    return legend


def strongman_figure() -> None:
    """Test the claim that Tunisians prefer strongman rule, on its own terms."""
    elections = paired_series(*ELECTIONS)
    constraints = {name: paired_series(pattern, wanted) for name, pattern, wanted in CONSTRAINTS}
    churchill = series_for("Q405_6", [1, 2], [1, 2, 3, 4], "arab-opinion-index")
    one_man = series_for(REJECT["One-man rule"], [1, 2], [1, 2, 3, 4, 5], "afrobarometer")
    one_man_full = []
    for key, survey in catalog().items():
        if survey["series"] != "afrobarometer":
            continue
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, meta = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        labels = {c: str(meta.column_names_to_labels.get(c) or "") for c in data.columns}
        column = next((c for c in data.columns if REJECT["One-man rule"].search(labels[c])), None)
        if column is None:
            continue
        weight = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)
        frame = pd.DataFrame({column: data[column], "weight": data[weight] if weight else 1.0})
        one_man_full.append((year_of(survey), {
            code: weighted_share(frame, column, [code], [1, 2, 3, 4, 5]) for code in (1, 2, 3, 4, 5)}))
    one_man_full.sort()

    index = []
    for year in [y for y, _ in elections]:
        values = [dict(points).get(year) for name, points in constraints.items()
                  if name in INDEX_ITEMS]
        values = [v for v in values if v is not None]
        if len(values) == len(INDEX_ITEMS):
            index.append((year, float(np.mean(values))))

    fig, axes = plt.subplots(2, 2, figsize=(15.0, 10.6), facecolor=SURFACE)
    axes = axes.ravel()

    ax = axes[0]
    ax.set_facecolor(SURFACE)
    line(ax, elections, PRIMARY, "Leaders should be chosen by election")
    line(ax, churchill, THIRD, "Democracy remains better than other systems (Arab Opinion Index)")
    line(ax, one_man, SECOND, "Disapproves of one-man rule", lift=-15.0)
    coup_line(ax)
    time_axis(ax)
    ax.set_title("Elections: still wanted", fontsize=10.4, color=INK, loc="left",
                 pad=10, fontweight="bold")
    inside_legend(ax, "lower left", 7.8)

    ax = axes[1]
    ax.set_facecolor(SURFACE)
    palette = (PRIMARY, SECOND, THIRD, "#4a3aa7", "#eda100")
    for i, (colour, (name, points)) in enumerate(zip(palette, constraints.items())):
        if points:
            # Five lines converging in a 20-point band cannot each carry an end label.
            line(ax, points, colour, name, annotate=False)
    coup_line(ax)
    time_axis(ax)
    ax.set_title("Constraints on the elected president: abandoned", fontsize=10.4, color=INK,
                 loc="left", pad=10, fontweight="bold")
    inside_legend(ax, "lower left", 7.4)

    ax = axes[2]
    ax.set_facecolor(SURFACE)
    years = [y for y, _ in index]
    ax.fill_between(years, [dict(elections)[y] for y in years], [v for _, v in index],
                    color="#e6ecf6", zorder=1)
    line(ax, [(y, dict(elections)[y]) for y in years], PRIMARY, "Leaders chosen by election")
    line(ax, index, SECOND, "Constraints on the president (mean of three items)")
    coup_line(ax)
    time_axis(ax)
    ax.set_title("The two come apart", fontsize=10.4, color=INK, loc="left",
                 pad=10, fontweight="bold")
    inside_legend(ax, "lower left", 7.8)

    ax = axes[3]
    ax.set_facecolor(SURFACE)
    years = [y for y, _ in one_man_full]
    up = np.zeros(len(years))
    down = np.zeros(len(years))
    for code, colour, label in ((1, DIVERGING[0], "Strongly disapprove"), (2, DIVERGING[1], "Disapprove")):
        values = np.array([p[1][code] for p in one_man_full])
        ax.bar(years, values, bottom=up, width=1.05, color=colour, edgecolor=SURFACE,
               linewidth=1.2, label=label)
        up = up + values
    for code, colour, label in ((4, DIVERGING[2], "Approve"), (5, DIVERGING[3], "Strongly approve")):
        values = np.array([p[1][code] for p in one_man_full])
        ax.bar(years, -values, bottom=down, width=1.05, color=colour, edgecolor=SURFACE,
               linewidth=1.2, label=label)
        down = down - values
    ax.axhline(0, color=INK_SOFT, lw=0.9, zorder=4)
    ax.set_ylim(-0.75, 1.12)
    ax.set_yticks([-0.6, -0.3, 0, 0.3, 0.6, 0.9])
    ax.set_yticklabels(["60%", "30%", "0", "30%", "60%", "90%"], fontsize=7.8)
    ax.set_xlim(2011.5, 2025.5)
    ax.set_xticks(years)
    ax.set_xticklabels(years, fontsize=7.8)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    ax.spines["bottom"].set_visible(False)
    ax.axvline(2021.0, color=INK, lw=1.1, ls=(0, (4, 3)), zorder=5)
    ax.set_title("'Only one leader, elections and parliament abolished'", fontsize=10.4,
                 color=INK, loc="left", pad=10, fontweight="bold")
    inside_legend(ax, "upper right", 7.8, ncol=2, handleheight=1.2)

    laws = constraints["Parliament makes the laws, not the president"]
    obey = constraints["President must obey laws and courts"]
    terms = constraints["President limited to two terms"]
    # How much of the decline is already done before the coup, computed rather than eyeballed.
    total = index[0][1] - index[-1][1]
    early = index[0][1] - index[2][1]
    # Where each item falls hardest. Only items measured in every round can be read this
    # way: the law-making item skips 2018 and 2020, so its worst "step" spans seven years.
    rounds = [y for y, _ in elections]
    steady = {name: points for name, points in
              list(constraints.items()) + [("Leaders chosen by election", elections)]
              if [y for y, _ in points] == rounds}
    worst = {}
    for name, points in steady.items():
        drops = [(points[i + 1][0], points[i + 1][1] - points[i][1]) for i in range(len(points) - 1)]
        worst[name] = min(drops, key=lambda d: d[1])[0]
    pre = sum(1 for y in worst.values() if y <= 2018)
    post = len(worst) - pre
    gap_first = dict(elections)[index[0][0]] - index[0][1]
    gap_last = dict(elections)[index[-1][0]] - index[-1][1]
    top = header(fig, "'Tunisians prefer strongman rule' — what the surveys actually say", [
        "The same six Afrobarometer rounds, separating two questions the claim runs together: who "
        "should choose the leader, and what the leader may then do. Weighted shares; the dashed line "
        "is 25 July 2021.",
        f"This claim does not fail the way the last one did. On everything to do with restraining the "
        f"president it is largely borne out: agreement that parliament rather than the president should "
        f"make the laws fell from {laws[0][1]:.0%} in {laws[0][0]} to {laws[-1][1]:.0%} in {laws[-1][0]}, "
        f"that the president must obey the laws and courts from {obey[0][1]:.0%} to {obey[-1][1]:.0%}, "
        f"and that he should be limited to two terms from {terms[0][1]:.0%} to {terms[-1][1]:.0%}. On the "
        "blunt item — one leader, elections and parliament abolished — approval has outweighed "
        "disapproval since 2020.",
        f"What survives is the vote. Agreement that leaders should be chosen through elections has "
        f"never fallen below {min(v for _, v in elections):.0%} and stands at {elections[-1][1]:.0%}, "
        f"while agreement that democracy remains the better system stands at {churchill[-1][1]:.0%}. The "
        f"gap between wanting elections and wanting the winner constrained widens from "
        f"{gap_first * 100:.0f} points in {index[0][0]} to {gap_last * 100:.0f} in {index[-1][0]}.",
        "So the accurate version is narrower and stranger than the claim: Tunisians want to elect a "
        "leader and then let him govern unchecked. That is a rejection of horizontal accountability "
        f"rather than of democracy, and most of it predates the coup — the index had already fallen "
        f"{early * 100:.0f} of its eventual {total * 100:.0f} points by {index[2][0]}, three years "
        "before parliament was suspended and under the elected governments those constraints belonged "
        f"to. Of the {len(worst)} items measured in every round, {pre} fall furthest in the step ending "
        f"2018 and {post} in the step ending 2022, so no single moment carries it.",
        "The index is the mean of the three constraint items asked in all six rounds, so its "
        "composition is fixed; the law-making item was not asked in 2018 or 2020 and its line is drawn "
        "with the gap. Round 10 recorded only agreement, not its strength, so its bars carry no "
        "'strongly' category, and the 2022 round is in French and words the blunt item as 'rejection of "
        "dictatorship' rather than of one-man rule. Every point is a separate cross-section.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top), h_pad=3.0, w_pad=3.0)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"democracy-strongman-claim.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"strongman: elections {elections[0][1]:.0%}->{elections[-1][1]:.0%}, "
          f"constraint index {index[0][1]:.0%}->{index[-1][1]:.0%}, gap {gap_first*100:.0f}->{gap_last*100:.0f}pts")



AOI_TRUST = {"Q201_6": "The army", "Q201_3": "Elected legislature", "Q201_5": "Political parties"}
INTERVENE = re.compile(r"armed forces never intervene|forces armées n'interviennent jamais", re.I)


def military_figure() -> None:
    """Test the claim that Tunisians want military rule, on its own terms."""
    approve = series_for(REJECT["Military rule"], [4, 5], [1, 2, 3, 4, 5], "afrobarometer")
    disapprove = series_for(REJECT["Military rule"], [1, 2], [1, 2, 3, 4, 5], "afrobarometer")
    one_man = series_for(REJECT["One-man rule"], [4, 5], [1, 2, 3, 4, 5], "afrobarometer")
    one_party = series_for(REJECT["One-party rule"], [4, 5], [1, 2, 3, 4, 5], "afrobarometer")
    wvs_army = (series_for("V129", [1, 2], [1, 2, 3, 4], "world-values-survey")
                + series_for("Q237", [1, 2], [1, 2, 3, 4], "world-values-survey"))
    wvs_army.sort()

    trust = {name: series_for(variable, [1, 2], [1, 2, 3, 4], "arab-opinion-index")
             for variable, name in AOI_TRUST.items()}
    never = paired_series(INTERVENE.pattern, [1, 2])
    when_abused = paired_series(INTERVENE.pattern, [3, 4])

    fig, axes = plt.subplots(2, 2, figsize=(15.0, 10.6), facecolor=SURFACE)
    axes = axes.ravel()

    ax = axes[0]
    ax.set_facecolor(SURFACE)
    line(ax, approve, SECOND, "Afrobarometer · approves of army rule")
    line(ax, disapprove, PRIMARY, "Afrobarometer · disapproves", lift=-16.0)
    line(ax, wvs_army, THIRD, "World Values Survey · 'the army rules' would be good", lift=-16.0)
    coup_line(ax)
    time_axis(ax)
    ax.set_title("The two instruments disagree", fontsize=10.4, color=INK, loc="left",
                 pad=10, fontweight="bold")
    inside_legend(ax, "lower left", 7.8)

    ax = axes[1]
    ax.set_facecolor(SURFACE)
    for colour, (name, points) in zip((PRIMARY, SECOND, THIRD), trust.items()):
        if points:
            line(ax, points, colour, name)
    coup_line(ax)
    time_axis(ax)
    ax.set_title("Trust in the army is a constant, not a variable", fontsize=10.4, color=INK,
                 loc="left", pad=10, fontweight="bold")
    inside_legend(ax, "center left", 7.8)

    ax = axes[2]
    ax.set_facecolor(SURFACE)
    line(ax, approve, SECOND, "Army rule")
    line(ax, one_man, PRIMARY, "One-man rule", lift=-16.0)
    line(ax, one_party, THIRD, "One-party rule", lift=-16.0)
    coup_line(ax)
    time_axis(ax)
    ax.set_title("Army rule rises — but less than one-man rule", fontsize=10.4, color=INK,
                 loc="left", pad=10, fontweight="bold")
    inside_legend(ax, "lower left", 7.8)

    ax = axes[3]
    ax.set_facecolor(SURFACE)
    years = [y for y, _ in never]
    ax.bar(years, [v for _, v in never], width=0.8, color=PRIMARY, edgecolor=SURFACE,
           linewidth=1.2, label="The armed forces should never intervene")
    ax.bar(years, [-v for _, v in when_abused], width=0.8, color=SECOND, edgecolor=SURFACE,
           linewidth=1.2, label="They should intervene when leaders abuse power")
    for year, value in never:
        ax.annotate(f"{value:.0%}", (year, value), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=8.4, color=INK, fontweight="bold")
    for year, value in when_abused:
        ax.annotate(f"{value:.0%}", (year, -value), textcoords="offset points", xytext=(0, -15),
                    ha="center", fontsize=8.4, color=INK, fontweight="bold")
    ax.axhline(0, color=INK_SOFT, lw=0.9, zorder=4)
    ax.set_ylim(-0.95, 0.75)
    ax.set_yticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5])
    ax.set_yticklabels(["75%", "50%", "25%", "0", "25%", "50%"], fontsize=7.8)
    ax.set_xlim(2020.8, 2025.2)
    ax.set_xticks(years)
    ax.set_xticklabels(years, fontsize=8.2)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    ax.spines["bottom"].set_visible(False)
    ax.set_title("Where it is consistent, it is conditional", fontsize=10.4, color=INK,
                 loc="left", pad=10, fontweight="bold")
    inside_legend(ax, "upper left", 7.8)

    # The crossing is not monotone, so "passes disapproval" needs the first year from
    # which it stays ahead in every later round — not merely the first year it leads.
    rounds = [y for y, _ in approve]
    up, down = dict(approve), dict(disapprove)
    durable = next(y for y in rounds if all(up[z] > down[z] for z in rounds if z >= y))
    level = [y for y, v in approve if abs(v - down[y]) < 0.01]
    army_trust = trust["The army"]
    legislature = trust["Elected legislature"]
    top = header(fig, "'Tunisians want military rule' — what the surveys actually say", [
        "Afrobarometer's approve/disapprove item against the World Values Survey's rating of the same "
        "system, alongside nine Arab Opinion Index rounds on trust. Weighted shares; the dashed line "
        "is 25 July 2021.",
        f"This one the archive cannot settle, because the two instruments that ask it disagree. On "
        f"Afrobarometer, approval of the army coming in to govern rises from {approve[0][1]:.0%} in "
        f"{approve[0][0]} to {approve[-1][1]:.0%} in {approve[-1][0]}, drawing level with disapproval "
        f"in {level[0]}, falling behind again in 2020, and standing clearly above it from {durable}. "
        "On the World Values Survey, "
        f"'the army rules' is called a good way of governing by {wvs_army[0][1]:.0%} in "
        f"{wvs_army[0][0]} and {wvs_army[-1][1]:.0%} in {wvs_army[-1][0]} — falling, not rising. The "
        f"two nearest readings are a year apart and {abs(dict(approve)[2020] - wvs_army[-1][1]) * 100:.0f} "
        "points apart.",
        f"What the usual explanation cannot do is carry the change. Trust in the army has been at the "
        f"ceiling throughout — {min(v for _, v in army_trust):.0%} to {max(v for _, v in army_trust):.0%} "
        f"across nine rounds, and already {army_trust[0][1]:.0%} in {army_trust[0][0]}, when approval of "
        "army rule was barely a third. A constant cannot explain a change. What moved is the other side "
        f"of the ledger: trust in the elected legislature fell from {legislature[0][1]:.0%} to "
        f"{min(v for _, v in legislature):.0%} at its floor.",
        f"And approval of army rule does not stand out from its neighbours. It rises "
        f"{(approve[-1][1] - approve[0][1]) * 100:.0f} points over the period against "
        f"{(one_man[-1][1] - one_man[0][1]) * 100:.0f} for one-man rule, so if anything the appetite "
        "is for a strong civilian rather than for the barracks. Where the sentiment is consistent it "
        "is conditional: "
        f"only {never[-1][1]:.0%} say in {never[-1][0]} that the armed forces should never intervene, "
        "but the alternative on offer is intervention 'when leaders abuse power' — a check of last "
        "resort, not a government.",
        "So the claim is not established here. It has real support on one instrument and none on the "
        "other, and the archive holds nothing to break the tie. Every point is a separate "
        "cross-section; the 2022 Afrobarometer round is in French.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top), h_pad=3.0, w_pad=3.0)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"democracy-military-claim.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"military: afro approve {approve[0][1]:.0%}->{approve[-1][1]:.0%}, "
          f"wvs good {wvs_army[0][1]:.0%}->{wvs_army[-1][1]:.0%}, "
          f"army trust {min(v for _, v in army_trust):.0%}-{max(v for _, v in army_trust):.0%}")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    afro = afrobarometer()
    timeline_figure(afro)
    ratings_figure(afro)
    who_figure(afro)
    meaning_figure()
    fear_figure()
    strongman_figure()
    military_figure()


if __name__ == "__main__":
    main()
