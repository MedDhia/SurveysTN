#!/usr/bin/env python3
"""Regime preference: what the archive says about the alternatives to democracy.

Every other topic in this repository has a figure. This one did not, and the reason is
worth stating: seven of the nine programmes carry an item on at least one of them, which
only one other question in the archive matches, and no two of the seven ask it the same
way. Pooling would have been easy and wrong.

So the figure does not pool. It plots every reading the archive holds on four
alternatives, one panel each, and encodes the **response frame** on the marker, because
the frame turns out to explain more of the spread than the year does. Four frames appear:

- a symmetric four-point good/bad scale (World Values Survey, SAHWA, Arab Opinion Index,
  Life in Transition, and Arab Barometer's expert item), drawn as a circle;
- a **lopsided** four-point scale on which three of the four options are shades of yes —
  "very / somewhat / absolutely inappropriate" in Arab Barometer Waves II and III,
  "very suitable / suitable / somewhat suitable / not suitable at all" in Wave VIII, and
  the same shape running the other way in Arab Transformations — drawn as a square, with
  a bar showing where the two defensible cuts fall;
- Afrobarometer's five-point approve/disapprove, drawn as a triangle, whose middle
  category is an explicit "neither".

A line joins consecutive readings only where the same programme used the same instrument.
Nothing is joined across programmes. Every marker is labelled with its programme, which
is also what makes the palette legible to a colourblind reader at this many series.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat

from build_coverage_figure import SERIES_COLOUR
from build_inequality_figures import (
    FIGURES, GRID, INK, INK_FAINT, INK_SOFT, ROOT, SHORT, SURFACE, WEIGHTS,
    catalog, frame_style, header, year_of,
)

# frame -> (marker, legend wording)
FRAMES = {
    "good": ("o", "Symmetric four-point: very good / fairly good / fairly bad / very bad"),
    "lopsided": ("s", "Lopsided four-point: three shades of yes against one no"),
    "approve": ("^", "Five-point approve / disapprove, with an explicit middle"),
}

# (survey, variable, frame, codes counted as support, the wider cut where the scale is
# lopsided, the substantive universe). The universe is always the four or five points of
# the scale itself: "don't know" and refusals are dropped rather than counted as no.
PANELS = [
    ("A strong leader, or an authority that need not\nheed elections or the opposition", [
        ("ab-w02", "q5183", "lopsided", [1, 2], [1, 2, 3], [1, 2, 3, 4]),
        ("ab-w03", "q5183", "lopsided", [1, 2], [1, 2, 3], [1, 2, 3, 4]),
        ("wvs-w06", "V127", "good", [1, 2], None, [1, 2, 3, 4]),
        ("arabtrans-w2014", "V27C", "lopsided", [3, 4], [2, 3, 4], [1, 2, 3, 4]),
        ("sahwa-w2015", "POL621A", "good", [1, 2], None, [1, 2, 3, 4]),
        ("wvs-w07", "Q235", "good", [1, 2], None, [1, 2, 3, 4]),
        ("lits-w04", "q408a", "good", [3, 4], None, [1, 2, 3, 4]),
        ("ab-w08", "Q518_3", "lopsided", [1, 2], [1, 2, 3], [1, 2, 3, 4]),
    ]),
    ("Unelected experts deciding what is\nbest for the country", [
        ("ab-w02", "q5173", "good", [1, 2], None, [1, 2, 3, 4]),
        ("wvs-w06", "V128", "good", [1, 2], None, [1, 2, 3, 4]),
        ("sahwa-w2015", "POL621B", "good", [1, 2], None, [1, 2, 3, 4]),
        ("wvs-w07", "Q236", "good", [1, 2], None, [1, 2, 3, 4]),
        ("aoi-2019-2020", "q2020_18_3", "good", [1, 2], None, [1, 2, 3, 4]),
    ]),
    ("Religious law, with no political\nparties and no elections", [
        ("ab-w02", "q5184", "lopsided", [1, 2], [1, 2, 3], [1, 2, 3, 4]),
        ("ab-w03", "q5184", "lopsided", [1, 2], [1, 2, 3], [1, 2, 3, 4]),
        ("afro-w05", "Q31D_ARB", "approve", [4, 5], None, [1, 2, 3, 4, 5]),
        ("arabtrans-w2014", "V27D", "lopsided", [3, 4], [2, 3, 4], [1, 2, 3, 4]),
        ("afro-w06", "Q28D_NAF", "approve", [4, 5], None, [1, 2, 3, 4, 5]),
        ("wvs-w07", "Q239", "good", [1, 2], None, [1, 2, 3, 4]),
        ("lits-w04", "q408e", "good", [3, 4], None, [1, 2, 3, 4]),
        ("ab-w08", "Q518_4", "lopsided", [1, 2], [1, 2, 3], [1, 2, 3, 4]),
    ]),
    ("The army ruling", [
        ("afro-w05", "Q31B", "approve", [4, 5], None, [1, 2, 3, 4, 5]),
        ("wvs-w06", "V129", "good", [1, 2], None, [1, 2, 3, 4]),
        ("afro-w06", "Q28B", "approve", [4, 5], None, [1, 2, 3, 4, 5]),
        ("afro-w07", "Q27B", "approve", [4, 5], None, [1, 2, 3, 4, 5]),
        ("wvs-w07", "Q237", "good", [1, 2], None, [1, 2, 3, 4]),
        ("afro-w08", "Q20B", "approve", [4, 5], None, [1, 2, 3, 4, 5]),
        ("lits-w04", "q408c", "good", [3, 4], None, [1, 2, 3, 4]),
        ("afro-w10", "Q21B", "approve", [4, 5], None, [1, 2, 3, 4, 5]),
    ]),
]

# The three surveys with no weight variable of any kind. Naming them here rather than
# testing for absence keeps a renamed weight column from passing silently as "unweighted".
UNWEIGHTED = {"wvs-w06", "arabtrans-w2014", "issp-w2018"}


def reading(key: str, variable: str, frame: str, support: list[int],
            wider: list[int] | None, universe: list[int]) -> dict:
    """One survey's share supporting one alternative, on its own scale."""
    survey = catalog()[key]
    path = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
    data, _ = pyreadstat.read_sav(str(path), user_missing=True)
    upper = {c.upper(): c for c in data.columns}
    column = upper[variable.upper()]
    name = next((upper[w.upper()] for w in WEIGHTS if w.upper() in upper), None)
    if name is None and key not in UNWEIGHTED:
        raise SystemExit(f"{key}: no weight found, and it is not one of the unweighted three")
    weight = data[name].astype(float) if name else pd.Series(1.0, index=data.index)
    values = pd.to_numeric(data[column], errors="coerce")
    keep = values.isin(universe)
    if not keep.any():
        raise SystemExit(f"{key}/{variable}: no substantive answers")

    def cut(codes: list[int]) -> float:
        return float((values[keep].isin(codes) * weight[keep]).sum() / weight[keep].sum())

    return {
        "survey": key, "series": survey["series"], "year": year_of(survey),
        "variable": column, "frame": frame, "support": cut(support),
        "wider": cut(wider) if wider else np.nan, "n": int(keep.sum()),
        "weighted": name is not None,
    }


def panel_rows() -> list[tuple[str, pd.DataFrame]]:
    return [(title, pd.DataFrame([reading(*row) for row in rows]).sort_values("year"))
            for title, rows in PANELS]


def draw(ax, frame: pd.DataFrame) -> None:
    ax.set_facecolor(SURFACE)
    # A line only where one programme used one instrument more than once. Matching on the
    # frame as well as the series is what keeps Arab Barometer's expert item, on the
    # symmetric scale, from being joined to its strong-authority item on the lopsided one.
    for (series, kind), block in frame.groupby(["series", "frame"], sort=False):
        # And only between readings close enough in time to be consecutive askings. Arab
        # Barometer put the strong-authority item to Tunisians in 2013 and not again until
        # 2023; a segment drawn across that decade would assert a path through years the
        # archive holds nothing for.
        run = block.sort_values("year")
        for (_, a), (_, b) in zip(run.iterrows(), run.iloc[1:].iterrows()):
            if b["year"] - a["year"] <= 6:
                ax.plot([a["year"], b["year"]], [a["support"], b["support"]],
                        color=SERIES_COLOUR[series], lw=1.6, alpha=0.55, zorder=2)
    # Readings land in clusters — three programmes inside two years, twice — and a label
    # printed at a fixed offset above each marker collides with its neighbours. Labels are
    # therefore placed at a preferred height and then pushed apart until no two that share
    # a stretch of the axis are closer than one label's height; a leader line is drawn
    # wherever that push moved one far enough to be ambiguous.
    ordered = frame.sort_values("year")
    tops = {i: max(row["support"], row["wider"] if np.isfinite(row["wider"]) else 0)
            for i, row in ordered.iterrows()}
    place = {i: top + 0.045 for i, top in tops.items()}
    for _ in range(4 * len(place)):
        moved = False
        for a in place:
            for b in place:
                if a == b or abs(ordered.loc[a, "year"] - ordered.loc[b, "year"]) >= 1.7:
                    continue
                # A label must clear its neighbour's label, and also its neighbour's
                # marker: spacing labels against each other alone still lets one land on
                # a dot that happens to sit between them.
                if 0 <= place[b] - place[a] < 0.135:
                    place[b] = place[a] + 0.135
                    moved = True
                if tops[a] - 0.055 < place[b] < tops[a] + 0.025:
                    place[b] = tops[a] + 0.055
                    moved = True
        if not moved:
            break

    for index, row in frame.iterrows():
        colour = SERIES_COLOUR[row["series"]]
        if np.isfinite(row["wider"]):
            ax.plot([row["year"], row["year"]], [row["support"], row["wider"]], color=colour,
                    lw=1.4, alpha=0.75, zorder=3)
            ax.scatter([row["year"]], [row["wider"]], s=52, facecolor=SURFACE,
                       edgecolor=colour, linewidth=1.5, marker=FRAMES[row["frame"]][0], zorder=4)
        ax.scatter([row["year"]], [row["support"]], s=62, color=colour, edgecolor=SURFACE,
                   linewidth=1.1, marker=FRAMES[row["frame"]][0], zorder=5)
        at = place[index]
        if at - tops[index] > 0.075:
            ax.plot([row["year"], row["year"]], [tops[index] + 0.012, at - 0.008],
                    color=INK_FAINT, lw=0.7, alpha=0.7, zorder=2)
        ax.annotate(f"{SHORT[row['series']]}  {row['support']:.0%}", (row["year"], at),
                    ha="center", va="bottom", fontsize=7.2, color=INK_SOFT, zorder=6)

    ax.set_xlim(2008.8, 2025.6)
    ax.set_xticks(range(2010, 2026, 3))
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0", "25%", "50%", "75%", "100%"], fontsize=7.8)
    ax.tick_params(labelsize=7.8)
    ax.grid(color=GRID, lw=0.8, zorder=0)
    frame_style(ax)


def alternatives_figure() -> None:
    panels = panel_rows()
    fig, axes = plt.subplots(2, 2, figsize=(15.0, 10.6), facecolor=SURFACE)
    for ax, (title, frame) in zip(axes.ravel(), panels):
        draw(ax, frame)
        ax.set_title(title, fontsize=10.0, color=INK, loc="left", pad=10, fontweight="bold")

    everything = pd.concat([f for _, f in panels], ignore_index=True)
    strong = panels[0][1].set_index("survey")
    experts = panels[1][1]
    army = panels[3][1].set_index("survey")
    gap13 = abs(strong.loc["wvs-w06", "support"] - strong.loc["ab-w03", "support"])
    widest = everything.assign(spread=everything["wider"] - everything["support"]).nlargest(
        1, "spread").iloc[0]
    top = header(fig, "The alternatives to democracy: every reading the archive holds, and why "
                      "they will not line up", [
        "Seven of the nine programmes ask whether some non-democratic system would be good, "
        "suitable, appropriate or approved of. Only one other question in the archive reaches as "
        "many programmes — whether the gap between rich and poor is too large — and no two of the "
        "seven ask this one the same way. Weighted where a weight exists; each marker is "
        "one survey, its shape the shape of the answer scale it was measured on. Lines join "
        "readings only within one programme and one instrument.",
        f"The spread tracks the question, not the year. In 2013 two surveys nine months apart "
        f"read the strong-authority item {gap13 * 100:.0f} points apart: Arab Barometer Wave III, "
        f"in the field in February and March, has {strong.loc['ab-w03', 'support']:.0%} calling it "
        f"appropriate; the World Values Survey, in November and December, has "
        f"{strong.loc['wvs-w06', 'support']:.0%} calling it good. Neither is wrong. They are not "
        "the same measurement, and a trend line drawn through both would be an artefact of the "
        "instrument.",
        f"The lopsided scales are the clearest case, and the bars show it rather than assert it. "
        f"Where three of four options are shades of yes, the analyst's choice of cut moves the "
        f"answer by up to {(widest['wider'] - widest['support']) * 100:.0f} points on a single "
        f"survey — {SHORT[widest['series']]} in {widest['year']} reads "
        f"{widest['support']:.0%} or {widest['wider']:.0%} for the same respondents, depending on "
        "whether the middle 'somewhat' counts as support. This archive reports the strict cut and "
        "draws the other.",
        f"What does survive the disagreement is a ranking. Rule by unelected experts is the "
        f"popular alternative — never below {experts['support'].min():.0%} in any of the "
        f"{len(experts)} readings from {experts['series'].nunique()} programmes, and above "
        f"{experts['support'].max():.0%} at its height — while a strong leader and religious rule "
        "without elections sit far below it on every instrument that asks about more than one. "
        "Technocracy, not the strongman, is the alternative Tunisians say they would accept, and "
        "it is the one least discussed.",
        "Three caveats travel with the panels. Two of the surveys drawn here — the World Values "
        "Survey's 2013 wave and Arab Transformations — carry no weight variable of any kind, and "
        "are drawn unweighted; every other marker is weighted. SAHWA interviewed only "
        "15-to-29-year-olds, so its two markers are a youth reading beside national ones. And "
        "Afrobarometer's army item is the same one drawn in democracy-military-claim, repeated "
        "here so the four alternatives can be compared on one page.",
    ])
    # The marker key belongs with the standfirst, not inside a panel, because it explains
    # all four. It is hung from the fraction ``header`` stopped at and the plotting area
    # is pulled down by its own height, half an inch for two rows.
    handles = [plt.Line2D([], [], marker=marker, ls="", color=INK_SOFT, markersize=7,
                          markeredgecolor=SURFACE, label=text)
               for marker, text in FRAMES.values()]
    handles.append(plt.Line2D([], [], marker="s", ls="", markerfacecolor=SURFACE,
                              markeredgecolor=INK_SOFT, markersize=7,
                              label="Hollow: the wider cut the lopsided scale also allows"))
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.012, top), ncol=2,
               frameon=False, fontsize=8.0, labelcolor=INK_SOFT, handlelength=1.4,
               columnspacing=2.4)
    fig.tight_layout(rect=(0, 0, 1, top - 0.50 / fig.get_figheight()), h_pad=3.4, w_pad=3.0)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"regime-alternatives.{suffix}", dpi=200, facecolor=SURFACE,
                    bbox_inches="tight")
    plt.close(fig)

    out = everything.copy()
    out.insert(0, "alternative", sum(([title.replace("\n", " ")] * len(f)
                                      for title, f in panels), []))
    out.to_csv(FIGURES / "regime-alternatives.csv", index=False)
    print(f"alternatives: {len(out)} readings, {out['series'].nunique()} programmes, "
          f"{out['survey'].nunique()} surveys; 2013 strong-authority gap {gap13 * 100:.0f}pts")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    alternatives_figure()


if __name__ == "__main__":
    main()
