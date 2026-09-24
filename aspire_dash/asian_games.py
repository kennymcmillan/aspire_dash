"""Asian Games design language (v0.91).

Components modelled on the Aichi-Nagoya 2026 sites (aichi-nagoya2026.org and
results.asiangames2026.org): the curved wave hero, glass navigation with a
disciplines mega-menu, row-card results tables, expandable medal table, the
lifting date strip, schedule rows and the athlete profile card.

Everything renders inside :func:`ag_shell`, which wraps the page in ``.ag-app``.
All styling lives in ``assets/03_asian_games.css`` and is scoped to that class,
so these components never restyle the rest of an Aspire app. When a page inside
an Aspire ``page_layout`` renders an ``.ag-app``, the Aspire header hides and the
content padding drops (pure CSS ``:has``), so the section reads as its own app.

    from aspire_dash.asian_games import (
        ag_shell, ag_hero_heading, ag_results_table, ag_medal_table, ...
    )

Interactive groups (pill tabs, sub-tabs, heat strip, date strip) and sortable
table headers are driven by clientside callbacks that AUTO-REGISTER on import,
the same way ``history_modal`` does. Read a group's value from
``Input(ag_choice_id(group), "data")`` and a table's sort state from
``Input(ag_sort_id(table), "data")``.
"""
from __future__ import annotations

import datetime as _dt

from dash import (
    ALL, MATCH, Input, Output, State, clientside_callback, dcc, html,
)

from . import countries as _countries
from .components.nav import _safe_relative

__all__ = [
    "AG_COLORS", "AG_COLORS_GAMES", "AG_DISCIPLINES",
    # shell + hero
    "ag_shell", "ag_topnav", "ag_wave_hero", "ag_hero_heading", "ag_hero_stats",
    "ag_band", "ag_subtab_links", "ag_subtabs", "ag_event_capsule", "ag_footer",
    # headings + small parts
    "ag_page_title", "ag_section_title", "ag_subtitle", "ag_gradient_title",
    "ag_intro", "ag_intro_pill", "ag_status_pill", "ag_medal_icon", "ag_medal_chip",
    "ag_medal_stack", "ag_chip", "ag_legend", "ag_noc", "ag_flag", "ag_athlete_name",
    "ag_athlete_link", "ag_button", "ag_empty",
    # tables + controls
    "ag_choice_id", "ag_pill_tabs", "ag_unit_strip", "ag_date_strip",
    "ag_sort_id", "ag_sort_store", "ag_sort_rows", "ag_results_table",
    "ag_filter_panel", "ag_field", "ag_records_panel",
    # medals + schedule
    "ag_medal_table", "ag_medal_widget", "ag_schedule_unit", "ag_discipline_card",
    # athletes + cards
    "ag_avatar", "ag_athlete_card", "ag_athlete_profile", "ag_sport_tile",
    "ag_news_card", "ag_feature_banner", "ag_stat",
]

# Default palette: Aspire brand colours (brand.yml) mapped onto the Asian Games
# layout. AG_COLORS_GAMES keeps the original Aichi-Nagoya purple and gold for
# ag_shell(..., theme="games").
AG_COLORS = {
    "primary": "#004185", "primary_hover": "#003566", "primary_dark": "#001d3d",
    "primary_light": "#dbeafe", "primary_50": "#eff6ff", "secondary": "#1876ab",
    "gold": "#fbb800", "gold_text": "#c98f00", "gold_light": "#fde68a", "green": "#16a34a",
    "page": "#f1f5f9", "card": "#ffffff", "border": "#e2e8f0", "muted": "#64748b",
    "text": "#1e293b", "navy": "#001d3d",
    "medal_gold": "#eaae47", "medal_silver": "#a7a6a6", "medal_bronze": "#ce8127",
}

AG_COLORS_GAMES = {
    "primary": "#4f3b95", "primary_hover": "#3c2e75", "primary_dark": "#291f55",
    "primary_light": "#d9d4ec", "primary_50": "#f2f0f9", "primary_400": "#8c7cc5",
    "gold": "#d1b100", "gold_light": "#ffec9f", "green": "#2e9a38", "tan": "#bd8d40",
    "page": "#f4f4f4", "card": "#fdfdfd", "border": "#e7e7e7", "muted": "#757575",
    "text": "#333333", "black": "#020d0b",
    "medal_gold": "#eaae47", "medal_silver": "#a7a6a6", "medal_bronze": "#ce8127",
}

# Discipline code -> (label, Font Awesome icon). Font Awesome stands in for the
# official pictograms, which we don't copy.
AG_DISCIPLINES = {
    "ATH": ("Athletics", "fa-person-running"),
    "SWM": ("Swimming", "fa-person-swimming"),
    "SQU": ("Squash", "fa-table-tennis-paddle-ball"),
    "FEN": ("Fencing", "fa-shield-halved"),
    "PAD": ("Padel", "fa-baseball"),
    "TTE": ("Table Tennis", "fa-table-tennis-paddle-ball"),
    "SHO": ("Shooting", "fa-bullseye"),
    "BDM": ("Badminton", "fa-feather"),
    "BK3": ("3x3 Basketball", "fa-basketball"),
    "FBL": ("Football", "fa-futbol"),
    "VBV": ("Beach Volleyball", "fa-volleyball"),
    "CRD": ("Cycling Road", "fa-person-biking"),
    "WLF": ("Weightlifting", "fa-dumbbell"),
    "JUD": ("Judo", "fa-hand-fist"),
    "KTE": ("Karate", "fa-hand"),
    "TKW": ("Taekwondo", "fa-shoe-prints"),
    "EQU": ("Equestrian", "fa-horse"),
    "SAL": ("Sailing", "fa-sailboat"),
    "GLF": ("Golf", "fa-golf-ball-tee"),
    "ESP": ("Esports", "fa-gamepad"),
}

_MEDALS = ("gold", "silver", "bronze")


def _icon(name, extra=""):
    if not name:
        return None
    cls = name if name.startswith("fa-solid") or name.startswith("fa-brands") else f"fa-solid {name}"
    return html.I(className=f"{cls} {extra}".strip())


def _cls(*parts):
    return " ".join(p for p in parts if p)


# ═══════════════════════════════ SHELL + HERO ══════════════════════════════

def ag_topnav(nav_items, active=None, *, disciplines=None, brand_title="Asian Games",
              brand_sub="Aspire design study", brand_mark="26", actions=None,
              disciplines_label="Disciplines"):
    """Logo, glass capsule nav, glass icon buttons and a mobile burger.

    nav_items : list of ``{"label", "href"}``. The item whose href equals
        ``active`` gets the active state.
    disciplines : optional list of ``{"label", "icon", "href"}``; when given, a
        "Disciplines" item opens a frosted 5-column mega-menu with a search box
        (filtered by ``asian_games.js``, no callback).
    actions : list of ``(icon, title)`` for the round glass buttons on the right.
    """
    links = []
    if disciplines:
        tiles = [
            dcc.Link([_icon(d.get("icon")), html.Span(d["label"])],
                     href=_safe_relative(d.get("href", "#")),
                     className="ag-mega__tile")
            for d in disciplines
        ]
        links.append(html.Div([
            html.Button([disciplines_label, _icon("fa-chevron-down")],
                        className="ag-nav__trigger", type="button"),
            html.Div(html.Div([
                dcc.Input(className="ag-mega__search", placeholder="Search disciplines",
                          type="text", debounce=False, autoComplete="off"),
                html.Div(tiles, className="ag-mega__grid"),
                html.Div("No discipline matches that search.", className="ag-mega__empty"),
            ], className="ag-mega__panel"), className="ag-mega"),
        ], className="ag-nav__item", tabIndex="-1"))
    for it in nav_items:
        links.append(dcc.Link(
            [_icon(it.get("icon")), it["label"]] if it.get("icon") else it["label"],
            href=_safe_relative(it["href"]),
            className=_cls("ag-nav__link", "is-active" if it["href"] == active else ""),
        ))

    actions = actions if actions is not None else [
        ("fa-regular fa-star", "Favourites"), ("fa-solid fa-globe", "Language"),
        ("fa-regular fa-clock", "Venue time"),
    ]
    btns = [html.Button(_icon(ic), className="ag-iconbtn ag-glass", title=t, type="button")
            for ic, t in actions]
    btns.append(html.Button(_icon("fa-bars"), className="ag-iconbtn ag-glass ag-burger",
                            title="Menu", type="button", **{"aria-expanded": "false"}))

    return html.Header([
        html.Div([
            html.Div(brand_mark, className="ag-brand__mark"),
            html.Div([html.Div(brand_title, className="ag-brand__title"),
                      html.Div(brand_sub, className="ag-brand__sub")],
                     className="ag-brand__text"),
        ], className="ag-brand"),
        html.Nav(links, className="ag-nav ag-glass"),
        html.Div(btns, className="ag-iconbtns"),
    ], className="ag-topnav")


def ag_wave_hero(children, *, variant="curve", rim=True, animate=True, dip=None,
                 curve_height=None, className=""):
    """The curved hero header with the sweeping wave.

    A black-to-indigo gradient carries a purple and gold swoosh layer and is
    clipped by an SVG ``mask-image`` whose bottom edge is a wide convex curve
    (the path measured from results.asiangames2026.org, swapped for its mobile
    path under 768px). ``rim=True`` adds a second copy of the curve a few pixels
    lower, painted purple to gold, which gives the trailing wave line.

    variant : ``"curve"`` (results pages) or ``"rounded"`` (24px bottom corners,
        as on the Medals and Schedule pages).
    dip : px of padding under the content so the curve has room (default 96).
    curve_height : px height of the curved band at the bottom (default 150).
    """
    style = {}
    if dip is not None:
        style["--ag-hero-dip"] = f"{dip}px"
    if curve_height is not None:
        style["--ag-curve-h"] = f"{curve_height}px"
    cls = _cls("ag-hero", f"ag-hero--{variant}", "" if rim else "ag-hero--no-rim",
               "" if animate else "ag-hero--static", className)
    return html.Div([
        html.Div(className="ag-hero__rim"),
        html.Div(className="ag-hero__mask"),
        *(children if isinstance(children, list) else [children]),
    ], className=cls, style=style or None)


def ag_hero_heading(title, *, eyebrow=None, lead=None, meta=None, actions=None,
                    children=None):
    """Centred hero text block. ``title`` may be a string or components (wrap a
    word in ``html.Em`` to colour it gold). ``meta`` is a list of ``(icon, text)``."""
    body = []
    if eyebrow:
        body.append(html.Div(eyebrow, className="ag-hero__eyebrow"))
    body.append(html.H1(title, className="ag-hero__title"))
    if lead:
        body.append(html.P(lead, className="ag-hero__lead"))
    if meta:
        body.append(html.Div([html.Span([_icon(ic), txt]) for ic, txt in meta],
                             className="ag-hero__meta"))
    if actions:
        body.append(html.Div(actions, className="ag-hero__actions"))
    if children:
        body.extend(children if isinstance(children, list) else [children])
    return html.Div(body, className="ag-hero__body")


def ag_hero_stats(items):
    """Glass stat pills for the hero: list of ``(value, label)``."""
    return html.Div([
        html.Div([html.Div(v, className="ag-hstat__v"), html.Div(l, className="ag-hstat__l")],
                 className="ag-hstat ag-glass")
        for v, l in items
    ], className="ag-hstats")


def ag_band(name, icon=None, tabs=None):
    """The glass discipline band under the nav: pictogram + name, then tabs."""
    return html.Div([
        html.Div([_icon(icon), html.Span(name)], className="ag-band__name"),
        tabs,
    ], className="ag-band ag-glass")


def ag_subtab_links(items, active=None):
    """Uppercase sub-tabs as links: ``[{"label", "href"}]``."""
    return html.Div([
        dcc.Link(it["label"], href=_safe_relative(it["href"]),
                 className=_cls("ag-subtab", "is-active" if it["href"] == active else ""))
        for it in items
    ], className="ag-subtabs")


def ag_event_capsule(name, phase=None, *, status=None, when=None, venue=None):
    """Unit title capsule for the hero, with a status pill and when/where line."""
    row = [html.Div([html.Span(name, className="ag-capsule__name"),
                     html.Span(phase, className="ag-capsule__phase") if phase else None],
                    className="ag-capsule")]
    if status:
        row.append(ag_status_pill(status))
    meta = []
    if when:
        meta.append(("fa-regular fa-clock", when))
    if venue:
        meta.append(("fa-solid fa-location-dot", venue))
    return html.Div([
        html.Div(row, className="ag-capsule-row"),
        html.Div([html.Span([_icon(ic), t]) for ic, t in meta], className="ag-hero__meta") if meta else None,
    ])


def ag_footer(*, brand_title="Asian Games", brand_sub="Aspire design study",
              address=None, socials=None, legal=None):
    """Near-black footer with rounded top corners."""
    address = address or [html.B("Aspire Academy"), html.Br(), "Sports Analytics", html.Br(),
                          "Doha, Qatar"]
    socials = socials if socials is not None else [
        ("fa-brands fa-x-twitter", "X"), ("fa-brands fa-instagram", "Instagram"),
        ("fa-brands fa-youtube", "YouTube"), ("fa-brands fa-linkedin-in", "LinkedIn"),
    ]
    legal = legal or [html.Span("Design study built on aspire_dash. Sample data only."),
                      html.Span("Modelled on the Aichi-Nagoya 2026 results site.")]
    return html.Footer(html.Div([
        html.Div([
            html.Div([
                html.Div("26", className="ag-brand__mark"),
                html.Div([html.Div(brand_title, className="ag-brand__title"),
                          html.Div(brand_sub, className="ag-brand__sub")], className="ag-brand__text"),
            ], className="ag-brand"),
            html.Div(address, className="ag-footer__addr"),
            html.Div([html.Span(_icon(ic), className="ag-social", title=t) for ic, t in socials],
                     className="ag-socials"),
        ], className="ag-footer__grid"),
        html.Div(legal, className="ag-footer__legal"),
    ], className="ag-container"), className="ag-footer")


def ag_shell(children, *, nav_items, active=None, hero=None, hero_variant="curve",
             hero_kwargs=None, disciplines=None, brand_title="Asian Games",
             brand_sub="Aspire design study", footer=True, overlays=None, className="",
             theme="aspire"):
    """Page wrapper that makes every page in a section share one design.

    Renders ``.ag-app`` with the wave hero (the top nav plus ``hero`` content),
    a 1140px content column holding ``children``, and the footer. ``overlays``
    (modals, stores) are appended at the end.

    theme : ``"aspire"`` (default) colours everything with the Aspire palette;
        ``"games"`` switches to the original Aichi-Nagoya purple and gold. A modal
        rendered outside the shell takes the same colours if you give it the
        ``ag-theme--games`` class too.
    """
    topnav = ag_topnav(nav_items, active, disciplines=disciplines,
                       brand_title=brand_title, brand_sub=brand_sub)
    hero_children = [topnav] + (hero if isinstance(hero, list) else ([hero] if hero else []))
    return html.Div([
        ag_wave_hero(hero_children, variant=hero_variant, **(hero_kwargs or {})),
        html.Main(html.Div(children, className="ag-container"), className="ag-main"),
        ag_footer(brand_title=brand_title, brand_sub=brand_sub) if footer is True else (footer or None),
        *(overlays or []),
    ], className=_cls("ag-app", "ag-theme--games" if theme == "games" else "", className))


# ═══════════════════════════════ HEADINGS + SMALL PARTS ════════════════════

def ag_page_title(text):
    """Gold, heavy, uppercase page title."""
    return html.H1(text, className="ag-page-title")


def ag_section_title(text, aside=None):
    """Sticky section title with a black rule. ``aside`` sits on the right."""
    return html.H2([html.Span(text), html.Span(aside, className="ag-section-title__aside") if aside else None],
                   className="ag-section-title")


def ag_subtitle(text):
    return html.Div(text, className="ag-subtitle")


def ag_gradient_title(text):
    """Org-site 64px purple-to-gold gradient heading."""
    return html.H2(text, className="ag-gradient-title")


def ag_intro_pill(text, icon=None):
    return html.Span([_icon(icon), text], className="ag-intro-pill")


def ag_intro(pill, title, lead=None, pill_icon=None):
    """Org-site page intro: lavender pill, gradient title, centred lead."""
    return html.Div([
        ag_intro_pill(pill, pill_icon),
        ag_gradient_title(title),
        html.P(lead, className="ag-intro__lead") if lead else None,
    ], className="ag-intro")


_STATUS_LABELS = {"ready": "Getting ready", "live": "Live"}


def ag_status_pill(status, label=None):
    """Status pill: official, finished, live, running, ready, delayed,
    intermediate, unofficial, scheduled, cancelled. Live and running pulse."""
    s = (status or "scheduled").lower()
    return html.Span(label or _STATUS_LABELS.get(s, s), className=f"ag-status ag-status--{s}")


def ag_medal_icon(kind="gold", title=None):
    """18px two-disc medal icon: gold, silver, bronze or total."""
    return html.Span(className=f"ag-medal ag-medal--{kind}", title=title or kind.title())


def ag_medal_chip(kind, text=None):
    return html.Span([ag_medal_icon(kind), text or kind.title()],
                     className=f"ag-medal-chip ag-medal-chip--{kind}")


def ag_medal_stack(label="Medal"):
    """Three overlapping discs plus a gold label (marks a medal event)."""
    return html.Span([ag_medal_icon("gold"), ag_medal_icon("silver"), ag_medal_icon("bronze"),
                      html.Span(label, className="ag-medal-stack__label") if label else None],
                     className="ag-medal-stack")


def ag_chip(text, variant=None, icon=None):
    """Small chip. variant: purple, gold, outline, live, or None (grey)."""
    return html.Span([_icon(icon), text], className=_cls("ag-chip", f"ag-chip--{variant}" if variant else ""))


def ag_legend(items):
    """Row of legend chips: list of ``(text, variant)``."""
    return html.Div([ag_chip(t, v) for t, v in items], className="ag-legend")


def ag_flag(noc, size="md"):
    url = _countries.flag_url(noc, size=80) if noc else ""
    return html.Img(src=url, alt=noc or "", className=_cls("ag-flag", "ag-flag--sm" if size == "sm" else ""))


def ag_noc(noc, name=None, *, show_name=True, size="md"):
    """Flag (33x22, 3px radius) + NOC code + bold country name."""
    name = name if name is not None else (_countries.name(noc) or noc)
    return html.Span([
        ag_flag(noc, size),
        html.Span([html.Span(noc, className="ag-noc__code"),
                   html.Span(name, className="ag-noc__name") if show_name else None],
                  className="ag-noc__stack"),
    ], className="ag-noc")


def ag_athlete_name(surname, given=None):
    """SURNAME in bold uppercase, given name regular."""
    return html.Span([html.B(surname), f" {given}" if given else None], className="ag-name")


def ag_athlete_link(athlete_id, children):
    """Clickable athlete element. Pages listen to
    ``Input({"type": "ag-athlete", "id": ALL}, "n_clicks")`` to open a profile."""
    return html.Button(children, id={"type": "ag-athlete", "id": str(athlete_id)},
                       n_clicks=0, className="ag-athlete-link", type="button")


def ag_button(text, *, href=None, variant=None, icon=None, id=None, **kw):
    """Button or link. variant: None (solid purple), outline, light, ghost."""
    cls = _cls("ag-btn", f"ag-btn--{variant}" if variant else "")
    inner = [_icon(icon), text] if icon else text
    if href:
        return dcc.Link(inner, href=_safe_relative(href), className=cls)
    extra = {"id": id, "n_clicks": 0} if id is not None else {}
    return html.Button(inner, className=cls, type="button", **extra, **kw)


def ag_empty(text="No results available"):
    return html.Div([_icon("fa-circle-info"), text], className="ag-empty")


# ═══════════════════════════════ CHOICE GROUPS ═════════════════════════════
# One clientside callback serves every pill-tab, sub-tab, heat strip and date
# strip on a page. Each group keeps its value in a dcc.Store whose id is
# ag_choice_id(group); read it as Input(ag_choice_id(group), "data").

def ag_choice_id(group):
    return {"type": "ag-choice-value", "group": group}


def _choice(group, value, children, base, active, **kw):
    return html.Button(children, id={"type": "ag-choice", "group": group, "value": value},
                       n_clicks=0, type="button", className=_cls(base, "is-active" if active else ""), **kw)


def _options(options):
    return [o if isinstance(o, dict) else {"label": o, "value": o} for o in options]


def ag_pill_tabs(group, options, value=None, *, variant=None, center=False):
    """Pill tab group (Start list | Results | Summary). ``variant="outline"``
    gives the 2px bordered medal-page style."""
    opts = _options(options)
    value = value if value is not None else opts[0]["value"]
    return html.Div([
        dcc.Store(id=ag_choice_id(group), data=value),
        *[_choice(group, o["value"], o["label"], "ag-pilltab", o["value"] == value) for o in opts],
    ], className=_cls("ag-pilltabs", f"ag-pilltabs--{variant}" if variant else "",
                      "ag-pilltabs--center" if center else ""))


def ag_subtabs(group, options, value=None):
    """Hero sub-tabs driven by a value (gradient pill + purple underline)."""
    opts = _options(options)
    value = value if value is not None else opts[0]["value"]
    return html.Div([
        dcc.Store(id=ag_choice_id(group), data=value),
        *[_choice(group, o["value"], o["label"], "ag-subtab", o["value"] == value) for o in opts],
    ], className="ag-subtabs")


def ag_unit_strip(group, units, value=None):
    """Heat / unit cards: ``[{"value", "label", "when", "status"}]``. The active
    card is full opacity; the rest fade."""
    value = value if value is not None else (units[0]["value"] if units else None)
    return html.Div([
        dcc.Store(id=ag_choice_id(group), data=value),
        *[_choice(group, u["value"], [
            html.Div(u.get("when", ""), className="ag-unit__when"),
            html.Div(u["label"], className="ag-unit__label"),
            ag_status_pill(u.get("status", "scheduled")),
        ], "ag-unit", u["value"] == value) for u in units],
    ], className="ag-units")


def ag_date_strip(group, days, value=None):
    """Lifting date boxes. ``days``: ``[{"value": "2026-09-24", "medal": bool,
    "today": bool}]``; weekday/day/month come from the ISO date."""
    value = value if value is not None else (days[0]["value"] if days else None)
    items = []
    for d in days:
        dt = _dt.date.fromisoformat(d["value"])
        items.append(_choice(group, d["value"], [
            html.Span(dt.strftime("%a"), className="ag-day__wd"),
            html.Span(str(dt.day), className="ag-day__d"),
            html.Span(dt.strftime("%b"), className="ag-day__m"),
        ], _cls("ag-day", "ag-day--medal" if d.get("medal") else "",
                "ag-day--today" if d.get("today") else ""), d["value"] == value,
            title=dt.strftime("%A %d %B")))
    return html.Div([dcc.Store(id=ag_choice_id(group), data=value), *items], className="ag-days")


clientside_callback(
    """
    function (clicks, ids, classes, current) {
        var nu = window.dash_clientside.no_update;
        var cc = window.dash_clientside.callback_context;
        var trig = cc.triggered_id;
        if (!trig && cc.triggered && cc.triggered.length) {
            try { trig = JSON.parse(cc.triggered[0].prop_id.replace(/\\.n_clicks$/, '')); } catch (e) {}
        }
        if (!trig || trig.value === undefined) { return [nu, nu]; }
        var idx = -1;
        for (var i = 0; i < ids.length; i++) { if (ids[i].value === trig.value) { idx = i; } }
        if (idx < 0 || !clicks[idx]) { return [nu, nu]; }
        var out = classes.map(function (c, i) {
            var base = (c || '').replace(/\\s*\\bis-active\\b/g, '');
            return ids[i].value === trig.value ? base + ' is-active' : base;
        });
        return [trig.value, out];
    }
    """,
    Output({"type": "ag-choice-value", "group": MATCH}, "data"),
    Output({"type": "ag-choice", "group": MATCH, "value": ALL}, "className"),
    Input({"type": "ag-choice", "group": MATCH, "value": ALL}, "n_clicks"),
    State({"type": "ag-choice", "group": MATCH, "value": ALL}, "id"),
    State({"type": "ag-choice", "group": MATCH, "value": ALL}, "className"),
    State({"type": "ag-choice-value", "group": MATCH}, "data"),
    prevent_initial_call=True,
)


# ═══════════════════════════════ SORTABLE ROW-CARD TABLE ═══════════════════

def ag_sort_id(table):
    return {"type": "ag-sort-state", "table": table}


def ag_sort_store(table, key=None, desc=False):
    """Holds ``{"key", "desc"}`` for a sortable :func:`ag_results_table`. Put it
    OUTSIDE the element you re-render, so the state survives a re-sort."""
    return dcc.Store(id=ag_sort_id(table), data={"key": key, "desc": bool(desc)})


def ag_sort_rows(rows, state):
    """Sort rows by ``state["key"]``; blanks always sink to the bottom."""
    if not state or not state.get("key"):
        return list(rows)
    k, desc = state["key"], bool(state.get("desc"))
    have = [r for r in rows if r.get(k) not in (None, "")]
    blank = [r for r in rows if r.get(k) in (None, "")]
    return sorted(have, key=lambda r: r[k], reverse=desc) + blank


clientside_callback(
    """
    function (clicks, ids, state) {
        var nu = window.dash_clientside.no_update;
        var cc = window.dash_clientside.callback_context;
        var trig = cc.triggered_id;
        if (!trig && cc.triggered && cc.triggered.length) {
            try { trig = JSON.parse(cc.triggered[0].prop_id.replace(/\\.n_clicks$/, '')); } catch (e) {}
        }
        if (!trig || trig.key === undefined) { return nu; }
        var idx = -1;
        for (var i = 0; i < ids.length; i++) { if (ids[i].key === trig.key) { idx = i; } }
        if (idx < 0 || !clicks[idx]) { return nu; }
        state = state || {};
        if (state.key === trig.key) { return {key: trig.key, desc: !state.desc}; }
        return {key: trig.key, desc: !!trig.d};
    }
    """,
    Output({"type": "ag-sort-state", "table": MATCH}, "data"),
    Input({"type": "ag-sort", "table": MATCH, "key": ALL, "d": ALL}, "n_clicks"),
    State({"type": "ag-sort", "table": MATCH, "key": ALL, "d": ALL}, "id"),
    State({"type": "ag-sort-state", "table": MATCH}, "data"),
    prevent_initial_call=True,
)


def _cell_style(col):
    st = {}
    if col.get("width"):
        st["flexBasis"] = col["width"]
        st["width"] = col["width"]
    return st


def _render_cell(col, row):
    kind = col.get("kind", "text")
    v = row.get(col["key"])
    if kind == "rank":
        return html.Span("" if v in (None, "") else v,
                         className=_cls("ag-rank", "ag-rank--muted" if col.get("muted") else ""))
    if kind == "athlete":
        name = ag_athlete_name(row.get("surname", ""), row.get("given"))
        inner = html.Span([ag_flag(row.get("noc")),
                           html.Span([html.Span(row.get("noc", ""), className="ag-noc__code"), name],
                                     className="ag-noc__stack")], className="ag-noc")
        return ag_athlete_link(row["athlete_id"], inner) if row.get("athlete_id") else inner
    if kind == "noc":
        return ag_noc(row.get("noc"), row.get("noc_name"))
    if kind == "mark":
        recs = [html.Span(r, className=_cls("ag-rec", "ag-rec--pb" if r in ("PB", "SB") else ""))
                for r in (row.get("records") or [])]
        return html.Span([html.Span(row.get("mark_display", v) or "", className="ag-mark"), *recs])
    if kind == "gap":
        return html.Span(v or "", className="ag-gap")
    if kind == "status":
        return ag_status_pill(v) if v else None
    if kind == "medal":
        return ag_medal_icon(v) if v in _MEDALS else None
    return html.Span("" if v is None else v, className="ag-num")


def ag_results_table(columns, rows, *, table_id=None, sort_state=None, focus_noc=None,
                     empty_text="No results available"):
    """Row-card results table, the results.asiangames2026.org way: every row is
    its own white card (13px radius, 0.5rem gap) and the header sits on the page.

    columns : list of dicts ``{"key", "label", "kind", "width", "align",
        "sortable", "desc_default", "hide_sm", "grow"}``. ``kind`` is one of
        rank, athlete, noc, mark, gap, status, medal, text.
    rows : list of dicts. ``medal`` ("gold"/"silver"/"bronze") colours the row's
        left edge; ``records`` (list like ``["GR", "PB"]``) adds chips to a mark.
    table_id : enables sortable headers (pair with :func:`ag_sort_store`).
    """
    sort_state = sort_state or {}
    head = []
    for c in columns:
        sortable = table_id is not None and c.get("sortable", False)
        is_sorted = sortable and sort_state.get("key") == c["key"]
        caret = None
        if sortable:
            caret = _icon("fa-sort" if not is_sorted else
                          ("fa-caret-down" if sort_state.get("desc") else "fa-caret-up"), "ag-th__caret")
        label = [c.get("label", ""), caret]
        if sortable:
            th = html.Button(label, id={"type": "ag-sort", "table": table_id, "key": c["key"],
                                        "d": bool(c.get("desc_default", False))},
                             n_clicks=0, type="button",
                             className=_cls("ag-th ag-th--sortable", "is-sorted" if is_sorted else ""))
        else:
            th = html.Span(label, className="ag-th")
        head.append(html.Div(th, className=_cell_cls(c), style=_cell_style(c)))

    body = []
    for r in rows:
        body.append(html.Div(
            [html.Div(_render_cell(c, r), className=_cell_cls(c), style=_cell_style(c)) for c in columns],
            className=_cls("ag-rrow",
                           f"ag-rrow--medal-{r['medal']}" if r.get("medal") in _MEDALS else "",
                           "ag-rrow--focus" if focus_noc and r.get("noc") == focus_noc else "")))
    if not body:
        body = [ag_empty(empty_text)]
    return html.Div([html.Div(head, className="ag-rrow ag-rrow--head"), *body], className="ag-rtable")


def _cell_cls(c):
    return _cls("ag-cell", "ag-cell--grow" if c.get("grow") or c.get("kind") in ("athlete", "noc") else "",
                f"ag-cell--{c['align']}" if c.get("align") else "",
                "ag-hide-sm" if c.get("hide_sm") else "")


def ag_filter_panel(children, *, label="Show filters", open=False, chips=None):
    """Collapsible filter panel behind a "Show filters" button (native
    ``<details>``, no callback). ``chips`` renders active-filter chips below."""
    return html.Details([
        html.Summary(html.Span([_icon("fa-sliders"), label], className="ag-btn ag-btn--ghost")),
        html.Div(children, className="ag-filters__panel"),
        html.Div(chips, className="ag-chipset") if chips else None,
    ], className="ag-filters", open=open)


def ag_field(label, control):
    return html.Div([html.Label(label, className="ag-field__label"), control])


def ag_records_panel(records, *, title="Latest records", open=True):
    """Collapsible panel of record cards: ``[{"type": "WR"|"AR"|"GR", "noc",
    "athlete", "mark", "date", "place"}]``."""
    cards = [html.Div([
        html.Span(r["type"], className=f"ag-record__type ag-record__type--{r['type']}"),
        ag_noc(r["noc"], r.get("athlete")),
        html.Div(r["mark"], className="ag-record__mark"),
        html.Div(" · ".join(x for x in (r.get("date"), r.get("place")) if x), className="ag-record__meta"),
    ], className="ag-record") for r in records]
    return html.Details([
        html.Summary([html.Span([_icon("fa-trophy"), " ", title]), _icon("fa-chevron-down", "ag-caret")]),
        html.Div(html.Div(cards, className="ag-records"), className="ag-collapse__body"),
    ], className="ag-collapse", open=open)


# ═══════════════════════════════ MEDALS + SCHEDULE ═════════════════════════

def _mcell(v, total=False):
    return html.Div(v, className=_cls("c", "t" if total else "", "z" if not v else ""))


def ag_medal_table(rows, *, focus_noc=None, open_noc=None):
    """Medal standings as expandable row cards (native ``<details>``). Each row:
    ``{"rank", "noc", "name", "gold", "silver", "bronze", "breakdown": [{"label",
    "icon", "gold", "silver", "bronze"}]}``. The caret rotates and the
    discipline breakdown slides in."""
    head = html.Div([
        html.Div("Rank"), html.Div("NOC"),
        html.Div(ag_medal_icon("gold"), className="c"), html.Div(ag_medal_icon("silver"), className="c"),
        html.Div(ag_medal_icon("bronze"), className="c"), html.Div(ag_medal_icon("total", "Total"), className="c"),
        html.Div(),
    ], className="ag-mgrid ag-mhead")
    out = [head]
    for i, r in enumerate(rows):
        total = r.get("total", r["gold"] + r["silver"] + r["bronze"])
        sub = []
        for b in r.get("breakdown") or []:
            bt = b["gold"] + b["silver"] + b["bronze"]
            sub.append(html.Div([
                html.Div(), html.Div([_icon(b.get("icon")), html.Span(b["label"])], className="ag-msub__disc"),
                _mcell(b["gold"]), _mcell(b["silver"]), _mcell(b["bronze"]), _mcell(bt, True), html.Div(),
            ], className="ag-mgrid"))
        out.append(html.Details([
            html.Summary(html.Div([
                html.Div(r["rank"], className="ag-rank ag-rank--muted"),
                ag_noc(r["noc"], r.get("name")),
                _mcell(r["gold"]), _mcell(r["silver"]), _mcell(r["bronze"]), _mcell(total, True),
                _icon("fa-chevron-down", "ag-caret"),
            ], className="ag-mgrid")),
            html.Div(sub or [html.Div("No breakdown", className="ag-muted")], className="ag-msub"),
        ], className=_cls("ag-mrow", "ag-mrow--focus" if r["noc"] == focus_noc else ""),
            open=r["noc"] == open_noc, style={"animationDelay": f"{min(i, 10) * 0.03:.2f}s"}))
    return html.Div(out, className="ag-mtable")


def ag_medal_widget(rows, *, title="Medal standings", limit=8, link=None):
    """Compact org-site medal widget: purple header bar, gold rank squares."""
    body = [html.Div([html.Div("#"), html.Div("NOC"), html.Div("G", className="c"),
                      html.Div("S", className="c"), html.Div("B", className="c"),
                      html.Div("Tot", className="c")], className="ag-mwidget__row ag-mwidget__row--head")]
    for r in rows[:limit]:
        body.append(html.Div([
            html.Div(r["rank"], className="ag-rankbox"),
            ag_noc(r["noc"], r.get("name"), size="sm"),
            html.Div(r["gold"], className="c"), html.Div(r["silver"], className="c"),
            html.Div(r["bronze"], className="c"),
            html.Div(r.get("total", r["gold"] + r["silver"] + r["bronze"]), className="c t"),
        ], className="ag-mwidget__row"))
    head_right = dcc.Link(["All ", _icon("fa-arrow-right")], href=_safe_relative(link),
                          style={"color": "#fff", "fontSize": "13px"}) if link else None
    return html.Div([html.Div([html.Span(title), head_right], className="ag-mwidget__head"), *body],
                    className="ag-mwidget")


def ag_schedule_unit(time, event, *, phase=None, unit=None, venue=None, status="scheduled",
                     icon=None, medal=False):
    """One schedule row: time, pictogram, event + phase, venue and status."""
    return html.Div([
        html.Div(time, className="ag-sunit__time"),
        html.Div(_icon(icon), className="ag-sunit__icon"),
        html.Div([
            html.Div([event, ag_medal_stack() if medal else None], className="ag-sunit__event"),
            html.Div([phase or "", html.Span(f" · {unit}") if unit else None], className="ag-sunit__phase"),
        ]),
        html.Div([html.Span(venue, className="ag-sunit__venue") if venue else None,
                  ag_status_pill(status)], className="ag-sunit__side"),
    ], className="ag-sunit")


def ag_discipline_card(name, icon, days, *, live=False):
    """By-discipline schedule card: gold pictogram, purple name, then that
    discipline's competition days (medal days in gold)."""
    boxes = []
    for d in days:
        dt = _dt.date.fromisoformat(d["value"])
        boxes.append(html.Div([
            html.Span(dt.strftime("%a"), className="ag-day__wd"),
            html.Span(str(dt.day), className="ag-day__d"),
            html.Span(dt.strftime("%b"), className="ag-day__m"),
        ], className=_cls("ag-day", "ag-day--medal" if d.get("medal") else "",
                          "ag-day--today" if d.get("today") else "")))
    return html.Div([
        ag_status_pill("live", "Live") if live else None,
        html.Div([_icon(icon), html.Span(name, className="ag-disccard__name")], className="ag-disccard__head"),
        html.Div(boxes, className="ag-days"),
    ], className="ag-disccard")


# ═══════════════════════════════ ATHLETES + CARDS ══════════════════════════

def ag_avatar(initials, size="lg"):
    return html.Div(initials, className=_cls("ag-avatar", "ag-avatar--sm" if size == "sm" else ""))


def _initials(a):
    return f"{(a.get('given') or ' ')[0]}{(a.get('surname') or ' ')[0]}".upper()


def ag_athlete_card(a):
    """Participant card; clicking it fires the ``ag-athlete`` pattern id."""
    medals = [ag_medal_icon(m) for m in (a.get("medals") or [])]
    return html.Button([
        ag_avatar(_initials(a), "sm"),
        html.Div([
            ag_athlete_name(a["surname"], a.get("given")),
            html.Div([ag_flag(a["noc"], "sm"), html.Span(a["noc"], className="ag-noc__code"),
                      html.Span(a.get("sport", ""), className="ag-sportchip"), *medals],
                     className="ag-acard__meta"),
        ], className="ag-acard__body"),
    ], id={"type": "ag-athlete", "id": str(a["id"])}, n_clicks=0, type="button", className="ag-acard")


def ag_athlete_profile(a):
    """Athlete profile body (for the modal or a page). ``a`` holds id, surname,
    given, noc, sport, gender, age, height, events ``[{"label", "rank",
    "medal"}]`` and schedule ``[{"date", "time", "event", "phase", "venue",
    "status"}]``."""
    stats = [(k, a.get(f)) for k, f in (("Gender", "gender"), ("Age", "age"),
                                         ("Height", "height"), ("Club", "club")) if a.get(f)]
    events = [html.Div([
        html.Span([ag_medal_icon(e["medal"]), " ", e["label"]] if e.get("medal") else e["label"]),
        html.Span(f"Rank {e['rank']}" if e.get("rank") else "Entered", className="ag-rankpill"),
    ], className="ag-evrow") for e in a.get("events") or []]
    sched = [html.Div([
        html.Div([html.Div(s["date"], className="ag-mini-unit__date"),
                  html.Div(s["time"], className="ag-mini-unit__time")]),
        html.Div([html.Div(s["event"], className="ag-mini-unit__ev"),
                  html.Div(s.get("phase", ""), className="ag-mini-unit__ph")]),
        html.Div([html.Div(s.get("venue", ""), className="ag-sunit__venue"),
                  ag_status_pill(s.get("status", "scheduled"))], className="ag-sunit__side"),
    ], className="ag-mini-unit") for s in a.get("schedule") or []]
    return html.Div([
        html.Div([
            ag_avatar(_initials(a)),
            html.Div([
                html.Div([html.B(a["surname"]), f" {a.get('given', '')}"], className="ag-profile__name"),
                html.Div(html.Span(a.get("sport", ""), className="ag-sportchip"), style={"margin": "8px 0"}),
                ag_noc(a["noc"]),
            ]),
        ], className="ag-profile__top"),
        html.Div([html.Div([html.Div(k, className="ag-profile__stat-l"),
                            html.Div(v, className="ag-profile__stat-v")]) for k, v in stats],
                 className="ag-profile__stats") if stats else None,
        html.Div([html.Div([_icon("fa-medal"), "Events & medals"], className="ag-profile__h"),
                  html.Div(events or [html.Div("No entries yet", className="ag-muted")],
                           style={"marginTop": "8px"})]),
        html.Div([html.Div([_icon("fa-regular fa-calendar"), "Schedule & results"], className="ag-profile__h"),
                  html.Div(sched or [html.Div("Nothing scheduled", className="ag-muted")],
                           style={"marginTop": "8px"})]),
    ], className="ag-profile")


def ag_sport_tile(label, icon, href=None):
    """Org-site sports tile: centred purple pictogram, grey label, soft hover."""
    inner = [_icon(icon), html.Span(label)]
    if href:
        return dcc.Link(inner, href=_safe_relative(href), className="ag-tile")
    return html.Div(inner, className="ag-tile")


def ag_news_card(title, text, *, date=None, tags=None, icon="fa-newspaper", tone=None, href=None):
    """News card: 16px radius, big soft shadow, image area (a branded gradient
    with an icon, since we ship no photos), lavender tag chips."""
    card = html.Div([
        html.Div(_icon(icon), className=_cls("ag-newscard__img", f"ag-newscard__img--{tone}" if tone else "")),
        html.Div(date, className="ag-newscard__date") if date else None,
        html.H3(title, className="ag-newscard__title"),
        html.P(text, className="ag-newscard__text"),
        html.Div([ag_chip(t, "purple") for t in tags or []], className="ag-chipset") if tags else None,
    ], className="ag-newscard")
    return dcc.Link(card, href=_safe_relative(href)) if href else card


def ag_feature_banner(title, text, *, icon="fa-medal", button=None):
    """Two-column feature banner: art panel left, patterned orange panel right."""
    return html.Div([
        html.Div(_icon(icon), className="ag-banner__art"),
        html.Div([html.H3(title, className="ag-banner__title"),
                  html.P(text, className="ag-banner__text"),
                  html.Div(button) if button else None], className="ag-banner__body"),
    ], className="ag-banner")


def ag_stat(label, value, sub=None, *, gold=False):
    return html.Div([html.Div(label, className="ag-stat__label"),
                     html.Div(value, className="ag-stat__value"),
                     html.Div(sub, className="ag-stat__sub") if sub else None],
                    className=_cls("ag-stat", "ag-stat--gold" if gold else ""))
