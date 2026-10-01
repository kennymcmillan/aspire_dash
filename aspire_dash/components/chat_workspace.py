"""Chat workspace renderers (v0.102.0): the Tables / Charts / Trace tabs and the clarify chips of `chat_panel`.

Ported from the Workbench v2 chat (DASH_WORKBENCH_v2 `feat/v2-chat-panel`, app/pages/chat.py +
assets/workbench_chat.js), made generic: no app pages, no sport pills, no engine knowledge beyond the done-event
contract. Every function here is PURE (payload in, Dash components out) so the tests assert on values.

Inputs are the engine's done event (SSE `type: done`) or the JSON door's `/api/agent/ask` reply; both are flat:

    {answer, agent, tools_used, usage{llm_calls, input_tokens, output_tokens, cost_usd},
     trace{llm_calls, llm_ms, tool_calls, tool_ms, tool_errors, cached_tokens, hops,
           spans: [{k: "node"|"llm"|"tool", node, name, t, ms, err, in?, out?, cached?, calls?}], spans_dropped?},
     suggestions: [{label, question, why?, aspire_id?, sport?}],
     clarify: {question, attr, options: [{label, aspire_id, sport, tracked}]}}

A "turn" (what aspire-chat.js keeps per thread) = that payload's useful keys plus `q` (the question) and `ms`
(client-measured duration).
"""
from __future__ import annotations

import re

from dash import dcc, html

from aspire_dash.sports import data_table, placement_badge

MAX_SPANS = 300
MAX_CHIPS = 6

# ------------------------------------------------------------------------------------------- markdown tables
_ROW = re.compile(r"^\s*\|.*\|\s*$")
_SEP = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")
_MDSTRIP = re.compile(r"\*\*|__|`|\[([^\]]*)\]\([^)]*\)")
_PLACE_HEAD = re.compile(r"^(#|no\.?|pos(ition)?|place|placing|finish|rank)$|\b(pos|place|placing|finish)\b", re.I)
_RANK_HEAD = re.compile(r"rank|seed|#|^no\.?$", re.I)
_YEAR_HEAD = re.compile(r"year|season|date|month", re.I)
_ORDINAL = re.compile(r"^(\d{1,3})(st|nd|rd|th)?\.?$", re.I)
_CLOCK = re.compile(r"^(\d+):(\d{1,2}(?:\.\d+)?)$")


def _strip(s) -> str:
    return _MDSTRIP.sub(lambda m: m.group(1) or "", str(s or "")).strip()


def _cells(line: str) -> list[str]:
    return [_strip(c) for c in line.strip().strip("|").split("|")]


def num(v):
    """'10.12' -> 10.12, '1,234' -> 1234, '2:05.30' -> 125.3, '45%' -> 45; else None."""
    s = str(v if v is not None else "").strip().replace(",", "").rstrip("%").strip()
    if not s:
        return None
    m = _CLOCK.match(s)
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))
    try:
        return float(s)
    except ValueError:
        return None


def _numeric_cols(head, rows) -> list[int]:
    out = []
    for c in range(len(head)):
        vals = [r[c] for r in rows if c < len(r) and str(r[c]).strip() not in ("", "-")]
        if vals and sum(num(v) is not None for v in vals) / len(vals) >= 0.8:
            out.append(c)
    return out


def tables_from_markdown(text: str) -> list[dict]:
    """Every pipe table in an answer -> {title, head, rows, numeric, values, chart}. The title is the nearest
    heading or short line above the table. `values[str(col)]` = the parsed numbers of a numeric column."""
    lines = str(text or "").replace("\r\n", "\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        if _ROW.match(lines[i]) and i + 1 < len(lines) and _SEP.match(lines[i + 1]):
            head = _cells(lines[i])
            j, rows = i + 2, []
            while j < len(lines) and _ROW.match(lines[j]):
                r = _cells(lines[j])
                rows.append((r + [""] * len(head))[:len(head)])
                j += 1
            title = None
            for k in range(i - 1, max(-1, i - 4), -1):
                t = _strip(lines[k].lstrip("#").strip())
                if t:
                    title = t if len(t) <= 90 else None
                    break
            nc = _numeric_cols(head, rows)
            values = {str(c): [num(r[c]) for r in rows] for c in nc}
            item = {"title": title, "head": head, "rows": rows, "numeric": nc, "values": values}
            item["chart"] = chart_spec(item) is not None
            out.append(item)
            i = j
        else:
            i += 1
    return out


def _place(v):
    m = _ORDINAL.match(str(v or "").strip())
    return int(m.group(1)) if m else None


def _cell(v, place_col: bool):
    p = _place(v) if place_col else None
    if p is None:
        m = re.match(r"^(\d{1,3})(st|nd|rd)$", str(v or "").strip(), re.I)   # "3rd" inside any column
        p = int(m.group(1)) if m else None
    if p is not None and 1 <= p <= 3:
        return placement_badge(p, size="sm")
    return v


def place_columns(head) -> set[int]:
    return {i for i, h in enumerate(head) if _PLACE_HEAD.search(h or "") or (i == 0 and _RANK_HEAD.search(h or ""))}


def table_card(item: dict, key: str) -> html.Div:
    """One answer table -> a card holding the aspire_dash `data_table`; places 1-3 become medal badges."""
    head, rows, nums = item.get("head") or [], item.get("rows") or [], set(item.get("numeric") or [])
    places = place_columns(head)
    cols = [{"label": h, "align": "right" if (i in nums and i not in places) else "left",
             "wrap": i not in nums and i not in places
             and max((len(str(r[i])) for r in rows if i < len(r)), default=0) > 40}
            for i, h in enumerate(head)]
    body = [[_cell(r[i] if i < len(r) else "", i in places) for i in range(len(head))] for r in rows]
    title = item.get("title") or item.get("q") or "Table"
    return html.Div([
        html.Div([html.Span(title, className="aspire-chat-card-title", title=title),
                  html.Span(f"{len(rows)} row{'s' if len(rows) != 1 else ''}", className="aspire-chat-card-sub")],
                 className="aspire-chat-card-head"),
        html.Div(data_table(cols, body), className="aspire-chat-dt"),
    ], className="aspire-chat-card", **{"data-table-key": key})


# ------------------------------------------------------------------------------------------------- charts
def chart_spec(item: dict):
    """Label column, value columns and form. Ranks are 'lower is better' (dots on a reversed axis), years and
    seasons make a line, anything else is horizontal bars. None = nothing worth drawing."""
    head, nums = item.get("head") or [], list(item.get("numeric") or [])
    label = next((i for i in range(len(head)) if i not in nums), None)
    if label is None or not nums:
        return None
    time_like = bool(_YEAR_HEAD.search(head[label] or ""))

    def rank_like(c):
        return bool(_RANK_HEAD.search(head[c] or "") or _PLACE_HEAD.search(head[c] or ""))

    values = [c for c in nums if not rank_like(c) and not _YEAR_HEAD.search(head[c] or "")]
    if values:
        vals = item.get("values") or {}

        def peak(c):
            return max((abs(v) for v in (vals.get(str(c)) or []) if v is not None), default=0)

        first = peak(values[0]) or 1          # one axis: keep series on a comparable scale to the first
        values = [c for c in values if 0.2 <= (peak(c) or 1) / first <= 5]
        return {"label": label, "cols": values[:3], "form": "line" if time_like else "bar"}
    ranks = [c for c in nums if rank_like(c)]
    if ranks and label != 0:
        return {"label": label, "cols": ranks[-1:], "form": "rank"}
    return None


def chart_card(item: dict):
    import plotly.graph_objects as go

    from aspire_dash.charts import GRAPH_CONFIG, apply_template
    from aspire_dash.theme import CHART_COLORS

    spec = chart_spec(item)
    if not spec:
        return None
    head, rows, vals = item["head"], item["rows"], item.get("values") or {}
    labels = [r[spec["label"]] if spec["label"] < len(r) else "" for r in rows]
    fig = go.Figure()
    for k, c in enumerate(spec["cols"]):
        ys = vals.get(str(c)) or [None] * len(rows)
        color = CHART_COLORS[k % len(CHART_COLORS)]
        if spec["form"] == "line":
            fig.add_trace(go.Scatter(x=labels, y=ys, name=head[c], mode="lines+markers",
                                     line={"color": color, "width": 2.5}, marker={"size": 7}))
        elif spec["form"] == "rank":
            fig.add_trace(go.Scatter(y=labels, x=ys, name=head[c], mode="markers+text", text=ys,
                                     textposition="middle right", marker={"size": 11, "color": color},
                                     hovertemplate="%{y}: " + head[c] + " %{x}<extra></extra>"))
        else:
            fig.add_trace(go.Bar(y=labels, x=ys, name=head[c], orientation="h", marker={"color": color},
                                 hovertemplate="%{y}: %{x}<extra>" + head[c] + "</extra>"))
    apply_template(fig)
    fig.update_layout(height=300 if spec["form"] == "line" else max(200, 26 * len(labels) + 70),
                      margin={"l": 8, "r": 24, "t": 8, "b": 36}, barmode="group",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font={"family": "Poppins, sans-serif", "size": 12},
                      showlegend=len(spec["cols"]) > 1, legend={"orientation": "h", "y": -0.18})
    fig.update_xaxes(zeroline=False, automargin=True)
    fig.update_yaxes(automargin=True)
    if spec["form"] != "line":
        fig.update_yaxes(autorange="reversed")
    if spec["form"] == "rank":
        fig.update_xaxes(autorange="reversed", title={"text": head[spec["cols"][0]] + " (lower is better)"})
    title = item.get("title") or item.get("q") or "Chart"
    return html.Div([
        html.Div([html.Span(title, className="aspire-chat-card-title", title=title)], className="aspire-chat-card-head"),
        dcc.Graph(figure=fig, config={**GRAPH_CONFIG, "responsive": True}, className="aspire-chat-graph"),
    ], className="aspire-chat-card")


# -------------------------------------------------------------------------------------------------- trace
def fmt_ms(ms) -> str:
    ms = float(ms or 0)
    return f"{round(ms)} ms" if ms < 1000 else f"{ms / 1000:.{2 if ms < 10000 else 1}f} s"


def fmt_tok(n) -> str:
    n = int(n or 0)
    return f"{n / 1000:.{0 if n >= 10000 else 1}f}k" if n >= 1000 else str(n)


def shape_trace(turn: dict | None) -> dict:
    """The waterfall model of one answer: rows (kind, depth, name, t, ms, tok, detail), the node path, KPIs.
    Uses `trace.spans` (k = node | llm | tool; node rows at depth 0, model and tool calls nested under them);
    an older engine with only `trace.hops` ('squash_agent:2916ms') gets the hops laid end to end (approx)."""
    turn = turn or {}
    tr, us = turn.get("trace") or {}, turn.get("usage") or {}
    spans = [s for s in (tr.get("spans") or []) if isinstance(s, dict) and s.get("k") in ("node", "llm", "tool")]
    rows, path, approx = [], [], False
    order = {"node": 0, "llm": 1, "tool": 1}
    for s in sorted(spans, key=lambda s: (float(s.get("t") or 0), order[s["k"]]))[:MAX_SPANS]:
        name = s.get("name") or s.get("node") or s["k"]
        t, ms = float(s.get("t") or 0), float(s.get("ms") or 0)
        bits = ["model call" if s["k"] == "llm" else s["k"], fmt_ms(ms), "starts +" + fmt_ms(t)]
        if s.get("node") and s["k"] != "node":
            bits.append("in " + s["node"])
        tok = ""
        if s["k"] == "llm" and (s.get("in") or s.get("out")):
            tok = f"{fmt_tok(s.get('in'))}/{fmt_tok(s.get('out'))}"
            bits.append(f"{fmt_tok(s.get('in'))} in / {fmt_tok(s.get('out'))} out"
                        + (f" ({fmt_tok(s.get('cached'))} cached)" if s.get("cached") else ""))
        if s.get("calls"):
            bits.append("asked for " + ", ".join(map(str, s["calls"])))
        if s.get("err"):
            bits.append("error")
        rows.append({"kind": "err" if s.get("err") else s["k"], "depth": 0 if s["k"] == "node" else 1, "name": name,
                     "t": t, "ms": ms, "tok": tok, "detail": f"{name}: " + ", ".join(bits)})
        step = s.get("node") if s["k"] == "llm" else name      # a model call puts control back in its node
        if step and (not path or path[-1] != step):
            path.append(step)
    if not rows:
        at = 0.0
        for h in tr.get("hops") or []:
            m = re.match(r"^(.*?):\s*(\d+(?:\.\d+)?)\s*ms$", str(h))
            name, ms = (m.group(1), float(m.group(2))) if m else (str(h), 0.0)
            rows.append({"kind": "node", "depth": 0, "name": name, "t": at, "ms": ms, "tok": "",
                         "detail": f"{name}: node, {fmt_ms(ms)} (approximate start)"})
            at += ms
            if not path or path[-1] != name:
                path.append(name)
        approx = bool(rows)
    end = max((r["t"] + r["ms"] for r in rows), default=0)
    llm = us.get("llm_calls") if isinstance(us.get("llm_calls"), int) else tr.get("llm_calls")
    in_tok = us.get("input_tokens")
    return {
        "rows": rows, "path": path, "approx": approx,
        "dropped": int(tr.get("spans_dropped") or 0) + max(0, len(spans) - MAX_SPANS),
        "total": max(end, float(turn.get("ms") or 0), 1.0), "fast": llm == 0,
        "kpis": {"total_ms": turn.get("ms") or end or None, "llm_calls": llm, "llm_ms": tr.get("llm_ms"),
                 "tools": tr.get("tool_calls") if isinstance(tr.get("tool_calls"), int) else len(turn.get("tools_used") or []),
                 "tool_ms": tr.get("tool_ms"), "tool_errors": tr.get("tool_errors") or 0,
                 "in_tok": in_tok, "out_tok": us.get("output_tokens"),
                 "cached_share": (tr["cached_tokens"] / in_tok) if tr.get("cached_tokens") and in_tok else None,
                 "cost": us.get("cost_usd")},
    }


def _kpi(label, value, sub=""):
    return html.Div([html.Div(label, className="aspire-chat-kpi-label"),
                     html.Div(value, className="aspire-chat-kpi-value"),
                     html.Div(sub, className="aspire-chat-kpi-sub") if sub else None], className="aspire-chat-kpi")


def trace_view(turn: dict | None):
    """The Trace tab for one turn: KPI strip, node path, and the span waterfall (bars positioned by start
    offset and width = duration, as a % of the run). Returns None when the turn carries no trace."""
    if not turn:
        return None
    x, k = shape_trace(turn), None
    k = x["kpis"]
    if not x["rows"] and k["llm_calls"] is None and not turn.get("agent"):
        return None
    cost = k["cost"]
    kids = [html.Div(turn.get("q") or "", className="aspire-chat-trace-q"), html.Div([
        _kpi("Total", fmt_ms(k["total_ms"]) if k["total_ms"] else "-"),
        _kpi("Model calls", "-" if k["llm_calls"] is None else str(k["llm_calls"]),
             fmt_ms(k["llm_ms"]) if k["llm_ms"] is not None and k["llm_calls"] else ("fast path" if x["fast"] else "")),
        _kpi("Tools", str(k["tools"]), (fmt_ms(k["tool_ms"]) if k["tool_ms"] is not None and k["tools"] else "")
             + (f"{', ' if k['tool_ms'] is not None and k['tools'] else ''}{k['tool_errors']} failed" if k["tool_errors"] else "")),
        _kpi("Tokens in / out", "-" if k["in_tok"] is None else f"{fmt_tok(k['in_tok'])} / {fmt_tok(k['out_tok'])}",
             f"{round(k['cached_share'] * 100)}% cached" if k["cached_share"] is not None else ""),
        _kpi("Cost", "-" if cost is None else (f"${cost:.4f}" if cost < 0.01 else f"${cost:.2f}")),
    ], className="aspire-chat-kpis")]
    if x["path"] or x["fast"] or turn.get("agent"):
        flow = [html.Span("Fast path, no model", className="aspire-pill aspire-pill--gold")] if x["fast"] else []
        for i, n in enumerate(x["path"] or ([turn["agent"]] if turn.get("agent") else [])):
            if i:
                flow.append(html.Span("›", className="aspire-chat-flow-sep", **{"aria-hidden": "true"}))
            flow.append(html.Span(n, className="aspire-chat-flow-node"))
        kids.append(html.Div(flow, className="aspire-chat-flow", **{"aria-label": "Node path"}))
    if x["rows"]:
        total = x["total"]
        ticks = [html.Span(fmt_ms(f * total), style={"left": f"{f * 100:g}%"}) for f in (0, .25, .5, .75, 1)]
        items = []
        for r in x["rows"]:
            left = min(99.5, r["t"] / total * 100)
            width = max(0.6, min(100 - left, r["ms"] / total * 100))
            items.append(html.Li([
                html.Span([html.Span(r["name"], className="aspire-chat-tr-name"),
                           html.Span(fmt_ms(r["ms"]) + (f" · {r['tok']}" if r["tok"] else ""),
                                     className="aspire-chat-tr-ms")], className="aspire-chat-tr-label"),
                html.Span(html.Span(className="aspire-chat-tr-bar", style={"left": f"{left:.2f}%", "width": f"{width:.2f}%"}),
                          className="aspire-chat-tr-track"),
            ], className=f"aspire-chat-tr-row is-{r['kind']}" + (" is-child" if r["depth"] else ""), tabIndex=0,
                title=r["detail"], **{"aria-label": r["detail"], "data-kind": r["kind"]}))
        note = ("Timings from the engine's hop list; start times are approximate." if x["approx"]
                else "Hover or focus a row for detail.") + (f" {x['dropped']} spans not shown." if x["dropped"] else "")
        kids.append(html.Div([
            html.Div([html.Span(), html.Div(ticks, className="aspire-chat-tr-ticks")], className="aspire-chat-tr-axis",
                     **{"aria-hidden": "true"}),
            html.Ol(items, className="aspire-chat-tr-rows", **{"aria-label": "Trace spans, in start order"}),
            html.Div([html.Div([html.Span(t, className=f"is-{t if t != 'model' else 'llm'}")
                                for t in ("node", "model", "tool", "err")], className="aspire-chat-tr-legend",
                               **{"aria-hidden": "true"}),
                      html.Div(note, className="aspire-chat-tr-note")], className="aspire-chat-tr-foot"),
        ], className="aspire-chat-trace"))
    if turn.get("tools_used"):
        kids.append(html.Div([html.Span("Tools used", className="aspire-chat-card-sub")]
                             + [html.Span(t, className="aspire-pill aspire-pill--archived") for t in turn["tools_used"]],
                             className="aspire-chat-toolset"))
    return html.Div(kids, className="aspire-chat-traceview")


# ------------------------------------------------------------------------------------------------ the tabs
def _empty(title, text):
    return html.Div([html.Div(title, className="aspire-chat-empty-title"), html.Div(text)], className="aspire-chat-empty")


def render_workspace(data: dict | None):
    """turns store -> (tables, charts, trace, counts). Tables and charts list every turn newest first; the
    trace is the selected turn (`sel`, default the newest). counts = {tables, charts, trace} for tab labels."""
    data = data or {}
    turns = [t for t in (data.get("turns") or []) if isinstance(t, dict)]
    items = []
    for ti in range(len(turns) - 1, -1, -1):
        for k, tb in enumerate(tables_from_markdown(turns[ti].get("answer") or "")):
            items.append((ti, k, {**tb, "q": turns[ti].get("q")}))
    tables = [table_card(tb, f"{ti}-{k}") for ti, k, tb in items]
    charts = [c for c in (chart_card(tb) for _, _, tb in items if tb["chart"]) if c is not None]
    sel = data.get("sel")
    turn = turns[sel] if isinstance(sel, int) and 0 <= sel < len(turns) else (turns[-1] if turns else None)
    trace = trace_view(turn)
    counts = {"tables": len(tables), "charts": len(charts), "trace": len(shape_trace(turn)["rows"]) if trace else 0}
    if not tables:
        tables = [_empty("No tables yet", "Ask for a ranking, a results list or a head-to-head. Every table in an "
                                          "answer lands here, with podium places marked.")]
    if not charts:
        charts = [_empty("No charts yet", "Any answer table with numbers gets a chart here: progressions as lines, "
                                          "marks as bars, rankings as dots.")]
    if trace is None:
        trace = _empty("No trace yet", "The trace of the last answer shows up here: the path through the graph and "
                                       "every model and tool call on a timeline, with tokens and cost.")
    return tables, charts, trace, counts


TAB_LABELS = (("answer", "Answer"), ("tables", "Tables"), ("charts", "Charts"), ("trace", "Trace"))


def tab_labels(counts: dict | None) -> list[str]:
    counts = counts or {}
    return [lab + (f" ({counts[v]})" if counts.get(v) else "") for v, lab in TAB_LABELS]


def pane_hidden(value: str | None) -> list[bool]:
    """Which panes hide for the active tab value (answer | tables | charts | trace); unknown = answer."""
    value = value if value in dict(TAB_LABELS) else "answer"
    return [v != value for v, _ in TAB_LABELS]
