"""Region rank maps (v0.110): a Plotly choropleth zoomed to a region, with the rank number in a bubble
on each nation. Built for team / nation ranking lists (fencing team rankings, any sport with an IOC
code, a rank and points). Kenny's pick from the Fencing Reports design pass (map option A).

    region_rank_map(rows, region="gulf" | "asia", highlight="QAT") -> go.Figure

Rows are dicts with an IOC ``nation_code``, ``rank_position`` and ``points`` (optional ``nation`` name).
Every member of the region is drawn; one with no usable rank shows as "not ranked". Rank bands are
top 8, 9-16, 17-32, 33+ and not ranked (``RANK_BANDS``). The map joins on ISO-3, the rows on IOC, via
``aspire_dash.countries.iso3`` (the one IOC to ISO-3 table in the library).
"""
from __future__ import annotations

from typing import Iterable, Optional

import plotly.graph_objects as go

from .charts import apply_template
from .countries import iso3 as _iso3, name as _country_name
from .theme import FONT_DATA

__all__ = ["REGIONS", "RANK_BANDS", "region_rank_map", "rank_band"]

#: (label, fill colour, text colour on that fill). Index 4 is "not ranked".
RANK_BANDS = (
    ("Top 8", "#001d3d", "#ffffff"),
    ("9-16", "#004185", "#ffffff"),
    ("17-32", "#4d86c4", "#ffffff"),
    ("33+", "#b4cde8", "#0f172a"),
    ("Not ranked", "#eef2f7", "#64748b"),
)
_NOT_RANKED = 4
_GOLD = "#fbb800"

# IOC code -> (lon, lat) of the rank bubble. Placement only, not data: Gulf bubbles are nudged apart so
# the small states do not stack; the Asia set is the Gulf six plus 27 more
# (IRQ, JOR, SYR, LBN, PAK, MGL added 2026-10-20: IRQ + JOR hold sabre team ranks and were never drawn).
_GULF = {
    "QAT": (51.45, 25.0), "BRN": (50.2, 26.6), "KUW": (47.6, 29.3),
    "UAE": (54.3, 23.9), "KSA": (44.5, 24.5), "OMA": (56.2, 20.6),
}
_ASIA = {
    "QAT": (52.5, 25.0), "BRN": (49.5, 27.5), "KUW": (46, 31), "UAE": (56, 22.5), "KSA": (43, 24.5),
    "OMA": (59.5, 19.5), "IRI": (54, 32.5), "KAZ": (67, 48), "TKM": (59, 39), "UZB": (64, 41.5),
    "KGZ": (74.5, 41.5), "CHN": (104, 35), "KOR": (127.8, 36.5), "JPN": (138, 36), "NEP": (84, 28.3),
    "HKG": (114.2, 22.6), "TPE": (121, 23.7), "IND": (79, 22), "MAC": (112.4, 21.2), "VIE": (106, 16),
    "PHI": (122, 12.5), "THA": (101, 15.5), "CAM": (104.9, 12.6), "SRI": (80.7, 7.8), "MAS": (102, 4.2),
    "SGP": (104.6, 0.4), "INA": (113, -1),
    "IRQ": (43.8, 33.2), "JOR": (36.6, 30.8), "SYR": (38.5, 35.2), "LBN": (35.9, 33.9),
    "PAK": (69.5, 29.8), "MGL": (103, 46.8),
}

#: region key -> members (IOC codes), bubble positions, geo window and bubble sizes.
REGIONS = {
    "gulf": dict(label="Gulf", centroids=_GULF, lon=(43.5, 60.5), lat=(19, 31.5), aspect=1.3,
                 bubble=44, font=10, codes=True),
    "asia": dict(label="Asia", centroids=_ASIA, lon=(34, 150), lat=(-8, 54), aspect=1.55,
                 bubble=22, font=10, codes=False),
}


def rank_band(rank) -> int:
    """Band index 0..4 into ``RANK_BANDS`` for a rank (None, 0 or junk = 4, not ranked)."""
    try:
        r = int(rank)
    except (TypeError, ValueError):
        return _NOT_RANKED
    if r <= 0:
        return _NOT_RANKED
    return 0 if r <= 8 else 1 if r <= 16 else 2 if r <= 32 else 3


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f


def _fmt_points(p) -> str:
    return f"{p:g}" if p is not None else ""


def region_rank_map(rows: Iterable[dict], region: str = "gulf", highlight: Optional[str] = "QAT", *,
                    title: Optional[str] = None, height: Optional[int] = None, width: int = 640,
                    subject: str = "world team rank") -> go.Figure:
    """Choropleth zoomed to ``region`` with a rank-number bubble at each nation.

    Parameters
    ----------
    rows : iterable of dict
        ``{"nation_code": "QAT", "rank_position": 27, "points": 120.5}`` (+ optional ``"nation"``). Codes
        are IOC. Rows for nations outside the region are ignored; members with no row, or no positive
        rank, are drawn as "not ranked". A duplicate code keeps the best rank.
    region : "gulf" | "asia"
        ``REGIONS`` keys. Gulf: QAT BRN KUW UAE KSA OMA. Asia: those six plus 21 more (see ``REGIONS``).
    highlight : str | None
        IOC code that gets the gold ring (default Qatar).
    title, height, width : layout. ``height`` defaults to ``width`` / the region aspect ratio.
    subject : str
        Wording for the hover ("<nation> world team rank 27, 120.5 pts").

    Returns
    -------
    plotly.graph_objects.Figure
        ``data[0]`` Choropleth (colour = band), ``data[1]`` Scattergeo rank bubbles (text = rank number),
        ``data[2]`` Scattergeo code labels (blank on Asia). No zoom (dragmode off), no modebar needed.
    """
    key = str(region).lower()
    if key not in REGIONS:
        raise ValueError(f"region must be one of {sorted(REGIONS)}, got {region!r}")
    spec = REGIONS[key]
    cents = spec["centroids"]

    best: dict[str, dict] = {}
    names: dict[str, str] = {}
    for r in rows or []:
        code = str(r.get("nation_code") or "").strip().upper()
        if code not in cents:
            continue
        if r.get("nation"):
            names[code] = str(r["nation"])
        rk = _num(r.get("rank_position"))
        if rk is None or rk <= 0:
            continue
        if code not in best or rk < best[code]["rank"]:
            best[code] = dict(rank=int(rk), points=_num(r.get("points")))

    codes = list(cents)
    bands = [rank_band(best[c]["rank"]) if c in best else _NOT_RANKED for c in codes]
    hl = (highlight or "").strip().upper()

    def hover(c):
        nm = names.get(c) or _country_name(c) or c
        if c not in best:
            return f"<b>{nm}</b><br>not ranked"
        b = best[c]
        pts = f", {_fmt_points(b['points'])} pts" if b["points"] is not None else ""
        return f"<b>{nm}</b><br>{subject} {b['rank']}{pts}"

    hovers = [hover(c) for c in codes]
    # five equal steps: each band index owns one flat colour stop
    scale, n = [], len(RANK_BANDS)
    for i, (_, fill, _) in enumerate(RANK_BANDS):
        scale += [[i / n, fill], [(i + 1) / n, fill]]

    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=[_iso3(c) for c in codes], z=bands, zmin=0, zmax=n - 1,
        colorscale=scale, showscale=False, text=hovers, hovertemplate="%{text}<extra></extra>",
        marker=dict(line=dict(color="#ffffff", width=0.8)), name="Rank band"))
    size = spec["bubble"]
    fig.add_trace(go.Scattergeo(
        mode="markers+text", lon=[cents[c][0] for c in codes], lat=[cents[c][1] for c in codes],
        text=[(f"<b>{best[c]['rank']}</b>" if c in best else "-") for c in codes],
        textfont=dict(size=spec["font"], family=FONT_DATA, color=[RANK_BANDS[b][2] for b in bands]),
        hovertext=hovers, hoverinfo="text", customdata=codes, name="Rank",
        marker=dict(size=[size + 6 if c == hl else size for c in codes],
                    color=[RANK_BANDS[b][1] for b in bands],
                    line=dict(color=[_GOLD if c == hl else "#ffffff" for c in codes],
                              width=[3.5 if c == hl else 1.5 for c in codes]))))
    # the code sits under the bubble, never on the rank: drop it by about a bubble's height in degrees
    drop = (spec["lat"][1] - spec["lat"][0]) * 0.075
    fig.add_trace(go.Scattergeo(
        mode="text", lon=[cents[c][0] for c in codes], lat=[cents[c][1] - drop for c in codes],
        text=codes if spec["codes"] else [""] * len(codes), textposition="middle center",
        textfont=dict(size=10, family=FONT_DATA, color="#0f172a"), hoverinfo="skip", name="Codes"))

    apply_template(fig)
    fig.update_layout(
        title=dict(text=title) if title else None,
        showlegend=False, dragmode=False,
        height=height or round(width / spec["aspect"]),
        margin=dict(l=0, r=0, t=34 if title else 0, b=0), paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(scope="asia", projection=dict(type="mercator"),
                 lonaxis=dict(range=list(spec["lon"])), lataxis=dict(range=list(spec["lat"])),
                 showland=True, landcolor="#e6ebf2", showocean=True, oceancolor="#d9e8f7",
                 showcountries=True, countrycolor="#ffffff", countrywidth=0.6, coastlinecolor="#c5d3e3",
                 showframe=False, resolution=50, bgcolor="rgba(0,0,0,0)"))
    return fig
