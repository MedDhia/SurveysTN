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

PRIMARY, SECOND = "#2a78d6", "#eb6834"
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


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    afro = afrobarometer()
    timeline_figure(afro)
    ratings_figure(afro)
    who_figure(afro)
    meaning_figure()


if __name__ == "__main__":
    main()
