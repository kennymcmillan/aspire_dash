"""Rank over time for ranked sports (v0.108, promoted from High Management Overview).

    rank_series_from_record(sport, payload)   {board: [(iso_date, rank)]} from a Sports API athlete record
    rank_titles_from_record(sport, payload)   [(iso_date, title name)]
    rank_over_time_figure(series, titles)     the figure: LINEAR axis, best rank on top, career high + now
                                              labelled, titles as stars on the main line
    rank_over_time(series, titles, ...)       the section (heading, graph, note); None when there is no series
    rank_small_multiples(series, mode)        v0.110: one small chart per list ("lists") or per source ("sources")

Kenny 2026-10-13: "dont use log scale" for rank charts. The axis runs from the worst rank shown at the bottom to
#1 at the top. Supported record shapes (payload.<sport>): squash ranking_history (PSA, '01 Oct 2011' dates),
fencing ranking_history (best rank per season and board), padel ranking_history_by_group ({board: [{date, rank}]}),
table tennis ranking_history (year + ISO week, per event and age category). Duplicate rows are dropped.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import plotly.graph_objects as go
from dash import dcc, html

from ..charts import apply_template

__all__ = ["RANKED_SPORTS", "rank_series_from_record", "rank_titles_from_record", "rank_over_time_figure",
           "rank_over_time", "rank_small_multiples", "rank_sources"]

RANKED_SPORTS = ("squash", "fencing", "padel", "tabletennis")
COLOURS = ("#004185", "#0f7a6e", "#b06a35", "#6b7a90")
GOLD, GOLD_EDGE = "#d4a017", "#7a5b00"


def _iso(d) -> Optional[str]:
    s = str(d or "").strip()
    for fmt in ("%Y-%m-%d", "%d %b %Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s[:19] if "T" in s else s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _clean(rows) -> list[tuple[str, int]]:
    seen, out = set(), []
    for d, r in rows:
        if d and isinstance(r, (int, float)) and not isinstance(r, bool) and r > 0 and (d, int(r)) not in seen:
            seen.add((d, int(r)))
            out.append((d, int(r)))
    return sorted(out)


def rank_series_from_record(sport: str, payload: dict) -> dict[str, list[tuple[str, int]]]:
    """One series per ranking board, each sorted by date. Empty boards are dropped."""
    blk = (payload or {}).get(sport) or {}
    out: dict[str, list] = {}
    if sport == "squash":
        rows = [(_iso(r.get("date")), r.get("rank")) for r in blk.get("ranking_history") or []]
        if rows:
            out["World (PSA)"] = _clean(rows)
    elif sport == "fencing":
        best: dict[tuple, int] = {}               # the grouped history holds scrape-date snapshots: best per season
        for r in blk.get("ranking_history") or []:
            season, rank = str(r.get("season") or "")[:4], r.get("rank")
            if not season.isdigit() or not isinstance(rank, (int, float)):
                continue
            key = (f"{r.get('band') or ''} {r.get('weapon') or ''} ({r.get('source') or 'FIE'})".strip(), season)
            best[key] = min(best.get(key, 10 ** 9), int(rank))
        for (board, season), rank in best.items():
            out.setdefault(board, []).append((f"{season}-07-01", rank))
        out = {k: _clean(v) for k, v in out.items()}
    elif sport == "padel":
        for board, rows in (blk.get("ranking_history_by_group") or {}).items():
            out[board] = _clean([(_iso(r.get("date")), r.get("rank")) for r in rows or []])
    elif sport == "tabletennis":
        groups: dict[str, list] = {}
        for r in blk.get("ranking_history") or []:
            try:
                d = date.fromisocalendar(int(r["year"]), max(1, min(52, int(r["week"]))), 1).isoformat()
            except (KeyError, TypeError, ValueError):
                continue
            label = f"{r.get('event_name') or r.get('event') or 'Ranking'} ({r.get('category') or '-'})"
            groups.setdefault(label, []).append((d, r.get("rank")))
        out = {k: _clean(v) for k, v in groups.items()}
    return {k: v for k, v in out.items() if v}


def rank_titles_from_record(sport: str, payload: dict) -> list[tuple[str, str]]:
    """Dated titles: honours.wins (squash, fencing, TT; honours.titles is a count) or padel titles_finals.titles."""
    blk = (payload or {}).get(sport) or {}
    raw = ((blk.get("honours") or {}).get("wins") if sport != "padel" else (blk.get("titles_finals") or {}).get("titles"))
    out = []
    for t in raw if isinstance(raw, list) else []:
        if not isinstance(t, dict):
            continue
        d = _iso(t.get("date"))
        name = t.get("tournament") or t.get("comp") or t.get("competition") or t.get("event")
        if d and name:
            out.append((d, str(name)))
    return sorted(out)


def _pick(series: dict, max_lines: int) -> dict:
    """The most recently active boards first, at most ``max_lines``."""
    return dict(sorted(series.items(), key=lambda kv: kv[1][-1][0], reverse=True)[:max_lines])


def rank_over_time_figure(series: dict, titles: Optional[list] = None, *, max_lines: int = 3,
                          height: int = 300) -> go.Figure:
    """``series``: {label: [(iso_date, rank)]} (non-empty); the first after sorting by latest date is the main
    line, which carries the career-high marker, the 'now' label and the title stars."""
    sers = _pick({k: v for k, v in series.items() if v}, max_lines)
    if not sers:
        raise ValueError("rank_over_time_figure needs at least one non-empty series")
    fig = go.Figure()
    for i, (label, pts) in enumerate(sers.items()):
        fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], name=label, mode="lines",
                                 line=dict(width=2.6, color=COLOURS[i % len(COLOURS)], shape="hv"),
                                 hovertemplate=f"{label}<br>%{{x|%d %b %Y}}: #%{{y}}<extra></extra>"))
    main = next(iter(sers.values()))
    best = min(main, key=lambda p: (p[1], p[0]))
    last = main[-1]
    fig.add_trace(go.Scatter(x=[best[0]], y=[best[1]], mode="markers", name="Career high", showlegend=False,
                             marker=dict(size=11, color=GOLD, line=dict(color="#ffffff", width=2)),
                             hovertemplate=f"Career high #{best[1]} ({best[0][:7]})<extra></extra>"))
    at_end = best[1] == last[1]
    # a title star on (or within ~60 days of) the career high would sit on its label: move the label to the right
    near_star = not at_end and any(abs((date.fromisoformat(d) - date.fromisoformat(best[0])).days) <= 60
                                   for d, _ in (titles or []))
    fig.add_annotation(x=last[0] if at_end else best[0], y=best[1],
                       text=f"<b>Career high #{best[1]}{', now' if at_end else ''}</b>", showarrow=False,
                       yanchor="top", xanchor="right" if at_end else ("left" if near_star else "center"),
                       xshift=-6 if at_end else (12 if near_star else 0), yshift=-10, font=dict(size=11.5))
    if not at_end:
        fig.add_annotation(x=last[0], y=last[1], text=f"<b>#{last[1]} now</b>", showarrow=False, xanchor="right",
                           yanchor="top", xshift=-6, yshift=-10, font=dict(size=11.5, color=COLOURS[0]))
    if titles:
        def rank_at(d):
            prior = [p for p in main if p[0] <= d]
            return (prior[-1] if prior else main[0])[1]
        fig.add_trace(go.Scatter(x=[d for d, _ in titles], y=[rank_at(d) for d, _ in titles], mode="markers",
                                 name="Title", text=[n for _, n in titles],
                                 marker=dict(symbol="star", size=13, color=GOLD, line=dict(color=GOLD_EDGE, width=1)),
                                 hovertemplate="%{text}<br>%{x|%d %b %Y}<extra>Title</extra>"))
    apply_template(fig)
    fig.update_layout(height=height, margin=dict(l=56, r=20, t=16, b=36), hovermode="closest",
                      legend=dict(orientation="h", y=-0.18, x=0))
    worst = max(p[1] for pts in sers.values() for p in pts)
    fig.update_yaxes(type="linear", range=[worst * 1.05, 0.5], title=None, tickprefix="#", showgrid=True)
    fig.update_xaxes(title=None)
    return fig


def rank_over_time(series: dict, titles: Optional[list] = None, *, heading: str = "Rank over time",
                   max_lines: int = 3, height: int = 300, className: str = ""):
    """The section: heading, graph and a one-line key. None when there is no series to draw."""
    if not any(series.values() if series else []):
        return None
    note = "Best rank on top. Stars are titles." if titles else "Best rank on top."
    return html.Section([
        html.H2(heading, className="ad-rot-title"),
        dcc.Graph(figure=rank_over_time_figure(series, titles, max_lines=max_lines, height=height),
                  config={"displayModeBar": False}, className="ad-rot-graph"),
        html.P(note, className="ad-rot-note"),
    ], className=f"ad-rot {className}".strip(), **{"aria-label": heading})


# ── v0.110: small multiples (Kenny's pick, Fencing Reports rankings history) ─────────────────────────────
_SM_MODES = ("lists", "sources")


def rank_sources(series: dict) -> dict[str, str]:
    """{label: source}. The source is the trailing ' (FIE)' of a label like 'Senior Foil (FIE)' (the shape
    ``rank_series_from_record`` gives fencing); a label without one is filed under 'Rankings'."""
    out = {}
    for label in series:
        t = str(label).rstrip()
        inner = t[t.rfind("(") + 1:-1].strip() if t.endswith(")") and "(" in t else ""
        out[label] = inner or "Rankings"
    return out


def rank_small_multiples(series: dict, mode: str = "lists", *, sources: Optional[dict] = None, cols: int = 3,
                         row_height: int = 190, colours: Optional[tuple] = None) -> go.Figure:
    """Rank history as small multiples.

    ``series``: {label: [(iso_date, rank)]} as from ``rank_series_from_record`` (empty lists are dropped).
    ``mode="lists"``: one chart per list, each on its OWN reversed rank axis (best on top), so a list that
    runs 1-6 is not flattened by one that runs 1-500. The latest point is ringed in gold.
    ``mode="sources"``: one chart per source with that source's lists overlaid (toggle target for the
    per-list view). ``sources`` maps label -> source (default: ``rank_sources(series)``).
    ``cols`` charts per row, ``row_height`` px per row. Raises ValueError for an unknown mode or no data.
    """
    from plotly.subplots import make_subplots

    if mode not in _SM_MODES:
        raise ValueError(f"mode must be one of {_SM_MODES}, got {mode!r}")
    sers = {k: v for k, v in (series or {}).items() if v}
    if not sers:
        raise ValueError("rank_small_multiples needs at least one non-empty series")
    colours = colours or COLOURS
    if mode == "lists":
        panels = {label: {label: pts} for label, pts in sers.items()}
    else:
        src = sources or rank_sources(sers)
        panels = {}
        for label, pts in sers.items():
            panels.setdefault(src.get(label) or "Rankings", {})[label] = pts
    n = len(panels)
    cols = max(1, min(cols, n))
    rows = -(-n // cols)
    titles = [str(k).upper() for k in panels]
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=titles, horizontal_spacing=0.09,
                        vertical_spacing=min(0.2, 0.55 / rows))
    ci = 0
    for i, (_, lists) in enumerate(panels.items()):
        r, c = i // cols + 1, i % cols + 1
        ranks = [p[1] for pts in lists.values() for p in pts]
        worst, best = max(ranks), min(ranks)
        pad = max(1.0, (worst - best) * 0.2)
        for label, pts in lists.items():
            col = colours[ci % len(colours)]
            ci += 1
            fig.add_trace(go.Scatter(
                x=[p[0] for p in pts], y=[p[1] for p in pts], mode="lines+markers", name=str(label),
                line=dict(width=2.6, color=col), marker=dict(size=7, color=col, line=dict(width=1.5, color="#ffffff")),
                hovertemplate=f"{label}<br>%{{x|%d %b %Y}}: #%{{y}}<extra></extra>", showlegend=False), row=r, col=c)
            last = pts[-1]
            fig.add_trace(go.Scatter(
                x=[last[0]], y=[last[1]], mode="markers", name=f"{label} latest", hoverinfo="skip", showlegend=False,
                marker=dict(size=16, color="rgba(251,184,0,0.10)", line=dict(color="#fbb800", width=2))), row=r, col=c)
        fig.update_yaxes(range=[worst + pad, max(0.5, best - pad)], tickprefix="#", nticks=4, showgrid=True,
                         title=None, row=r, col=c)
        fig.update_xaxes(title=None, tickfont=dict(size=10), row=r, col=c)
    apply_template(fig)
    for i, a in enumerate(fig.layout.annotations):     # subplot titles: small caps, left-aligned on the panel
        ax = fig.layout["xaxis" + ("" if i == 0 else str(i + 1))]
        a.update(font=dict(size=11, color="#0f172a"), xanchor="left", x=ax.domain[0])
    fig.update_layout(height=row_height * rows + 30, margin=dict(l=44, r=16, t=30, b=30), hovermode="closest",
                      showlegend=False)
    return fig
