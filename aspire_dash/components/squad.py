"""Squad overview components (v0.107, promoted from endurance-dashboard Group Overview,
shaped with High Management Overview so both apps share one card).

    percentile_ring(pct, band)          conic ring, 'P73 / PCTL'; None = quiet dash
    tier_card(name, ...)                band-tinted athlete card, one big number
    spotlight_hero(index, name, ...)    one athlete large: tinted identity + stat columns
    spotlight_thumb(index, name, ...)   tap-to-spotlight chip for the strip
    spotlight(heroes, thumbs, id=...)   prev/next + position + heroes + strip
    register_spotlight(id, filter_id)   clientside nav (zero server hits)
    view_switch(toggle_id, views)       clientside show/hide of view containers
    stat_chip(value, label)             '12 SQUAD' inline KPI for a top bar
    meta_line(parts)                    'QAT · 16.7y · U18' with soft separators

BANDS ARE DATA. A card takes ``band="<key>"`` and gets class ``ad-band-<key>``, which
sets four CSS variables: ``--ad-tier`` (band fill), ``--ad-tier-ink`` (band text),
``--ad-tier-deep`` (ring, hero gradient, active outline), ``--ad-tier-soft``. Shipped
keys: ``target`` (gold), ``future`` (teal), ``squad`` (grey/navy, the default). An app
adds its own in its CSS without forking::

    .ad-band-gcc { --ad-tier:#8fb3e0; --ad-tier-ink:#0b2545; --ad-tier-deep:#1d4f91; --ad-tier-soft:#e6eef9; }

Styling in ``assets/07_squad_bands.css``.
"""
from __future__ import annotations

import re

from dash import ALL, Input, Output, State, clientside_callback, dcc, html

from ..athlete import athlete_avatar, _initials

__all__ = [
    "percentile_ring", "tier_card", "spotlight_hero", "spotlight_thumb", "spotlight",
    "register_spotlight", "view_switch", "stat_chip", "meta_line", "STATUS_TONES", "photo_card",
]

# status pill (label, tone): background, text
STATUS_TONES = {"ok": ("#dcfce7", "#166534"), "warn": ("#fef3c7", "#92400e"),
                "bad": ("#fee2e2", "#991b1b"), "unknown": ("#f1f5f9", "#64748b")}
_KEY = re.compile(r"[^a-z0-9_-]+")


def _band_cls(band) -> str:
    return "ad-band-" + (_KEY.sub("-", str(band or "squad").lower()).strip("-") or "squad")


def _data_attrs(data) -> dict:
    return {f"data-{k}": str(v) for k, v in (data or {}).items() if v is not None}


def _is_win(pos) -> bool:
    """1 / '1' / '1st' / 'gold' is a win; '10th', '11', '1:52.4' are not."""
    return str(pos).strip().lower() in {"1", "1st", "gold", "winner"}


def meta_line(parts):
    """Join non-empty parts (strings or components) with soft '·' separators."""
    out = []
    for p in [p for p in parts if p not in (None, "", [])]:
        if out:
            out.append(html.Span("·", className="ad-sep"))
        out.append(p if not isinstance(p, str) else html.Span(p))
    return out


def percentile_ring(pct, band="squad", size: str = "md", caption: str = "PCTL", prefix: str = "P"):
    """Conic ring filled to `pct` in the band's deep colour. None = quiet '–' ring."""
    if pct is None:
        return html.Div(html.Span("–", className="ad-ring-num"),
                        className=f"ad-ring ad-ring-{size} is-empty {_band_cls(band)}",
                        title="No percentile")
    p = max(0.0, min(100.0, float(pct)))
    return html.Div(html.Div([html.Span(f"{prefix}{p:.0f}", className="ad-ring-num"),
                              html.Span(caption, className="ad-ring-cap")], className="ad-ring-hole"),
                    className=f"ad-ring ad-ring-{size} {_band_cls(band)}", role="img",
                    **{"aria-label": f"Percentile {p:.0f}"},
                    style={"background": f"conic-gradient(var(--ad-tier-deep) 0 {p:.1f}%, #e2e8f0 0)"})


def _attendance(att):
    if att is None:
        return None
    week, season = att
    tone = ("none" if season is None else "good" if season >= 95 else "mid" if season >= 90 else "low")
    pct = (lambda v: f"{v:.0f}%" if v is not None else "–")
    return html.Div([
        html.Span([html.Span(f"wk {pct(week)}"), html.Span(" · season ", className="ad-muted"),
                   html.B(pct(season))], className="ad-att"),
        html.Div(html.Div(className=f"ad-att-fill is-{tone}",
                          style={"width": f"{max(0, min(100, season or 0)):.0f}%"}),
                 className="ad-att-bar")], className="ad-att-wrap")


def tier_card(name, *, photo=None, band="squad", band_label=None, corner=None, sub=None,
              value=None, scope=None, value_label=None, value_sub=None, pct=None,
              position=None, status=None, attendance=None, footer=None, href=None,
              link: str = "a", data=None, avatar_size="lg", ring: bool = False, id=None):
    """A small band-tinted athlete card.

    Band strip (``band_label`` left, ``corner`` right, e.g. 'Grade 3'), avatar + name +
    `sub` (one string 'Squash · PSA · 19.2y' or a list for ``meta_line``), then the ONE
    big number: optional ``percentile_ring(pct)`` beside ``value_label`` / ``value`` /
    ``scope`` ('#6' 'world') / ``value_sub``. ``value=None`` shows a quiet '–'.
    ``ring=True`` keeps a quiet ring slot even when ``pct`` is None.

    Optional, each left out when None: ``position`` badge (podium 1-5), ``status`` pill
    ``(label, tone)`` with tone in ok/warn/bad/unknown, ``attendance`` ``(week%, season%)``
    bar, ``footer`` (any component, e.g. a next-step bar). ``href`` makes the whole card
    a link (``link="dcc"`` for ``dcc.Link``). ``data`` adds ``data-*`` attributes (used
    by filters, e.g. ``{"band": "U18"}``)."""
    has_value = value is not None
    main = []
    if pct is not None or ring:
        main.append(percentile_ring(pct, band))
    vblock = [html.Span(value_label, className="ad-card-vlabel")] if value_label else []
    vblock.append(html.Span([html.Span(str(value) if has_value else "–", className="ad-card-value"),
                             html.Span(f" {scope}", className="ad-card-scope") if scope else None]))
    if value_sub:
        vblock.append(html.Span(value_sub, className="ad-card-vsub"))
    main.append(html.Div(vblock, className="ad-card-vblock"))
    foot = []
    if status is not None:
        bg, fg = STATUS_TONES.get(status[1] if len(status) > 1 else "unknown", STATUS_TONES["unknown"])
        foot.append(html.Span(status[0], className="ad-status", style={"background": bg, "color": fg}))
    att = _attendance(attendance)
    if att is not None:
        foot.append(att)
    if footer is not None:
        foot.append(footer)
    children = [
        html.Div([html.Span((band_label or "").upper()), html.Span(corner or "")],
                 className="ad-card-band"),
        html.Div([athlete_avatar(photo, name, size=avatar_size),
                  html.Div([html.Div(name or "Unknown", className="ad-card-name"),
                            html.Div(meta_line(sub) if isinstance(sub, (list, tuple)) else sub,
                                     className="ad-card-sub") if sub else None],
                           className="ad-card-idtext")], className="ad-card-id"),
        html.Div(main, className="ad-card-main"),
    ]
    if position is not None:
        children.append(html.Span(str(position), className=f"ad-pos ad-pos-{position}",
                                  **{"aria-label": f"Position {position}"}))
    if foot:
        children.append(html.Div(foot, className="ad-card-foot"))
    kw = {"id": id} if id is not None else {}
    card = html.Div(children, className=f"ad-tier-card {_band_cls(band)}", **kw)
    attrs = _data_attrs(data)
    if href is None:
        return html.Div(card, className="ad-tier-cell", **attrs) if attrs else card
    if link == "dcc":
        return html.Div(dcc.Link(card, href=href, className="ad-tier-link"), className="ad-tier-cell", **attrs)
    return html.A(card, href=href, className="ad-tier-link ad-tier-cell", **attrs)


def spotlight_hero(index, name, *, photo=None, band="squad", band_label=None, sub=None,
                   chips=(), value_label=None, value=None, value_sub=None, pct=None,
                   pct_text=None, bars=(), bars_label=None, rows=(), rows_label=None,
                   href=None, link_text="Open athlete page", data=None):
    """One athlete large. Left: band-gradient identity panel (avatar, name, `sub`,
    `chips` strings, link). Right: stat columns, each left out when empty:
    - value block: `value_label`, big `value`, `value_sub`, ring(`pct`) + `pct_text`
    - `bars`: ``[(label, pct 0-100), ...]`` mini column chart (e.g. season bests)
    - `rows`: ``[{"date", "title", "result", "pos"?}, ...]`` (e.g. last races; pos 1 / '1st' / 'gold'
      gets the gold chip). Only index 0 is visible at first; ``register_spotlight``
      switches."""
    cols = [html.Div([
        html.Span(value_label or "", className="ad-cap"),
        html.Span(value if value is not None else "–", className="ad-hero-value"),
        html.Span(value_sub or "", className="ad-hero-sub"),
        html.Div([percentile_ring(pct, band, "lg"),
                  html.Span(pct_text or ("No percentile" if pct is None else ""), className="ad-hero-ringtext")],
                 className="ad-hero-ringrow")], className="ad-hero-col")]
    if bars:
        cols.append(html.Div([html.Span(bars_label or "", className="ad-cap"), html.Div([
            html.Div([html.Span(f"P{v:.0f}", className="ad-bar-num"),
                      html.Div(className="ad-bar", style={"height": f"{max(4, v * 1.2):.0f}px"}),
                      html.Span(lbl, className="ad-bar-year")], className="ad-bar-col")
            for lbl, v in bars], className="ad-bars")], className="ad-hero-col"))
    if rows:
        cols.append(html.Div([html.Span(rows_label or "", className="ad-cap"), *[html.Div([
            html.Div([html.Span(r.get("date", ""), className="ad-row-date"),
                      html.Span(r.get("title", ""), className="ad-row-title")], className="ad-row-left"),
            html.Span(r.get("result", ""), className="ad-row-res"),
            html.Span(r["pos"], className="ad-row-pos" + (" is-win" if _is_win(r["pos"]) else ""))
            if r.get("pos") else None], className="ad-row") for r in rows]], className="ad-hero-col"))
    left = [html.Span((band_label or "").upper(), className="ad-hero-tier"),
            athlete_avatar(photo, name, size=112),
            html.Div(name or "Unknown", className="ad-hero-name")]
    if sub:
        left.append(html.Div(meta_line(sub) if isinstance(sub, (list, tuple)) else sub,
                             className="ad-hero-meta"))
    if chips:
        left.append(html.Div([html.Span(c, className="ad-hero-chip") for c in chips if c],
                             className="ad-hero-chips"))
    if href:
        left.append(html.A(link_text, href=href, className="ad-hero-link"))
    return html.Div([html.Div(left, className="ad-hero-left"), html.Div(cols, className="ad-hero-right")],
                    className=f"ad-hero {_band_cls(band)}",
                    style=None if index == 0 else {"display": "none"},
                    **{"data-spot": str(index), **_data_attrs(data)})


def spotlight_thumb(index, name, *, photo=None, band="squad", sub=None, data=None, id: str = "spot"):
    """Thumb chip for the strip; clicking it spotlights `index`."""
    return html.Button(
        [athlete_avatar(photo, name, size=36),
         html.Span([html.Span(name or "Unknown", className="ad-thumb-name"),
                    html.Span(sub or "", className="ad-thumb-sub")], className="ad-thumb-text")],
        id={"type": f"{id}-thumb", "index": index}, n_clicks=0,
        className=f"ad-thumb {_band_cls(band)}" + (" is-active" if index == 0 else ""),
        **{"data-spot": str(index), "aria-label": f"Spotlight {name or 'athlete'}", **_data_attrs(data)})


def spotlight(heroes, thumbs, *, id: str = "spot", strip_label: str = "Squad · tap to spotlight"):
    """Carousel shell: prev / 'i / n' / next, the heroes, the thumb strip. Element ids:
    ``{id}-root``, ``{id}-prev``, ``{id}-next``, ``{id}-pos``, store ``{id}-idx``.
    Call ``register_spotlight(id)`` once at import time."""
    n = len(heroes)
    return html.Div(id=f"{id}-root", className="ad-spotlight", children=[
        dcc.Store(id=f"{id}-idx", data=0),
        html.Div([
            html.Button(html.I(className="fas fa-chevron-left"), id=f"{id}-prev", n_clicks=0,
                        className="ad-nav-btn", **{"aria-label": "Previous athlete"}),
            html.Span(f"1 / {n}" if n else "", id=f"{id}-pos", className="ad-spot-pos"),
            html.Button(html.I(className="fas fa-chevron-right"), id=f"{id}-next", n_clicks=0,
                        className="ad-nav-btn", **{"aria-label": "Next athlete"}),
        ], className="ad-spot-nav"),
        html.Div(heroes, className="ad-heroes"),
        html.Div(strip_label, className="ad-cap ad-strip-cap") if strip_label else None,
        html.Div(thumbs, className="ad-strip"),
    ])


_SPOT_JS = """
function(_p, _n, _thumbs, filt, cur) {
    const root = document.getElementById('%(id)s-root');
    if (!root) return [cur || 0, ''];
    const strip = root.querySelectorAll('.ad-thumb');
    const heroes = root.querySelectorAll('.ad-hero');
    if (!strip.length) return [cur || 0, ''];
    const attr = '%(attr)s';
    const inF = (el) => !filt || filt === '%(all)s' || el.getAttribute(attr) === filt;
    const visible = [];
    strip.forEach((t) => {
        const ok = inF(t);
        t.style.display = ok ? '' : 'none';
        if (ok) visible.push(Number(t.getAttribute('data-spot')));
    });
    if (!visible.length) return [cur || 0, '0 / 0'];
    const ctx = window.dash_clientside.callback_context;
    let trig = ctx.triggered_id;
    if (trig === undefined && ctx.triggered && ctx.triggered.length) {
        const pid = ctx.triggered[0].prop_id.split('.')[0];
        try { trig = JSON.parse(pid); } catch (e) { trig = pid; }
    }
    let idx = visible.includes(cur) ? cur : visible[0];
    let k = visible.indexOf(idx);
    if (trig === '%(id)s-prev') k = (k - 1 + visible.length) %% visible.length;
    else if (trig === '%(id)s-next') k = (k + 1) %% visible.length;
    else if (trig && typeof trig === 'object' && trig.type === '%(id)s-thumb'
             && visible.includes(trig.index)) k = visible.indexOf(trig.index);
    idx = visible[k];
    heroes.forEach((h) => { h.style.display = Number(h.getAttribute('data-spot')) === idx ? '' : 'none'; });
    strip.forEach((t) => { t.classList.toggle('is-active', Number(t.getAttribute('data-spot')) === idx); });
    const act = root.querySelector('.ad-thumb.is-active');
    if (act && act.scrollIntoView) act.scrollIntoView({block: 'nearest', inline: 'nearest'});
    return [idx, (k + 1) + ' / ' + visible.length];
}
"""


def register_spotlight(id: str = "spot", filter_id: str | None = None,
                       filter_attr: str = "data-band", all_value: str = "_ALL_"):
    """Clientside prev / next / thumb navigation for ``spotlight(id=...)``. With
    `filter_id` (any component with a ``value``) it only steps through heroes/thumbs
    whose `filter_attr` equals that value (``all_value`` = no filter)."""
    inputs = [Input(f"{id}-prev", "n_clicks"), Input(f"{id}-next", "n_clicks"),
              Input({"type": f"{id}-thumb", "index": ALL}, "n_clicks")]
    js = _SPOT_JS % {"id": id, "attr": filter_attr, "all": all_value}
    if filter_id:
        inputs.append(Input(filter_id, "value"))
    else:
        js = js.replace("function(_p, _n, _thumbs, filt, cur)", "function(_p, _n, _thumbs, cur, _u)")
        js = js.replace("const attr", "const filt = null;\n    const attr")
    clientside_callback(js, Output(f"{id}-idx", "data"), Output(f"{id}-pos", "children"),
                        *inputs, State(f"{id}-idx", "data"))


def view_switch(toggle_id: str, views: dict):
    """Clientside show/hide: ``views = {"cards": "cards-box", "spotlight": "spot-box"}``
    maps each toggle value to a container id; only the selected one shows. Pair with
    ``aspire_tabs(toggle_id, ..., persistence="session")`` so the choice survives
    navigation; pages read the choice as ``Input(toggle_id, "value")``. Call once at
    import time."""
    keys = list(views)
    js = ("function(v){ const k = %s; return k.map(x => ({display: x === v ? '' : 'none'})); }"
          % ("[" + ",".join(f"'{k}'" for k in keys) + "]"))
    clientside_callback(js, *[Output(cid, "style") for cid in views.values()], Input(toggle_id, "value"))


def stat_chip(value, label, color: str = "#0f172a"):
    """Inline KPI for a one-line top bar: big number + small caps label, never wraps."""
    return html.Div([html.Span(str(value), className="ad-stat-chip-num", style={"color": color}),
                     html.Span(label, className="ad-stat-chip-label")], className="ad-stat-chip")


# --------------------------------------------------------------------------- #
# photo card (v0.109): squash PSA-broadcast style, band-tinted (Kenny 2026-10-16,
# option B from the endurance mock: PB in the tab, percentile ring on the photo)
# --------------------------------------------------------------------------- #
PHOTO_TONES = {"bad": "is-bad", "warn": "is-warn", "ok": "is-ok"}


def _split_name(name):
    parts = [p for p in (name or "").split() if p]
    if len(parts) < 2:
        return "", (name or "Unknown")
    return " ".join(parts[:-1]), parts[-1]


def photo_card(name, *, photo=None, band="squad", band_label=None, tab_caption=None,
               tab_value=None, pct=None, injury=None, recovery=None, flag=None, meta=None,
               chip=None, stats=None, last=None, attendance=None, hover=None, href=None,
               link: str = "a", data=None, id=None):
    """A photo-led athlete card, broadcast style, tinted by ``band`` (same
    ``ad-band-<key>`` variables as ``tier_card``).

    Photo (or big initials) fading into the band's deep colour; top-left tab
    ``tab_caption`` over ``tab_value`` (e.g. 'TARGET · 800M PB' / '1:50.85'); the
    ``percentile_ring(pct)`` on the photo bottom-right; status top-right: ``injury``
    ``(text, tone)`` pill (tone bad/warn), WHOOP-style ``recovery`` 0-100 ring, ``flag``
    ``(text, tone)`` pill (tone warn/bad). First name light over SURNAME caps.

    Below: ``meta`` (string or list for ``meta_line``) + optional ``chip`` text,
    ``stats`` ``[(caption, value), ...]`` (up to 3), ``last`` ``{"title", "result",
    "ago", "win"}`` and an ``attendance`` % bar on the bottom edge. Each part is left
    out when None. ``hover`` = the card's tooltip (e.g. a stored short summary)."""
    first, surname = _split_name(name)
    photo_el = (html.Img(src=photo, alt=name or "", className="ad-pc-img")
                if photo else html.Div(_initials(name), className="ad-pc-img is-initials"))
    over = [photo_el, html.Div(className="ad-pc-shade")]
    if tab_value is not None or tab_caption:
        over.append(html.Div([html.Span(tab_caption or "", className="ad-pc-tab-cap"),
                              html.Span(str(tab_value) if tab_value is not None else "–",
                                        className="ad-pc-tab-val")], className="ad-pc-tab"))
    status = []
    if injury:
        status.append(html.Span([html.I(className="fa-solid fa-kit-medical", **{"aria-hidden": "true"}),
                                 html.Span(injury[0])],
                                className=f"ad-pc-pill {PHOTO_TONES.get(injury[1] if len(injury) > 1 else 'bad', 'is-bad')}"))
    if recovery is not None:
        r = max(0.0, min(100.0, float(recovery)))
        col = "#16a34a" if r >= 67 else ("#ca8a04" if r >= 34 else "#dc2626")
        status.append(html.Div(html.Span(f"{r:.0f}", className="ad-pc-rec-num"), className="ad-pc-rec",
                               title=f"Recovery {r:.0f}% today",
                               style={"background": f"conic-gradient({col} 0 {r:.1f}%, rgba(255,255,255,.25) 0)"}))
    if flag:
        status.append(html.Span(flag[0], className=f"ad-pc-pill {PHOTO_TONES.get(flag[1] if len(flag) > 1 else 'warn', 'is-warn')}"))
    if status:
        over.append(html.Div(status, className="ad-pc-status"))
    if pct is not None:
        over.append(html.Div(percentile_ring(pct, band), className="ad-pc-ring"))
    over.append(html.Div([html.Span(first, className="ad-pc-first"),
                          html.Span(surname.upper(), className="ad-pc-last")], className="ad-pc-name"))
    body = [html.Div(over, className="ad-pc-photo")]
    if meta or chip:
        body.append(html.Div([html.Span(meta_line(meta) if isinstance(meta, (list, tuple)) else meta,
                                        className="ad-pc-meta-text") if meta else None,
                              html.Span(chip, className="ad-pc-chip") if chip else None],
                             className="ad-pc-meta"))
    if stats:
        body.append(html.Div([html.Div([html.Span(c, className="ad-pc-stat-cap"),
                                        html.Span(v if v not in (None, "") else "–",
                                                  className="ad-pc-stat-val")], className="ad-pc-stat")
                              for c, v in stats[:3]], className="ad-pc-stats"))
    if last:
        win = bool(last.get("win"))
        body.append(html.Div([
            html.Span(className="ad-pc-dot" + (" is-win" if win else "")),
            html.Div([html.Span(last.get("title") or "", className="ad-pc-last-title"),
                      html.Span(last.get("result") or "", className="ad-pc-last-res" + (" is-win" if win else ""))],
                     className="ad-pc-last-text"),
            html.Span(last.get("ago") or "", className="ad-pc-ago")], className="ad-pc-lastrow"))
    if attendance is not None:
        a = max(0.0, min(100.0, float(attendance)))
        tone = "good" if a >= 95 else ("mid" if a >= 90 else "low")
        body.append(html.Div(html.Div(className=f"ad-att-fill is-{tone}", style={"width": f"{a:.0f}%"}),
                             className="ad-pc-att", title=f"Attendance {a:.0f}%"))
    kw = {"id": id} if id is not None else {}
    card = html.Div(body, className=f"ad-pc {_band_cls(band)}", **kw)
    attrs = _data_attrs(data)
    if hover:
        attrs["title"] = hover
    if href is None:
        return html.Div(card, className="ad-tier-cell", **attrs)
    if link == "dcc":
        return html.Div(dcc.Link(card, href=href, className="ad-tier-link"), className="ad-tier-cell", **attrs)
    return html.A(card, href=href, className="ad-tier-link ad-tier-cell", **attrs)
