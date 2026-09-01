#!/usr/bin/env python3
"""Economic and spatial inequality: what people go without, and where.

The other inequality figures ask what people *think* about equality. These ask what
they have, and where they live, using the two instruments in this archive that measure
material conditions rather than opinions about them.

**Lived poverty** — Afrobarometer's five "how often have you gone without" items (food,
clean water, medical care, cooking fuel, cash income), averaged on their 0-to-4 scale.
Six rounds, 2013 to 2024, in every one of Tunisia's seven statistical regions.

**Area provision** — Afrobarometer's enumeration-area checklist, recorded by the
interviewer rather than reported by the respondent: is there piped water, a sewage
system, a clinic, a bank, a paved road in this place. It is the only observational
measure of spatial inequality in the archive.

**Hardship by governorate** — the Arab Opinion Index's household-income question, which
is the only material measure the archive carries at governorate rather than region
resolution, pooled over eight rounds.

**Conditions against perception** — whether the map of what people go without matches
the map of where they say equality is not applied. It does, and the two maps come from
different programmes, different respondents and different years.

The Afrobarometer batteries are matched on their **question wording, never their variable
names**: the lived-poverty items are Q8A-E in Rounds 5 to 7, Q7A-E in Rounds 8 and 10,
and Q6A-E in Round 9 — where Q7A is instead "did not feel safe in the neighbourhood",
which a name-based match would silently fold into a poverty index.
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
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import PercentFormatter
from scipy import stats

from build_inequality_figures import (
    FIGURES, GRID, INK, INK_FAINT, INK_SOFT, ROOT, SURFACE, WEIGHTS,
    catalog, clip, frame_style, header, year_of,
)
from build_inequality_breakdowns import REGIONS, share

PRIMARY, SECOND, ACCENT = "#2a78d6", "#eb6834", "#104281"

# A governorate enters a figure only with this many effective respondents on the measure
# being drawn. Applied identically everywhere, so the figures agree on which places exist.
FLOOR = 150

# Matched on wording because Afrobarometer renumbers between rounds while keeping the
# Q prefix: Round 9's Q7A is a safety question, not a deprivation one.
LIVED_POVERTY = re.compile(
    r"gone without\s+(food|water|medical care|cooking fuel|cash income)"
    r"|manque\s+d[eu']?\s*(nourriture|eau potable|soins m|combustible|revenus)", re.I)
AREA = re.compile(r"^EA[-_](SVC|FAC|ROAD)[-_]([A-G])\b", re.I)
AMENITY = {
    "EA_SVC_A": "Electricity grid", "EA_SVC_B": "Piped water", "EA_SVC_C": "Sewage system",
    "EA_SVC_D": "Cell phone service", "EA_SVC_E": "Borehole or tubewell",
    "EA_FAC_A": "Post office", "EA_FAC_B": "School", "EA_FAC_C": "Police station",
    "EA_FAC_D": "Health clinic", "EA_FAC_E": "Market stalls", "EA_FAC_F": "Bank",
    "EA_FAC_G": "Paid transport",
}


def geography() -> tuple[dict, dict, dict, set]:
    spec = json.loads(REGIONS.read_text(encoding="utf-8"))
    governorate = {g: n for n, b in spec["regions"].items() for g in b["governorates"]}
    coastal = {n for n, b in spec["regions"].items() if b["coastal"]}
    return governorate, spec["region_variants"], spec["spelling_variants"], coastal


def code_for(codes: dict, *names: str):
    """Look a code up by label, tolerating a code of 0.

    ``codes.get("no") or codes.get("non")`` is wrong here and quietly so: Afrobarometer
    codes No as 0, which is falsy, so the fallback fires and returns None for every
    English round. That left one French round standing in for all six.
    """
    for name in names:
        if name in codes:
            return codes[name]
    return None


def labelled(frame: pd.DataFrame, meta, column: str) -> pd.Series:
    return frame[column].map(meta.variable_value_labels.get(column, {})).astype("string").str.strip()


def afrobarometer() -> pd.DataFrame:
    """One row per Afrobarometer respondent: region, lived poverty, area provision."""
    governorate, region_variants, spelling, _ = geography()
    frames = []
    for key, survey in catalog().items():
        if survey["series"] != "afrobarometer":
            continue
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, meta = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        labels = {c: str(meta.column_names_to_labels.get(c) or "") for c in data.columns}

        region = labelled(data, meta, upper["REGION"]).replace(spelling)
        region = region.map(lambda x: region_variants.get(x, governorate.get(x)))
        weight = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)
        block = pd.DataFrame({
            "survey": key, "year": year_of(survey), "region": region,
            "weight": data[weight] if weight else 1.0,
            "urban": (data[upper["URBRUR"]] == 1).astype(float).where(
                data[upper["URBRUR"]].isin([1, 2])),
        })

        items = [c for c in data.columns if LIVED_POVERTY.search(labels[c])]
        if len(items) == 5:
            scored = pd.concat([data[c].where(data[c].between(0, 4)) for c in items], axis=1)
            block["lived_poverty"] = scored.mean(axis=1)
        elif items:
            raise SystemExit(f"{key}: found {len(items)} lived-poverty items, expected 5 or 0")

        for column in data.columns:
            if not AREA.match(labels[column]) and not AREA.match(column):
                continue
            name = column.upper()
            if name not in AMENITY:
                continue
            codes = {str(v).lower(): k for k, v in meta.variable_value_labels.get(column, {}).items()}
            yes, no = code_for(codes, "yes", "oui"), code_for(codes, "no", "non")
            if yes is not None and no is not None:
                block[name] = (data[column] == yes).astype(float).where(data[column].isin([yes, no]))
        frames.append(block)
    return pd.concat(frames, ignore_index=True)


def opinion_index() -> pd.DataFrame:
    """One row per Arab Opinion Index respondent: governorate, region, equality, hardship."""
    governorate, _, spelling, _ = geography()
    dimensions = [f"Q422_{i}" for i in (1, 2, 3, 4, 5, 6, 7, 14)]
    frames = []
    for key, survey in catalog().items():
        if survey["series"] != "arab-opinion-index" or key == "aoi-2011":
            continue
        path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
        data, meta = pyreadstat.read_sav(str(path), user_missing=True)
        upper = {c.upper(): c for c in data.columns}
        names = labelled(data, meta, upper["Q3"]).replace(spelling)
        block = pd.DataFrame({
            "survey": key, "year": year_of(survey), "governorate": names,
            "region": names.map(governorate), "weight": data[upper["WEIGHT"]],
        })
        asked = [np.where(data[upper[v]].isin([1, 2]), 1.0,
                          np.where(data[upper[v]].isin([3, 4]), 0.0, np.nan))
                 for v in dimensions if v in upper]
        block["equality"] = np.nanmean(np.vstack(asked), axis=0)
        income = data[upper["Q1211"]]
        block["hardship"] = (income == 3).astype(float).where(income.isin([1, 2, 3]))
        frames.append(block)
    return pd.concat(frames, ignore_index=True)


def ordered_regions(afro: pd.DataFrame) -> list[str]:
    means = afro.groupby("region").apply(lambda g: share(g.rename(columns={"weight": "weight"}),
                                                         "lived_poverty")[0])
    return list(means.sort_values(ascending=False).index)


def poverty_figure(afro: pd.DataFrame) -> None:
    have = afro[afro["lived_poverty"].notna()]
    regions = ordered_regions(have)
    series = {
        r: [(y, share(g, "lived_poverty")[0]) for y, g in sorted(block.groupby("year"))]
        for r, block in have.groupby("region")
    }
    _, _, _, coastal = geography()

    cols = 4
    rows = int(np.ceil(len(regions) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(15.0, 3.0 * rows), facecolor=SURFACE)
    axes = np.atleast_1d(axes).ravel()
    for panel, region in enumerate(regions):
        ax = axes[panel]
        ax.set_facecolor(SURFACE)
        for other in regions:
            if other != region:
                xs, ys = zip(*series[other])
                ax.plot(xs, ys, color="#dcdbd6", lw=1.4, zorder=1)
        xs, ys = zip(*series[region])
        ax.plot(xs, ys, color=PRIMARY, lw=2.2, zorder=3)
        ax.plot(xs, ys, "o", color=PRIMARY, ms=5, mec=SURFACE, mew=1.2, zorder=4)
        for x, y in ((xs[0], ys[0]), (xs[-1], ys[-1])):
            ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 9),
                        ha="center", fontsize=7.6, color=INK, fontweight="bold")
        ax.set_ylim(0.2, 1.45)
        ax.set_yticks([0.25, 0.50, 0.75, 1.00, 1.25])
        ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00", "1.25"], fontsize=7.6)
        ax.set_xticks(list(xs))
        ax.set_xticklabels(list(xs), rotation=45, ha="right", fontsize=7.6)
        ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
        frame_style(ax)
        ax.set_title(f"{region}  ·  {'littoral' if region in coastal else 'interior'}",
                     fontsize=9.2, color=INK, loc="left", pad=6)
    for ax in axes[len(regions):]:
        ax.axis("off")

    worst, best = regions[0], regions[-1]
    # Generated rather than asserted: an eyeballed "rose everywhere" was wrong for one region.
    years = sorted({y for points in series.values() for y, _ in points})
    peak = max(years[1:], key=lambda y: sum(
        v for points in series.values() for py, v in points if py == y))
    rose = sum(1 for points in series.values()
               if dict(points).get(peak, 0) > dict(points).get(years[years.index(peak) - 1], 0))
    climb = max(series, key=lambda r: series[r][-1][1] - series[r][0][1])
    change = series[climb][0][1], series[climb][-1][1]
    top = header(fig, "What Tunisians go without, by region", [
        "Afrobarometer's Lived Poverty Index: how often a household went without food, clean water, "
        "medical care, cooking fuel or a cash income in the past year, averaged over the five items on "
        f"their 0-to-4 scale, so 0 is never and 1 is roughly 'just once or twice' on every item. "
        f"{len(have):,} respondents across six rounds, weighted. Panels are ordered worst to best and "
        "each carries the other six regions in grey.",
        f"{worst} and {regions[1]} — both interior — sit above every littoral region in almost every "
        f"round, and {best} sits lowest. {peak} is the exception: deprivation rose in {rose} of the "
        f"{len(regions)} regions that round and they converge, rather than the interior improving. The "
        f"steepest climb over the period is {climb}, from {change[0]:.2f} to {change[1]:.2f}.",
        "Littoral here is a development category rather than a coastline: the South East fronts the sea "
        "but is counted outside it, as in Tunisia's own regional accounts.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top), h_pad=2.6)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"spatial-lived-poverty.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"lived-poverty: {len(regions)} regions, {have['year'].nunique()} rounds, {len(have):,} respondents")


def provision_figure(afro: pd.DataFrame) -> None:
    present = [c for c in AMENITY if c in afro.columns and afro[c].notna().any()]
    table = pd.DataFrame({
        AMENITY[c]: {region: share(block, c)[0] for region, block in afro.groupby("region")}
        for c in present
    })
    table = table[table.mean().sort_values(ascending=False).index]
    table = table.loc[table.mean(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(1.05 * len(table.columns) + 6.0, 0.5 * len(table) + 4.4),
                           facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ramp = LinearSegmentedColormap.from_list(
        "blues", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"])
    grid = table.to_numpy(dtype=float)
    image = ax.imshow(grid, cmap=ramp, vmin=0, vmax=1, aspect="auto")
    for i in range(len(table)):
        for j in range(len(table.columns)):
            if np.isfinite(grid[i, j]):
                ax.text(j, i, f"{grid[i, j]:.0%}", ha="center", va="center", fontsize=8,
                        color="#ffffff" if grid[i, j] > 0.55 else INK)
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns, rotation=35, ha="right", fontsize=8.8, color=INK)
    ax.set_yticks(range(len(table)))
    ax.set_yticklabels(table.index, fontsize=8.8, color=INK)
    ax.set_xticks(np.arange(len(table.columns) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(table) + 1) - 0.5, minor=True)
    ax.grid(which="minor", color=SURFACE, lw=1.6)
    ax.tick_params(which="both", length=0)
    for side in ax.spines.values():
        side.set_visible(False)

    bank = table["Bank"] if "Bank" in table.columns else None
    extra = ""
    if bank is not None:
        extra = (f" A bank is in reach for {bank.max():.0%} of respondents in {bank.idxmax()} and "
                 f"{bank.min():.0%} in {bank.idxmin()}.")
    top = header(fig, "What is in the place, not what people think of it", [
        "Share of Afrobarometer respondents whose enumeration area contains each amenity, recorded by "
        f"the interviewer on arrival rather than reported by the respondent. {len(afro):,} respondents "
        "across six rounds, 2013 to 2024, weighted and pooled. Columns are ordered by national "
        "provision, rows by how well served the region is overall.",
        "This is the only measure of spatial inequality here that does not pass through an opinion." + extra
        + " Note what it is not: an enumeration area is where the interview happened, so this describes "
        "the places sampled, not the territory — and 'in the area' is a coarser thing than a household "
        "connection.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"spatial-provision.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"provision: {len(table)} regions x {len(table.columns)} amenities")


def hardship_figure(aoi: pd.DataFrame) -> None:
    governorate, _, _, coastal = geography()
    rows = []
    for name, block in aoi[aoi["governorate"].notna()].groupby("governorate"):
        mean, half, effective = share(block, "hardship")
        if effective >= FLOOR:
            rows.append((str(name), mean, half, effective, governorate.get(str(name))))
    rows.sort(key=lambda r: r[1])

    fig, ax = plt.subplots(figsize=(11.5, 0.40 * len(rows) + 3.8), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    national = share(aoi, "hardship")[0]
    ax.axvline(national, color=INK_FAINT, lw=1, ls=(0, (4, 3)), zorder=1)
    ys = [len(rows) - i for i in range(len(rows))]
    for y, row in zip(ys, rows):
        colour = SECOND if row[4] and row[4] not in coastal else PRIMARY
        ax.plot([row[1] - row[2], row[1] + row[2]], [y, y], color=colour, lw=2.4,
                alpha=0.45, solid_capstyle="round", zorder=2)
        ax.scatter([row[1]], [y], s=58, color=colour, edgecolor=SURFACE, linewidth=1.2, zorder=3)
        ax.annotate(f"{row[1]:.0%}", (row[1], y), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=7.8, color=INK, fontweight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r[0]}  ·  {r[4] or '—'}" for r in rows], fontsize=8.6, color=INK)
    ax.set_xlim(0.32, 0.76)
    ax.set_xticks(np.arange(0.35, 0.76, 0.05))
    ax.set_xticklabels([f"{x:.0%}" for x in np.arange(0.35, 0.76, 0.05)], fontsize=8.2)
    ax.set_ylim(0.3, len(rows) + 0.9)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    frame_style(ax)
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=t, markersize=7)
               for c, t in ((PRIMARY, "Littoral region"), (SECOND, "Interior region"))]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.004), ncol=2,
              frameon=False, fontsize=8.8, labelcolor=INK_SOFT)

    top = header(fig, "Where household income does not cover the household", [
        "Share saying their household income does not cover their requirements and they have difficulty "
        f"paying for necessities, by governorate, pooled over eight Arab Opinion Index rounds, "
        f"{len(aoi):,} respondents, 2012 to 2025. Weighted, with 95% intervals on Kish's effective "
        "sample size; the dashed line is the national share. Governorates with fewer than 150 effective "
        "respondents are left out.",
        f"This is the finest geography the archive supports for a material measure — Afrobarometer's "
        "lived-poverty items exist only at region level from Round 7 on. Interior governorates cluster "
        "at the hard end, but the split is not clean: the ranking runs through the littoral as well.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top))
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"economic-hardship-by-governorate.{suffix}", dpi=200,
                    facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"hardship: {len(rows)} governorates")


def conditions_figure(afro: pd.DataFrame, aoi: pd.DataFrame) -> None:
    """Does the map of what people go without match the map of where they feel unequal?"""
    _, _, _, coastal = geography()
    region = pd.DataFrame({
        "poverty": {r: share(g, "lived_poverty")[0] for r, g in afro.groupby("region")},
        "equality": {r: share(g, "equality")[0] for r, g in aoi.groupby("region")},
    }).dropna()
    gov = pd.DataFrame({
        "hardship": {str(n): share(g, "hardship")[0] for n, g in aoi.groupby("governorate")},
        "equality": {str(n): share(g, "equality")[0] for n, g in aoi.groupby("governorate")},
        "on_hardship": {str(n): share(g, "hardship")[2] for n, g in aoi.groupby("governorate")},
        "on_equality": {str(n): share(g, "equality")[2] for n, g in aoi.groupby("governorate")},
    }).dropna()
    total = len(gov)
    gov = gov[(gov["on_hardship"] >= FLOOR) & (gov["on_equality"] >= FLOOR)]

    fig, axes = plt.subplots(1, 2, figsize=(14.5, 6.6), facecolor=SURFACE)
    panels = [
        (axes[0], region, "poverty", "Lived Poverty Index (Afrobarometer)",
         "Seven regions · two programmes", True),
        (axes[1], gov, "hardship", "Income does not cover needs (Arab Opinion Index)",
         f"{len(gov)} of {total} governorates · one programme", False),
    ]
    stat_lines = []
    for ax, table, xcol, xlabel, note, annotate in panels:
        ax.set_facecolor(SURFACE)
        x, y = table[xcol].to_numpy(), table["equality"].to_numpy()
        rho = stats.spearmanr(x, y)
        stat_lines.append((note.split(" · ")[0], rho.statistic, rho.pvalue, len(table)))
        fit = np.poly1d(np.polyfit(x, y, 1))
        span = np.linspace(x.min(), x.max(), 20)
        ax.plot(span, fit(span), color=INK_FAINT, lw=1.4, ls=(0, (5, 3)), zorder=1)
        for name in table.index:
            colour = SECOND if annotate and name not in coastal else PRIMARY
            ax.scatter(table.loc[name, xcol], table.loc[name, "equality"], s=90 if annotate else 52,
                       color=colour, edgecolor=SURFACE, linewidth=1.3, zorder=3)
            if annotate or table.loc[name, xcol] in (table[xcol].max(), table[xcol].min()):
                ax.annotate(clip(str(name), 16), (table.loc[name, xcol], table.loc[name, "equality"]),
                            textcoords="offset points", xytext=(0, 11), ha="center",
                            fontsize=8.2, color=INK)
        ax.set_xlabel(xlabel, fontsize=8.8, color=INK_SOFT, labelpad=8)
        ax.set_ylabel("Share saying equality is applied", fontsize=8.8, color=INK_SOFT, labelpad=8)
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
        ax.tick_params(labelsize=8)
        if annotate:
            ax.legend(handles=[
                plt.Line2D([], [], marker="o", ls="", color=c, label=t, markersize=7)
                for c, t in ((PRIMARY, "Littoral region"), (SECOND, "Interior region"))],
                loc="upper right", frameon=False, fontsize=8.4, labelcolor=INK_SOFT)
        ax.grid(color=GRID, lw=0.8, zorder=0)
        frame_style(ax)
        ax.set_title(f"{note}   ·   Spearman ρ = {rho.statistic:+.2f}"
                     f"{'' if rho.pvalue >= 0.001 else ' (p < 0.001)'}"
                     f"{'' if rho.pvalue < 0.001 else f' (p = {rho.pvalue:.3f})'}",
                     fontsize=9.4, color=INK, loc="left", pad=10)

    left, right = stat_lines
    top = header(fig, "Where people go without is where they say equality is not applied", [
        "Each point is a place. The horizontal axis is a material measure, the vertical axis the share "
        "saying equality is applied across the eight dimensions the Arab Opinion Index asks about. "
        "Weighted throughout; the dashed line is an ordinary least-squares fit shown to guide the eye.",
        f"On the left the two axes come from different programmes, different respondents and different "
        f"years — Afrobarometer 2013-2024 against the Arab Opinion Index 2012-2025 — and still rank the "
        f"seven regions almost identically (ρ = {left[1]:+.2f}). That agreement is the point: neither "
        "survey could produce it alone. On the right the same relationship is re-run within one "
        f"programme across {right[3]} governorates, where it is weaker but holds (ρ = {right[1]:+.2f}, "
        f"p = {right[2]:.3f}).",
        "The interior is not simply the deprived end: it holds both the worst two regions and the best "
        "two, which is why the coast/interior line on its own explained so little in the earlier "
        "regional figure and this material axis explains so much more.",
        "Read it as association between places, not as an effect on people: seven points cannot carry "
        "much weight, both panels are ecological — they describe regions, not the individuals in them — "
        f"and nothing here identifies which way the relationship runs. A governorate enters only with "
        f"{FLOOR} effective respondents on both measures.",
    ])
    fig.tight_layout(rect=(0, 0, 1, top), w_pad=4.0)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"spatial-conditions-and-perception.{suffix}", dpi=200,
                    facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"conditions: region rho {left[1]:+.2f} (p={left[2]:.3f}), "
          f"governorate rho {right[1]:+.2f} (p={right[2]:.3f})")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    afro, aoi = afrobarometer(), opinion_index()
    poverty_figure(afro)
    provision_figure(afro)
    hardship_figure(aoi)
    conditions_figure(afro[afro["lived_poverty"].notna()], aoi)


if __name__ == "__main__":
    main()
