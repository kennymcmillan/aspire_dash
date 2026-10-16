"""The athlete's ladder, steps and season-by-season chart (v0.108, promoted from High Management Overview;
Kenny approved the ladder 2026-10-12 and chose Steps on desktop, Ladder on phone 2026-10-13).

    ladder(j, className="")           the ladder card: hardest rung on top, junior percentile rungs at the bottom,
                                      reached rungs coloured, the next one dashed, the climber on the best mark;
                                      far rungs fold away. On screens >= 900px the same card shows the Steps view
                                      (a staircase, easiest on the left) instead.
    season_section(j, className="")   season bests by year against the same rungs, the junior percentile corridor,
                                      a flag on the year each rung was first beaten, championship medals, the gap
                                      to the next rung. None with fewer than two seasons.
    chart_figure(j), story(j), first_beaten(value, season_bests, lower), nice_holder(name)

``j`` is the Sports API journey (GET /api/athlete/{id}/brief?view=page, athletics): ``event``, ``unit``,
``lower`` (times: lower is better), ``season_bests`` [[year, value, text]], ``corridor`` [{year, p75, p90, p95}],
``champs`` [{year, comp, lane, medal, mark}], ``level`` {now, peak}, ``climb.steps`` [{kind, stage, label, mark,
value, state, gap, holder, won}] with state one of youth / before / cleared / next / ahead. ``rec`` (optional)
carries ``.name`` for the climber's initials. Every number is a journey field; the only thing derived here is
the year a rung was first beaten. Look: assets/08_profile.css (ad-lj-*); motion: assets/aspire_ladder.js
(in view, replay, the fold), static under prefers-reduced-motion and in print.
"""
from __future__ import annotations

from typing import Optional

import plotly.graph_objects as go
from ..charts import apply_template
from dash import dcc, html

__all__ = ["ladder", "steps_view", "season_section", "chart_figure", "story", "first_beaten", "nice_holder"]

ROW_PX = 46                                    # one ladder row; the climber starts this far below per row under it
FOLD_AFTER_NEXT = 4                            # rungs shown above the next one before the rest fold away
STAGE = {"Youth": ("fa-seedling", "Junior years"), "Asia": ("fa-flag", "Asia"), "World": ("fa-earth-americas", "World"),
         "Podium": ("fa-medal", "World podium"), "Records": ("fa-trophy", "Records")}
LINE_COLOUR = {"Records": "#d4a017", "Podium": "#b06a35"}
BRAND, BRAND_2, INK_3, YOUTH, YOUTH_2, YOUTH_SOFT = "#004185", "#1a5fa8", "#8492a6", "#0f7a55", "#3fb187", "rgba(63,177,135,.18)"
MEDAL_FILL = {1: "#d4a017", 2: "#9aa4b1", 3: "#b06a35"}
MEDAL_WORD = {1: "Gold", 2: "Silver", 3: "Bronze"}
MAJOR_LANES = {"og", "wch", "ag", "ach", "yth"}


def _i(icon: str) -> html.I:
    return html.I(className=f"fa-solid {icon}", **{"aria-hidden": "true"})


def _medal(place: int) -> html.Span:
    return html.Span(str(place), className=f"ad-lj-medal{'' if place == 1 else ' is-silver' if place == 2 else ' is-bronze'}",
                     title=MEDAL_WORD.get(place))


def first_beaten(value: Optional[float], season_bests: list, lower: bool) -> Optional[int]:
    """The first season whose best reached the rung (at or under it for times, at or over it for jumps/throws)."""
    if value is None:
        return None
    for yr, best, _ in season_bests or []:
        if best is not None and (best <= value if lower else best >= value):
            return int(yr)
    return None


def _initials(j: dict) -> str:
    name = getattr(j.get("rec"), "name", None) or ""
    parts = [p for p in name.split() if p[:1].isalpha()]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()


def _chip(text: str, cls: str = "") -> html.Span:
    return html.Span(text, className=f"ad-lj-ld-chip{' ' + cls if cls else ''}")


def _what(s: dict, j: dict, first: Optional[int]) -> list:
    """The right-hand side of a rung: what was won there, since when, or how far off."""
    w, u, out = s.get("won") or {}, j.get("unit") or "", []
    if w.get("medal"):
        out.append(_medal(w["medal"]))
    if s["kind"] in ("pctl", "pct"):
        if s["state"] == "youth":
            out.append(_chip(w.get("text") or "", "is-y"))
        elif s.get("gap"):
            out += [_chip(f"{s['gap']} {u} to go", "is-go"), html.Span(w.get("text") or "")]
        else:
            out.append(_chip(w.get("text") or "", "is-miss"))
        return out
    if s["state"] == "next":
        out.append(_chip(f"{s['gap']} {u} to go", "is-go"))
    if w.get("text") and (w.get("medal") or w.get("place") or w.get("round")):
        out.append(html.Span(w["text"]))
    if first and s["state"] != "next":
        out.append(_chip(f"{'did it' if s['state'] == 'before' else 'since'} {first}"))
    if s["kind"] == "youth" and not w.get("medal"):
        out.append(_chip("junior", "is-y"))
    if s["state"] == "ahead" and s.get("gap"):
        out.append(_chip(f"{s['gap']} {u} off", "is-off"))
    if s["state"] == "next" and first:
        out.append(_chip(f"did it {first}"))
    return out


def ladder(j: dict, className: str = "") -> Optional[html.Section]:
    steps = (j.get("climb") or {}).get("steps") or []
    if not steps:
        return None
    sbs, lower = j.get("season_bests") or [], bool(j.get("lower"))
    ni = next((k for k, s in enumerate(steps) if s["state"] == "next"), None)
    keep = len(steps) if ni is None else ni + 1 + FOLD_AFTER_NEXT
    def folded(k: int) -> bool:                # the climber's own row (best / this season) never folds
        return keep <= k < len(steps) - 1 and steps[k]["kind"] not in ("pb", "now")

    far_n = sum(1 for k in range(len(steps)) if folded(k))
    rows = [html.Div(_i("fa-mountain"), className="ad-lj-ld-summit")]
    for k in range(len(steps) - 1, -1, -1):
        s = steps[k]
        if k == len(steps) - 2 and far_n:
            rows.append(html.Div(html.Button(f"+{far_n} more rung{'s' if far_n > 1 else ''} to the world record",
                                             className="ad-lj-btn", **{"data-more": "1", "aria-expanded": "false"}),
                                 className="ad-lj-ld-more"))
        name = html.Div([html.B([html.Span(_i(STAGE.get(s["stage"], ("fa-stairs",))[0]), className="ad-lj-ld-si",
                                           title=STAGE.get(s["stage"], (None, s["stage"]))[1]), s["label"].strip()]),
                         html.Small(s["mark"] + (f" · {s['holder']}" if s.get("holder") else ""))], className="ad-lj-ld-name")
        if s["kind"] in ("pb", "now"):
            only_pb = not any(x["kind"] == "now" for x in steps)
            tag = "this season" if s["kind"] == "now" else ("now, best ever" if only_pb else "best ever")
            rows.append(html.Div([
                html.Div(className="ad-lj-ld-line"), name,
                html.Div(_initials(j), className="ad-lj-ld-climber" + (" is-now" if s["kind"] == "now" else ""),
                         style={"--from": f"{k * ROW_PX}px"}),
                html.Div(_chip(tag, "is-pb" if s["kind"] == "pb" else ""), className="ad-lj-ld-what"),
            ], className="ad-lj-ld-here"))
            continue
        first = first_beaten(s.get("value"), sbs, lower) if s["kind"] == "rung" else None
        far = folded(k)
        rows.append(html.Div([name, html.Div(html.Div(className="ad-lj-ld-rung"), className="ad-lj-ld-rail"),
                              html.Div(_what(s, j, first), className="ad-lj-ld-what")],
                             className=f"ad-lj-ld-row is-{s['state']}{' is-far' if far else ''}", style={"--i": k}))
    steps_el = steps_view(j, steps, sbs, lower)
    lv = j.get("level") or {}
    level = html.Div([html.Span(f"Level now: {lv['now']}", className="ad-lj-ld-level"),
                      html.Span(["Career peak: ", html.B(lv["peak"])], className="ad-lj-ld-peak") if lv.get("peak") else None]
                     ) if lv.get("now") else None
    return html.Section([
        html.Div([html.Div([html.H2(f"The ladder: {j['event']}", className="ad-lj-h2"),
                            html.P("Hardest at the top. Coloured rungs are reached, the dashed rung is next, green is "
                                   "the junior years.", className="ad-lj-sub ad-lj-only-ladder"),
                            html.P("Easiest on the left, rising to the right. Coloured steps are reached, the dashed "
                                   "step is next, green is the junior years.", className="ad-lj-sub ad-lj-only-steps")]),
                  html.Button([_i("fa-rotate-right"), " Replay"], className="ad-lj-btn", **{"data-replay": "1"})],
                 className="ad-lj-head"),
        level,
        html.Div(rows, className="ad-lj-ld ad-lj-anim"),
        steps_el,
    ], className=f"ad-lj-card ad-lj-ladder-card {className}".strip(), **{"aria-label": "The ladder"})


def steps_view(j: dict, steps: list, sbs: list, lower: bool) -> html.Div:
    """The same rungs as a staircase, easiest on the left (Kenny 2026-10-13: Steps on desktop, Ladder on phone).
    Nothing folds here: the staircase scrolls inside its own box when it is wider than the card."""
    n = len(steps)
    height = lambda i: round(28 + i * 190 / max(1, n - 1))   # noqa: E731
    cols = []
    for k, s in enumerate(steps):
        if s["kind"] in ("pb", "now"):
            tag = "this season" if s["kind"] == "now" else "best ever"
            cols.append(html.Div([
                html.Div([html.Div(_initials(j), className="ad-lj-ld-climber" + (" is-now" if s["kind"] == "now" else "")),
                          _chip(tag, "is-pb" if s["kind"] == "pb" else "")], className="ad-lj-st-top"),
                html.Div(className="ad-lj-st-blk", style={"height": f"{height(max(0, k - 1))}px"}),
                html.Div([html.B(s["label"].strip()), html.Small(s["mark"])], className="ad-lj-st-lab"),
            ], className="ad-lj-st-step is-here", style={"--i": k}))
            continue
        first = first_beaten(s.get("value"), sbs, lower) if s["kind"] == "rung" else None
        cols.append(html.Div([
            html.Div(_what(s, j, first), className="ad-lj-st-top"),
            html.Div(html.Span(s["mark"]), className="ad-lj-st-blk", style={"height": f"{height(k)}px"}),
            html.Div([html.B([html.Span(_i(STAGE.get(s["stage"], ("fa-stairs",))[0]), className="ad-lj-ld-si"), s["label"].strip()]),
                      html.Small(nice_holder(s.get("holder")))] if s.get("holder") else
                     [html.B([html.Span(_i(STAGE.get(s["stage"], ("fa-stairs",))[0]), className="ad-lj-ld-si"), s["label"].strip()])],
                     className="ad-lj-st-lab"),
        ], className=f"ad-lj-st-step is-{s['state']}", style={"--i": k}))
    return html.Div(cols, className="ad-lj-st ad-lj-anim", tabIndex=0, role="list",
                    **{"aria-label": f"The steps for {j.get('event') or 'this event'}, easiest on the left"})


def nice_holder(h: Optional[str]) -> str:
    """'Jane DOE SMITH' -> 'Jane Doe Smith' (source lists shout the surname)."""
    return " ".join(w.capitalize() if w.isupper() and len(w) > 2 else w for w in str(h or "").split())


# --------------------------------------------------------------------------- season by season
def _shown_rungs(j: dict) -> list:
    """Every rung with a mark, up to the first two still ahead: no empty sky up to the world record."""
    rungs = [s for s in (j.get("climb") or {}).get("steps") or [] if s["kind"] == "rung" and s.get("value") is not None]
    ahead = [r for r in rungs if r["state"] in ("ahead", "next")][:2]
    return [r for r in rungs if r["state"] not in ("ahead", "next") or r in ahead]


def chart_figure(j: dict) -> go.Figure:
    sbs, cor, lower, u = j.get("season_bests") or [], j.get("corridor") or [], bool(j.get("lower")), j.get("unit") or ""
    shown = _shown_rungs(j)
    vals = [s[1] for s in sbs] + [r["value"] for r in shown] + [c[k] for c in cor for k in ("p75", "p95") if c.get(k) is not None]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.07 or 0.1
    lo, hi = lo - pad, hi + pad
    span = hi - lo
    y0 = min([sbs[0][0]] + [c["year"] for c in cor])
    y1 = max(sbs[-1][0], max((c["year"] for c in cor), default=0))
    fig = go.Figure()
    if cor:                                              # p75..p95 band and the p90 line while 14-20
        xs = [c["year"] for c in cor]
        fig.add_trace(go.Scatter(x=xs, y=[c["p75"] for c in cor], name="Top 25% for age", mode="lines",
                                 line=dict(color=YOUTH_2, width=1), hovertemplate="%{x}: top 25%% for age %{y}<extra></extra>"))
        fig.add_trace(go.Scatter(x=xs, y=[c["p95"] for c in cor], name="Top 5% for age", mode="lines", fill="tonexty",
                                 fillcolor=YOUTH_SOFT, line=dict(color=YOUTH_2, width=1),
                                 hovertemplate="%{x}: top 5%% for age %{y}<extra></extra>"))
        fig.add_trace(go.Scatter(x=xs, y=[c["p90"] for c in cor], name="Top 10% for age", mode="lines",
                                 line=dict(color=YOUTH, width=1.5, dash="dot"),
                                 hovertemplate="%{x}: top 10%% for age %{y}<extra></extra>"))
        fig.add_annotation(x=xs[0], y=cor[0]["p95"], text="Top 25% to 5% for age", showarrow=False, xanchor="left",
                           yshift=12, font=dict(size=10.5, color=YOUTH))
    # one line per rung (rungs at the same height share a label); labels pushed apart so they never overlap
    merged: list[dict] = []
    for r in sorted(shown, key=lambda r: r["value"]):
        if merged and abs(merged[-1]["value"] - r["value"]) < span * 0.008:
            merged[-1]["also"] += 1                          # same height: one line, "+1" in the label
            merged[-1]["first"] = merged[-1]["first"] or first_beaten(r["value"], sbs, lower)
            continue
        merged.append({**r, "first": first_beaten(r["value"], sbs, lower), "also": 0})
    by_height = sorted(merged, key=lambda r: -r["value"] if not lower else r["value"])   # top of the chart first
    gap_min, placed = span * 0.045, []
    for r in by_height:
        ly = r["value"]
        if placed and abs(placed[-1] - ly) < gap_min:
            ly = placed[-1] - gap_min if not lower else placed[-1] + gap_min
        placed.append(ly)
        beaten = r["first"] is not None
        col = LINE_COLOUR.get(r["stage"], BRAND_2) if beaten else INK_3
        fig.add_shape(type="line", xref="paper", x0=0, x1=1, y0=r["value"], y1=r["value"],
                      line=dict(color=col, width=1.6 if beaten else 1.3, dash="solid" if beaten else "dash"))
        txt = f"{r['label']} {r['mark']}" + (f" (+{r['also']})" if r["also"] else "")
        fig.add_annotation(xref="paper", x=1.01, y=ly, xanchor="left", showarrow=False,
                           text=f"<b>{txt}</b>" if r["state"] == "next" else txt,
                           font=dict(size=11, color=BRAND if r["state"] == "next" else col))
        if beaten:
            fig.add_trace(go.Scatter(x=[r["first"]], y=[r["value"]], mode="markers", name="First beaten", showlegend=False,
                                     marker=dict(symbol="triangle-right", size=12, color="#d4a017",
                                                 line=dict(color="#0f1b2d", width=1)),
                                     hovertemplate=f"{r['label']}: first beaten in {r['first']}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[s[0] for s in sbs], y=[s[1] for s in sbs], name="Season best", mode="lines+markers",
                             text=[s[2] for s in sbs], hovertemplate="%{x}: %{text}<extra></extra>",
                             line=dict(width=3.2, color=BRAND), marker=dict(size=9, color="#ffffff", line=dict(width=2.4, color=BRAND))))
    last = sbs[-1]
    fig.add_trace(go.Scatter(x=[last[0]], y=[last[1]], mode="markers", showlegend=False, name="Latest",
                             marker=dict(size=15, color="#d4a017", line=dict(color="#ffffff", width=2)),
                             hovertemplate=f"{last[0]}: {last[2]}<extra></extra>"))
    fig.add_annotation(x=last[0], y=last[1], text=f"<b>{last[2]} · {last[0]}</b>", showarrow=False, xanchor="right",
                       xshift=-12, yshift=-16, font=dict(size=12))      # below-left: the gap label sits above-left
    # major championship medals along the bottom, on their year
    bottom, up = (hi, -1) if lower else (lo, 1)
    mx, my, mt, mc, mh, per_year = [], [], [], [], [], {}
    for c in j.get("champs") or []:
        if not c.get("medal") or c.get("lane") not in MAJOR_LANES or not (y0 <= c["year"] <= y1):
            continue
        k = per_year.get(c["year"], 0)
        if k >= 3:
            continue
        per_year[c["year"]] = k + 1
        mx.append(c["year"]); my.append(bottom + up * span * (0.04 + 0.065 * k)); mt.append(str(c["medal"]))
        mc.append(MEDAL_FILL[c["medal"]]); mh.append(f"{c['year']} {c['comp']}: {c['mark']}")
    if mx:
        fig.add_trace(go.Scatter(x=mx, y=my, mode="markers+text", name="Championship medal", text=mt, hovertext=mh,
                                 hovertemplate="%{hovertext}<extra></extra>", textfont=dict(size=10, color="#2b2000"),
                                 marker=dict(size=18, color=mc, line=dict(color="#ffffff", width=1.5))))
    nxt = next((s for s in (j.get("climb") or {}).get("steps") or [] if s["state"] == "next" and s.get("value") is not None), None)
    if nxt:                                             # the gap to the next rung, from the latest season best
        gx = last[0] + 0.3
        fig.add_trace(go.Scatter(x=[gx, gx], y=[last[1], nxt["value"]], mode="lines", showlegend=False, name="Gap",
                                 line=dict(color=BRAND, width=2.4), hoverinfo="skip"))
        fig.add_annotation(x=gx, y=(last[1] + nxt["value"]) / 2, text=f"<b>{nxt['gap']} {u}</b>", showarrow=False,
                           xanchor="right", xshift=-6, font=dict(size=12, color=BRAND),
                           bgcolor="rgba(255,255,255,.85)")             # left of the bracket, clear of the rung labels
    apply_template(fig)
    fig.update_layout(height=440, margin=dict(l=50, r=210, t=16, b=36), showlegend=False, hovermode="closest")
    fig.update_yaxes(range=[hi, lo] if lower else [lo, hi], title=None, tickformat=".2f" if hi < 100 else None)
    fig.update_xaxes(range=[y0 - 0.5, y1 + 0.8], dtick=1 if y1 - y0 <= 12 else 2, title=None)
    return fig


def story(j: dict) -> str:
    """One paragraph reading the chart, from the same fields."""
    steps = (j.get("climb") or {}).get("steps") or []
    sbs, lower, u = j.get("season_bests") or [], bool(j.get("lower")), j.get("unit") or ""
    bits = []
    pct = [s for s in steps if s["kind"] in ("pctl", "pct") and s["state"] == "youth" and (s.get("won") or {}).get("text")]
    if pct:
        bits.append("As a junior: " + ", ".join(f"{s['label'].lower()} {s['won']['text'].replace('At ', 'at ', 1)}"
                                                for s in pct) + ".")
    reached = sorted(((first_beaten(s["value"], sbs, lower), s) for s in _shown_rungs(j)), key=lambda t: t[0] or 9999)
    reached = [(y, s) for y, s in reached if y]
    if reached:
        bits.append(f"First rung beaten: {reached[0][1]['label']} in {reached[0][0]}; "
                    f"latest: {reached[-1][1]['label']} in {reached[-1][0]}.")
    nxt = next((s for s in steps if s["state"] == "next" and s.get("gap")), None)
    if nxt:
        bits.append(f"Next: {nxt['label']}, {nxt['gap']} {u} from the latest season best.")
    return " ".join(bits)


def season_section(j: dict, className: str = "") -> Optional[html.Section]:
    if len(j.get("season_bests") or []) < 2:
        return None
    key = [("ad-lj-sc-sb", "Season best"), ("ad-lj-sc-cor", "Top 25% to top 5% for age"), ("ad-lj-sc-beat", "Rung beaten"),
           ("ad-lj-sc-todo", "Still to beat"), ("ad-lj-sc-flag", "Year first beaten")]
    return html.Section([
        html.H2(f"Season by season: {j['event']}", className="ad-lj-h2"),
        html.P(f"Best mark each season ({'faster' if j.get('lower') else 'better'} is higher). Each rung of the ladder is "
               "a line: solid once beaten, with a flag on the year it first was. Green band: top 25% to top 5% for age "
               "while a junior.", className="ad-lj-sub"),
        html.Div(dcc.Graph(figure=chart_figure(j), config={"displayModeBar": False}, className="ad-lj-graph"),
                 className="ad-lj-sc-wrap"),                                # phones: the chart scrolls in its own box
        html.Div([html.Span([html.Span(className=f"ad-lj-sc-key {c}"), t]) for c, t in key]
                 + [html.Span([_medal(1), " Championship medal"])], className="ad-lj-legend"),
        html.P(story(j), className="ad-lj-sc-story"),
    ], className=f"ad-lj-card {className}".strip(), **{"aria-label": "Season bests"})
