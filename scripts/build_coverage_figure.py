#!/usr/bin/env python3
"""Draw when Tunisian survey fieldwork actually happened.

The archive spans 2010 to 2025, but it does not cover it. Twelve of the
twenty-five surveys record an interview date per respondent, so for those the days
in the field are known exactly. One records only the month fieldwork opened and
closed. The other twelve record nothing, and all that is known is the year range
the publisher prints on the release.

The figure keeps those three levels of knowledge visually distinct, because a
chart that drew them alike would claim day-level coverage the archive does not
have. Writes ``main/figures/fieldwork-coverage.png``, ``.svg``, and the day-level
counts behind it as ``fieldwork-coverage-days.csv``.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import pyreadstat

from extract_tunisia import ROOT, wave_tag

FIGURES = ROOT / "main" / "figures"

SERIES_ORDER = ["arab-barometer", "world-values-survey", "afrobarometer", "arab-opinion-index"]
SERIES_COLOUR = {
    "arab-barometer": "#2a78d6",
    "world-values-survey": "#eb6834",
    "afrobarometer": "#1baf7a",
    "arab-opinion-index": "#4a3aa7",
}
INK = "#0b0b0b"
INK_SOFT = "#52514e"
INK_FAINT = "#8a8984"
SURFACE = "#fcfcfb"
GRID = "#e4e3df"

# A fortnight of fieldwork is a third of a percent of a sixteen-year axis, so a
# true-width bar would be invisible. Windows are widened to a floor purely so they
# can be seen; the exact span and day count are printed beside every row.
MIN_DRAWN_DAYS = 40


def interview_days(survey: dict, spec: dict) -> pd.Series | None:
    """Interviews per calendar day, or None if the release records no date."""
    var = spec.get("fieldwork_date_var")
    if not var:
        return None
    sav = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
    renamed = survey.get("renamed_variables", {})
    column = renamed.get(var, var)
    frame, _ = pyreadstat.read_sav(str(sav), usecols=[column])
    values = frame[column]
    fmt = spec.get("fieldwork_date_format")
    if fmt:
        values = values.astype("Int64").astype(str)
    parsed = pd.to_datetime(values, format=fmt, errors="coerce").dropna()
    if parsed.empty:
        return None
    return parsed.dt.date.value_counts().sort_index()


def month_span(spec: dict, survey: dict) -> tuple[date, date] | None:
    """First and last day of the months a release says fieldwork ran between."""
    if not spec.get("fieldwork_month_vars"):
        return None
    sav = ROOT / survey["path"] / f"{survey['series']}-{survey['tag']}-tunisia.sav"
    first, last = spec["fieldwork_month_vars"]
    frame, _ = pyreadstat.read_sav(str(sav), usecols=[first, last])
    start = pd.to_datetime(str(int(frame[first].dropna().min())), format="%Y%m")
    end = pd.to_datetime(str(int(frame[last].dropna().max())), format="%Y%m")
    return start.date(), (end + pd.offsets.MonthEnd(0)).date()


def year_span(spec: dict) -> tuple[date, date]:
    years = [int(y) for y in str(spec["fieldwork_years_series"]).split("-") if y.strip().isdigit()]
    return date(years[0], 1, 1), date(years[-1], 12, 31)


def runs(days: list[date]) -> list[tuple[date, date]]:
    """Collapse a sorted list of days into contiguous stretches."""
    out: list[tuple[date, date]] = []
    for day in days:
        if out and day - out[-1][1] <= timedelta(days=1):
            out[-1] = (out[-1][0], day)
        else:
            out.append((day, day))
    return out


def gather() -> tuple[list[dict], pd.DataFrame]:
    catalog = json.loads((ROOT / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "catalog" / "sources.json").read_text(encoding="utf-8"))
    specs = {(w["series"], wave_tag(w)): w for w in manifest["waves"]}

    rows, day_records = [], []
    for survey in catalog["surveys"]:
        spec = specs[(survey["series"], survey["tag"])]
        row = {
            "series": survey["series"],
            "tag": survey["tag"],
            "label": f"{survey['series_name'].replace('World Values Survey', 'WVS')} {survey['wave_label']}",
            "respondents": survey["n_respondents"],
        }

        counts = interview_days(survey, spec)
        if counts is not None:
            row["precision"] = "day"
            row["days"] = list(counts.index)
            row["n_days"] = len(counts)
            row["start"], row["end"] = counts.index[0], counts.index[-1]
            for day, n in counts.items():
                day_records.append(
                    {"date": day, "series": survey["series"], "survey": survey["tag"],
                     "interviews": int(n)}
                )
        elif (span := month_span(spec, survey)) is not None:
            row["precision"] = "month"
            row["days"], row["n_days"] = [], None
            row["start"], row["end"] = span
        else:
            row["precision"] = "year"
            row["days"], row["n_days"] = [], None
            row["start"], row["end"] = year_span(spec)
        rows.append(row)

    rows.sort(key=lambda r: (SERIES_ORDER.index(r["series"]), r["start"]))
    return rows, pd.DataFrame(day_records).sort_values(["date", "survey"])


def span_text(row: dict) -> str:
    start, end = row["start"], row["end"]
    if row["precision"] == "day":
        if start == end:
            return f"{start:%-d %b %Y} · 1 day"
        same_year = start.year == end.year
        left = f"{start:%-d %b}" if same_year else f"{start:%-d %b %Y}"
        return f"{left} – {end:%-d %b %Y} · {row['n_days']} days"
    if row["precision"] == "month":
        return f"{start:%b} – {end:%b %Y} · month only"
    return (
        f"{start:%Y}" if start.year == end.year else f"{start:%Y}–{end:%Y}"
    ) + " · year only"


def draw(rows: list[dict], days: pd.DataFrame) -> None:
    x_min, x_max = date(2010, 1, 1), date(2026, 6, 30)
    fig = plt.figure(figsize=(15.5, 11.6), facecolor=SURFACE)
    grid = fig.add_gridspec(
        2, 1, height_ratios=[8.2, 1], hspace=0.06, left=0.215, right=0.795, top=0.868, bottom=0.085
    )
    ax = fig.add_subplot(grid[0], facecolor=SURFACE)
    ax_n = fig.add_subplot(grid[1], facecolor=SURFACE, sharex=ax)

    # One row per survey, newest at the top of each series block.
    positions, y, boundaries = {}, 0.0, []
    for i, row in enumerate(rows):
        if i and row["series"] != rows[i - 1]["series"]:
            boundaries.append(y + 0.5)
            y += 1.0
        positions[row["tag"] + row["series"]] = y
        y += 1.0
    height = y

    for row in rows:
        pos = height - positions[row["tag"] + row["series"]]
        colour = SERIES_COLOUR[row["series"]]

        if row["precision"] == "day":
            for first, last in runs(row["days"]):
                width = max((last - first).days + 1, MIN_DRAWN_DAYS)
                ax.barh(pos, width, left=first, height=0.62, color=colour,
                        edgecolor="none", zorder=3)
        else:
            width = max((row["end"] - row["start"]).days + 1, MIN_DRAWN_DAYS)
            hatch = "///" if row["precision"] == "month" else None
            ax.barh(
                pos, width, left=row["start"], height=0.62,
                facecolor=colour + "26" if row["precision"] == "year" else colour + "40",
                edgecolor=colour, linewidth=1.2, hatch=hatch, zorder=3,
            )

        ax.text(mdates.date2num(x_max) + 40, pos, span_text(row), va="center", ha="left",
                fontsize=8.3, color=INK_SOFT if row["precision"] == "day" else INK_FAINT)

    ax.set_yticks([height - positions[r["tag"] + r["series"]] for r in rows])
    ax.set_yticklabels([r["label"] for r in rows], fontsize=8.6, color=INK)
    ax.set_ylim(-0.4, height + 0.9)

    for boundary in boundaries:
        ax.axhline(height - boundary + 0.5, color=GRID, linewidth=1, zorder=1)

    # The days themselves, and how many surveys were running on each.
    if not days.empty:
        per_day = days.groupby("date")["survey"].nunique()
        ax_n.bar(list(per_day.index), list(per_day.values), width=8,
                 color=INK_SOFT, edgecolor="none", zorder=3)
        ax_n.set_ylim(0, 1.35)
        ax_n.set_yticks([0, 1])
        if int(per_day.max()) == 1:
            ax_n.text(
                mdates.date2num(x_max), 1.22,
                "never more than one survey in the field at a time",
                ha="right", va="center", fontsize=8.4, color=INK_FAINT,
            )
    ax_n.set_ylabel("surveys\nin field", fontsize=8.3, color=INK_SOFT, labelpad=8)
    ax_n.tick_params(axis="y", labelsize=8, colors=INK_SOFT)

    for axis in (ax, ax_n):
        axis.set_xlim(x_min, x_max)
        axis.xaxis.set_major_locator(mdates.YearLocator())
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        axis.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
        for side in ("top", "right", "left"):
            axis.spines[side].set_visible(False)
        axis.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", labelbottom=False, length=0)
    ax.tick_params(axis="y", length=0)
    ax_n.tick_params(axis="x", labelsize=8.6, colors=INK_SOFT, length=0)

    n_day = sum(1 for r in rows if r["precision"] == "day")
    covered = days["date"].nunique() if not days.empty else 0
    dated = sum(r["respondents"] for r in rows if r["precision"] == "day")
    gap = 0
    if not days.empty:
        stamps = pd.Series(sorted(days["date"].unique()))
        gap = int(pd.to_datetime(stamps).diff().dt.days.max() or 0)
    fig.text(0.215, 0.968, "Which days Tunisian survey fieldwork actually covers",
             fontsize=16, color=INK, fontweight="bold", ha="left")
    fig.text(
        0.215, 0.944,
        f"{len(rows)} surveys over sixteen years. Only {n_day} record an interview date per "
        f"respondent, and between them they cover {covered:,} days — "
        f"{dated:,} of the archive's {sum(r['respondents'] for r in rows):,} interviews.",
        fontsize=10, color=INK_SOFT, ha="left",
    )
    fig.text(
        0.215, 0.925,
        f"The rest are drawn at the resolution their release supports. The longest gap between two covered days is {gap:,} days.",
        fontsize=10, color=INK_SOFT, ha="left",
    )

    legend = [
        mpatches.Patch(facecolor=INK_SOFT, label="Interview dates recorded — days in the field are exact"),
        mpatches.Patch(facecolor="#52514e40", edgecolor=INK_SOFT, hatch="///", label="Fieldwork month only"),
        mpatches.Patch(facecolor="#52514e26", edgecolor=INK_SOFT, label="Year of the wave only — no dates in the release"),
    ]
    ax.legend(handles=legend, loc="lower left", bbox_to_anchor=(0, 1.012), ncol=3,
              frameon=False, fontsize=8.8, labelcolor=INK_SOFT, handlelength=1.6,
              columnspacing=2.2, handletextpad=0.7)

    fig.text(0.215, 0.036,
             f"A window shorter than {MIN_DRAWN_DAYS} days is widened so it stays visible at this scale, "
             "so bar length is not readable as duration — the exact span and day count are printed beside each row.",
             fontsize=8.2, color=INK_FAINT, ha="left")
    fig.text(0.215, 0.017, "SurveysTN · scripts/build_coverage_figure.py · data in main/figures/fieldwork-coverage-days.csv",
             fontsize=8.2, color=INK_FAINT, ha="left")

    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg"):
        fig.savefig(FIGURES / f"fieldwork-coverage.{suffix}", dpi=200,
                    facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    rows, days = gather()
    FIGURES.mkdir(parents=True, exist_ok=True)
    days.to_csv(FIGURES / "fieldwork-coverage-days.csv", index=False)

    pd.DataFrame(
        [
            {k: v for k, v in r.items() if k != "days"}
            | {"span": span_text(r)}
            for r in rows
        ]
    ).to_csv(FIGURES / "fieldwork-coverage-surveys.csv", index=False)

    draw(rows, days)

    by = pd.Series([r["precision"] for r in rows]).value_counts()
    print(f"surveys: {len(rows)}  ({dict(by)})")
    print(f"distinct days with at least one interview: {days['date'].nunique():,}")
    print(f"wrote {FIGURES.relative_to(ROOT)}/fieldwork-coverage.png / .svg / two CSVs")


if __name__ == "__main__":
    main()
