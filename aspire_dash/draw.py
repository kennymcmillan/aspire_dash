"""Draw path: an athlete's run through a knockout draw as a horizontal chain (v0.106.0).

Promoted from the Fencing Reports app (Nation Focus tab). Any knockout sport can use it:
fencing tableaux, squash / table tennis / padel draws, judo / taekwondo brackets.

    [POOLS] -> T64 -> T32 -> QF -> (5th)
     5V / 6   15-9   15-12  11-15

Each step is a plain dict, so the sport app only maps its own bouts to steps::

    from aspire_dash.draw import draw_path, draw_rows, win_step, loss_step, bye_step, lead_step, finish_step

    steps = [lead_step("POOLS", "5V / 6", below=pool_stats),
             bye_step("T128"),
             win_step("T64", "15-10", opp="NOVAK", nation="CZE", rank=60, star=True),
             loss_step("T32", "12-15", opp="KAPALA", nation="POL", rank=4),
             finish_step(17)]
    draw_path(steps)                       # one chain
    draw_rows([(header, steps), ...])      # several athletes, rounds aligned in shared columns

Rounds line up across rows: the same round sits in the same column for every athlete, so the deepest
run reads at a glance. A line runs through any empty column between two nodes. Styling lives in
00_aspire_base.css (`.draw-*`); the grid column count is the only inline style.
"""
from __future__ import annotations

from dash import html

from .sports import country_flag, ordinal, upset_star

_SHORT = {"semi-finals": "SF", "semifinal": "SF", "semifinals": "SF", "semi-final": "SF",
          "quarterfinal": "QF", "quarterfinals": "QF", "quarter-finals": "QF", "quarter-final": "QF",
          "finals": "F", "final": "F", "bronze medal": "BRONZE", "bronze": "BRONZE"}
_NAMED_DEPTH = {"QF": -8, "SF": -4, "BRONZE": -3, "F": -2}
LEAD, FINISH = "lead", "finish"


def short_round(label) -> str:
    """'Table of 64' -> 'T64', 'Round of 32' -> 'R32', 'Quarter-finals' -> 'QF', 'Final' -> 'F'."""
    label = str(label or "").strip()
    named = _SHORT.get(label.lower())
    if named:
        return named
    return label.replace("Table of ", "T").replace("Round of ", "R").upper()


def round_depth(key) -> int:
    """Column order of a round key: bigger tables first (T128 before T64), then QF, SF, BRONZE, F.
    Unknown keys sort 0 (after the tables and finals, in first-seen order)."""
    key = str(key or "")
    if key in _NAMED_DEPTH:
        return _NAMED_DEPTH[key]
    if key[:1] in ("T", "R") and key[1:].isdigit():
        return -int(key[1:])
    return 0


# ── Steps ───────────────────────────────────────────────────────────────────

def _step(col, kind, text, *, label=None, title=None, opp=None, nation=None, opp_title=None,
          rank=None, star=False, below=None):
    return {"col": col, "kind": kind, "text": text, "label": label or col, "title": title, "opp": opp,
            "nation": nation, "opp_title": opp_title, "rank": rank, "star": star, "below": below}


def win_step(round_label, score, **kw):
    """A won round. kw: opp (text under the pill, e.g. surname or 'CZE 2'), nation (IOC, flag under the
    pill), opp_title (hover for opp), rank (opponent's rank, '#60' under the pill), star (upset win),
    title (hover on the pill), label (top label; defaults to the short round)."""
    return _step(short_round(round_label), "win", score, **kw)


def loss_step(round_label, score, **kw):
    """A lost round (same keywords as win_step)."""
    return _step(short_round(round_label), "loss", score, **kw)


def bye_step(round_label, text="BYE", title="Bye"):
    """A round passed on a bye (grey pill)."""
    return _step(short_round(round_label), "bye", text, title=title)


def lead_step(col, text, *, below=None, title=None):
    """The opening stage before the draw (e.g. POOLS '5V / 6', GROUP '2-1'), navy pill, always first."""
    return _step(col, LEAD, text, below=below, title=title)


def finish_step(place, tied=False):
    """The finish circle ('1st' gold, '2nd' silver, '3rd' bronze, else outlined). None when no place."""
    try:
        p = int(place)
    except (TypeError, ValueError):
        return None
    return _step("FINISH", FINISH, ordinal(p) + ("=" if tied else ""), rank=p)


# ── Rendering ───────────────────────────────────────────────────────────────

def _line_kind(step):
    return step["kind"] if step["kind"] in ("win", "loss") else "rule"


def _node(step):
    kind = step["kind"]
    top = [step["label"].upper() if kind != FINISH else "FINISH"]
    if step.get("star"):
        top.append(upset_star())
    if kind == FINISH:
        place = step["rank"]
        medal = f" draw-finish--{place}" if place in (1, 2, 3) else ""
        body = html.Div(step["text"], className=f"draw-finish{medal}")
    else:
        body = html.Div(step["text"], title=step.get("title"), className=f"draw-pill draw-pill--{kind}")
    below = step.get("below")
    if below is None and (step.get("opp") or step.get("nation")):
        text = step.get("opp") or step.get("nation")
        below = [country_flag(step["nation"], size="sm") if step.get("nation") else None,
                 html.Span(text, title=step.get("opp_title") or None, className="draw-node__opp")]
    return html.Div([
        html.Div(top, className="draw-node__label"),
        body,
        html.Div(below, className="draw-node__below") if below is not None else html.Div(className="draw-node__below"),
        html.Div(f"#{step['rank']}", title="Opponent's ranking at the time", className="draw-node__rank")
        if step.get("rank") and kind != FINISH else None,
    ], className="draw-node")


def _cell(node, line_in=None, line_out=None):
    parts = []
    if line_in:
        parts.append(html.Div(className=f"draw-line draw-line--in draw-line--{line_in}"))
    if line_out:
        parts.append(html.Div(className=f"draw-line draw-line--out draw-line--{line_out}"))
    return html.Div(parts + [node], className="draw-cell")


def draw_columns(step_lists):
    """Shared column keys for several chains: the lead stage, each round reached by anyone in draw order,
    FINISH."""
    seen, lead = [], []
    for steps in step_lists:
        for s in steps:
            if not s:
                continue
            if s["kind"] == LEAD:
                if s["col"] not in lead:
                    lead.append(s["col"])
            elif s["col"] != "FINISH" and s["col"] not in seen:
                seen.append(s["col"])
    rounds = sorted(seen, key=lambda k: (round_depth(k), seen.index(k)))
    tail = ["FINISH"] if any(s and s["col"] == "FINISH" for steps in step_lists for s in steps) else []
    return lead + rounds + tail


def draw_path(steps, columns=None, className=""):
    """One chain. `columns` (from draw_columns) aligns it with other chains; default = its own steps.
    Returns None when there are no steps. Scrolls inside its own box on phones."""
    nodes = {s["col"]: s for s in steps if s}
    if not nodes:
        return None
    cols = columns or draw_columns([list(nodes.values())])
    present = [i for i, k in enumerate(cols) if k in nodes]
    cells = []
    for i, k in enumerate(cols):
        before = [j for j in present if j < i]
        after = [j for j in present if j > i]
        nxt = [j for j in present if j >= i]
        line_in = _line_kind(nodes[cols[nxt[0]]]) if before and nxt else None
        line_out = _line_kind(nodes[cols[after[0]]]) if after and (k in nodes or before) else None
        cells.append(_cell(_node(nodes[k]) if k in nodes else html.Div(), line_in, line_out))
    grid = html.Div(cells, className="draw-path__grid",
                    style={"gridTemplateColumns": f"repeat({len(cols)}, minmax(84px, 1fr))"})
    return html.Div(grid, className=f"draw-path {className}".strip())


def draw_rows(rows, title=None):
    """Several athletes' chains on shared columns. rows: [(header component, steps), ...], best first.
    None when no row has steps."""
    rows = [(h, [s for s in steps if s]) for h, steps in rows]
    rows = [(h, steps) for h, steps in rows if steps]
    if not rows:
        return None
    cols = draw_columns([steps for _, steps in rows])
    return html.Div([
        html.Div(title, className="draw-rows__title") if title else None,
        html.Div([html.Div([html.Div(h, className="draw-row__head"), draw_path(steps, cols)],
                           className="draw-row") for h, steps in rows], className="draw-rows"),
    ])
