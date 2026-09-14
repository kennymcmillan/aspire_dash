"""Athlete-specific widgets — avatar, profile header, picker shell.

Lifted from aspire-nutrition's picker_widget(), medical-dashboard's
_initials helper, SAMS_register's profile chips, and the attendance /
endurance / whoop apps' photo-with-fallback pattern.

The picker_widget() helper provides the **layout** (trigger button →
offcanvas → tabs → roster list → search). Wiring to SAMS / Oracle / any
specific athlete source is up to the caller — they pass roster-loader
and search-loader functions into ``register_athlete_picker``.
"""
from __future__ import annotations

from typing import Callable, Iterable

import dash
from dash import (ALL, Input, Output, State, callback_context, dcc, html, no_update)
import dash_bootstrap_components as dbc

from .theme import ASPIRE, SLATE, GOLD, ASPIRE_NAVY, RADIUS_LG, SHADOW_SM, BG_PAGE


# ── Avatar ─────────────────────────────────────────────────────────────────

def _initials(name: str | None) -> str:
    """Two-letter initials from a full name. Returns '?' for empty."""
    parts = [p for p in (name or "").strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


# v0.29 — re-export athlete_card_v2 from v12_helpers under aspire_dash.athlete
# so it lives where callers expect ("athlete things go in athlete module").
from .v12_helpers import athlete_card_v2, athlete_card_compact     # noqa: F401  (public re-exports)


def athlete_avatar(
    photo_url: str | None = None,
    name: str | None = None,
    size: str | int = "md",
    is_target: bool = False,
    border_color: str | None = None,
):
    """SAMS photo or initials-circle fallback.

    Canonical pattern across nutrition, medical, attendance, endurance,
    whoop — pass the SAMS ``imageUrl`` directly, browser fetches from the
    azfpictures public blob (do **not** build a Flask proxy route).

    Parameters
    ----------
    photo_url : str or None
        Public image URL (e.g. SAMS azfpictures blob). If None / empty,
        renders initials in an Aspire-blue circle.
    name : str or None
        Athlete name — used for initials fallback and the ``alt`` text.
    size : "sm" | "md" | "lg" | int
        Diameter in px. Presets: sm=32, md=44, lg=64.
    is_target : bool
        If True, the avatar wears a gold ring (Aspire pathway indicator).
    border_color : str or None
        Override border hex. Defaults to gold if ``is_target`` else slate-200.

    Example::

        athlete_avatar(profile.get("imageUrl"), profile["full_name"], size="md")
    """
    size_map = {"sm": 32, "md": 44, "lg": 64}
    px = size_map.get(size, size) if not isinstance(size, int) else size
    font_size = max(11, int(px * 0.35))
    border = border_color or (GOLD if is_target else SLATE["200"])

    common_style = {
        "width": f"{px}px",
        "height": f"{px}px",
        "borderRadius": "50%",
        "border": f"2px solid {border}",
        "flexShrink": "0",
        "display": "inline-flex",
        "alignItems": "center",
        "justifyContent": "center",
        "overflow": "hidden",
    }

    if photo_url:
        from .v12_helpers import lazy_img
        return lazy_img(
            photo_url,
            alt=name or "athlete",
            className="athlete-avatar" + (" is-target" if is_target else ""),
            style={**common_style, "objectFit": "cover"},
        )

    return html.Div(
        _initials(name),
        className="athlete-avatar" + (" is-target" if is_target else ""),
        style={
            **common_style,
            "background": ASPIRE["600"],
            "color": "white",
            "fontWeight": "700",
            "fontSize": f"{font_size}px",
            "fontVariantNumeric": "tabular-nums",
        },
    )


# ── Profile Header ─────────────────────────────────────────────────────────

def athlete_profile_header(
    name: str,
    photo_url: str | None = None,
    sport: str | None = None,
    subtitle: str | None = None,
    badges: list | None = None,
    is_target: bool = False,
    right_content=None,
):
    """Profile hero strip — avatar + name + sport/subtitle + badges.

    Used in /athlete pages across medical, nutrition, endurance, attendance.
    Pass ``badges`` for arbitrary right-of-name pills (status / availability /
    membership). ``right_content`` lands on the far right (action buttons,
    last-updated stamp).
    """
    badges = badges or []
    return html.Div([
        athlete_avatar(photo_url, name, size="lg", is_target=is_target),
        html.Div([
            html.Div([
                html.Span(name, style={
                    "fontSize": "22px", "fontWeight": "700",
                    "color": ASPIRE_NAVY, "marginRight": "12px",
                }),
                *badges,
            ], style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "6px"}),
            html.Div(
                " · ".join(filter(None, [sport, subtitle])) or "",
                style={"fontSize": "13px", "color": SLATE["500"], "marginTop": "2px"},
            ),
        ], style={"flex": "1", "marginLeft": "16px", "minWidth": "0"}),
        html.Div(right_content) if right_content else None,
    ], style={
        "display": "flex", "alignItems": "center",
        "padding": "16px 20px",
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": f"{RADIUS_LG}px",
        "boxShadow": SHADOW_SM,
        "marginBottom": "16px",
    })


# ── Athlete Identity Card — v0.37 (promoted from DASH_Anthro) ─────────────
#
# "Did I pick the right person?" — sits at the top of any capture /
# single-athlete page after a picker selection. Shows photo + name +
# optional TARGET badge + 2 rows of pills (sport/event categorical,
# dob/mrn/sams identity) + decimal age. Gold accent + ring for Target-
# pathway athletes.
#
# Pure data → component (no callbacks). Consumes any picker-store dict
# with the standard keys; everything is gated on truthiness so partial
# data renders without empty pills.
#
# Styling lives in 00_aspire_base.css under .athlete-id-card — keep
# this helper free of inline styles so the brand can evolve via CSS
# without code changes.

from datetime import date as _date


def _athlete_id_card_fractional_age(dob_iso: str | None) -> float | None:
    """Decimal years between dob and today (e.g. 16.1). Returns None if
    dob is missing or unparseable. Display-only — Oracle / SAMS keep the
    integer age. Helper isolated so consumers can override without a
    full re-render."""
    if not dob_iso:
        return None
    try:
        dob = _date.fromisoformat(str(dob_iso)[:10])
    except (TypeError, ValueError):
        return None
    return round((_date.today() - dob).days / 365.25, 1)


def athlete_id_card(data: dict | None) -> html.Div:
    """Picker-confirmation identity card (v0.39 "C-style" redesign).

    Photo with corner-star badge for target athletes, Aspire-navy name,
    one combined Sport · Event pill, and a single identity line with
    DOB, SAMS ID, and decimal age. No MRN, no inline "TARGET" text —
    target status is conveyed visually by the gold ring + corner star +
    warm gradient background.

    Parameters
    ----------
    data : dict | None
        Picker-store payload. Recognised keys (all optional except
        ``player_id`` which gates the empty-state):

        ============     ===========================================
        ``player_id``    SAMS player ID (gates empty state, shown
                         as SAMS in the identity line)
        ``full_name``    Display name
        ``photo_url``    Photo URL (FA user icon falls back if missing)
        ``sport``        e.g. "Athletics"
        ``target_event`` e.g. "100m" (combined with sport in one pill)
        ``date_of_birth`` ISO date — drives DOB + decimal age
        ``is_target``    bool — gold ring + corner star
        ``pathway``      "Target" also triggers target styling
        ============     ===========================================

        ``mrn`` is no longer rendered (SAMS player_id is the durable
        identifier). The data may still contain it; it's ignored.

    Returns
    -------
    html.Div
        Ready-to-render component. Empty/None payload returns the
        amber "no athlete picked" prompt.
    """
    if not data or not data.get("player_id"):
        return html.Div(
            [html.I(className="fa-solid fa-user-plus me-2"),
             "No athlete picked. Use the picker (top-right) to choose a "
             "sport, then an athlete."],
            className="athlete-id-card is-empty",
        )

    name      = data.get("full_name") or "?"
    photo     = data.get("photo_url")
    sport     = data.get("sport")
    target    = data.get("target_event")
    dob       = data.get("date_of_birth")
    sams_id   = data.get("player_id")
    is_target = bool(data.get("is_target")) or (data.get("pathway") == "Target")
    frac_age  = _athlete_id_card_fractional_age(dob)

    # Photo (or FA user fallback) — ring colour flips via .is-target.
    # Target athletes get a corner-star badge overlay.
    photo_node = (
        html.Img(src=photo, alt=name, className="athlete-id-card__photo")
        if photo
        else html.Div(html.I(className="fa-solid fa-user"),
                      className="athlete-id-card__photo-fallback")
    )
    photo_wrap_children = [photo_node]
    if is_target:
        photo_wrap_children.append(html.Div(
            html.I(className="fa-solid fa-star"),
            className="athlete-id-card__target-star",
            title="Target pathway athlete",
        ))
    photo_wrap = html.Div(photo_wrap_children,
                          className="athlete-id-card__photo-wrap")

    # Name row — Aspire-navy name + optional combined Sport · Event pill
    name_row: list = [html.Span(name, className="athlete-id-card__name")]
    sport_event_parts = [p for p in (sport, target) if p]
    if sport_event_parts:
        name_row.append(html.Span(
            " · ".join(sport_event_parts),
            className="athlete-id-card__sport-pill",
        ))

    # Identity line — slate text with label spans + age in emerald
    identity_bits: list = []

    def _sep():
        return html.Span("·", className="athlete-id-card__identity-sep")

    if dob:
        identity_bits.append(html.Span([
            html.Span("DOB", className="athlete-id-card__identity-label"),
            str(dob),
        ]))
    if sams_id:
        if identity_bits:
            identity_bits.append(_sep())
        identity_bits.append(html.Span([
            html.Span("SAMS", className="athlete-id-card__identity-label"),
            str(sams_id),
        ]))
    if frac_age is not None:
        if identity_bits:
            identity_bits.append(_sep())
        identity_bits.append(html.Span(
            f"{frac_age:.1f} yrs",
            className="athlete-id-card__identity-age",
            title=f"Age computed from DOB ({dob})" if dob else None,
        ))

    body_children = [html.Div(name_row, className="athlete-id-card__name-row")]
    if identity_bits:
        body_children.append(html.Div(identity_bits,
                                      className="athlete-id-card__identity"))

    return html.Div(
        [photo_wrap,
         html.Div(body_children, className="athlete-id-card__body")],
        className=f"athlete-id-card{' is-target' if is_target else ''}",
    )


# ── Picker Widget ──────────────────────────────────────────────────────────

#: Component IDs used by athlete_picker / register_athlete_picker. Exposed
#: so callers can wire their own State("athlete-picker-store", "data")
#: inputs into downstream callbacks.
PICKER_STORE_ID         = "athlete-picker-store"
PICKER_WRAP_ID          = "athlete-picker-wrap"
PICKER_TRIGGER_ID       = "athlete-picker-trigger"
PICKER_OFFCANVAS_ID     = "athlete-picker-offcanvas"
PICKER_DISPLAY_ID       = "athlete-picker-display"
PICKER_SPORT_DD_ID      = "athlete-picker-sport"
PICKER_ROSTER_ID        = "athlete-picker-roster"
PICKER_ROSTER_FILTER_ID = "athlete-picker-roster-filter"
PICKER_ROSTER_COUNT_ID  = "athlete-picker-roster-count"
PICKER_ROSTER_DATA_ID   = "athlete-picker-roster-data"
PICKER_SEARCH_INPUT_ID  = "athlete-picker-search-input"
PICKER_SEARCH_RESULTS_ID = "athlete-picker-search-results"


def _picker_trigger_button():
    """Aspire-navy primary button with a gold 'pick required' dot."""
    return dbc.Button(
        [
            html.Span(style={
                "display": "inline-block", "width": "8px", "height": "8px",
                "borderRadius": "50%", "backgroundColor": GOLD,
                "marginRight": "10px",
            }),
            html.I(className="fa-solid fa-user-plus me-2",
                   style={"color": GOLD}),
            "Select athlete",
        ],
        id=PICKER_TRIGGER_ID, n_clicks=0,
        className="picker-trigger-btn",
        style={
            "backgroundColor": ASPIRE_NAVY,
            "color": "#ffffff",
            "border": "none",
            "padding": "8px 16px",   # v0.24: on 4/8 scale (was 9/18)
            "fontSize": "0.92rem",
            "fontWeight": "600",
            "borderRadius": "8px",
            "letterSpacing": "0.2px",
            "minWidth": "200px",
            "boxShadow": "0 2px 6px rgba(0,29,61,0.18)",
        },
    )


def _picker_selected_chip(athlete: dict):
    """280px chip — avatar | identity | actions. Gold ring when on Target pathway."""
    name = athlete.get("full_name") or athlete.get("name") or "—"
    sport = athlete.get("sport") or "—"
    age = athlete.get("age")
    photo = athlete.get("photo_url") or athlete.get("imageUrl")
    is_target = bool(athlete.get("is_target"))

    sub_bits = [html.Span(str(sport).upper(), style={
        "fontSize": "0.7rem", "letterSpacing": "0.5px",
        "color": SLATE["500"], "fontWeight": "600",
    })]
    if age:
        sub_bits.append(html.Span(f"  ·  age {age}", style={
            "fontSize": "0.7rem", "color": SLATE["500"],
        }))
    if is_target:
        sub_bits.append(html.Span("TARGET", style={
            "backgroundColor": GOLD, "color": ASPIRE_NAVY,
            "padding": "2px 6px", "borderRadius": "4px",   # v0.24: on-scale
            "fontSize": "0.65rem", "fontWeight": "700",
            "marginLeft": "6px", "letterSpacing": "0.4px",
        }))

    return html.Div([
        athlete_avatar(photo, name, size="md", is_target=is_target),
        html.Div([
            html.Div(name, style={
                "fontSize": "0.92rem", "fontWeight": "600",
                "color": ASPIRE_NAVY, "whiteSpace": "nowrap",
                "overflow": "hidden", "textOverflow": "ellipsis",
                "maxWidth": "170px",
            }, title=name),
            html.Div(sub_bits, className="d-flex align-items-center"),
        ], style={"minWidth": 0}),
        html.Div([
            dbc.Button("Change", id=PICKER_TRIGGER_ID, color="link", size="sm",
                       n_clicks=0,
                       className="p-0 text-decoration-none",
                       style={"color": ASPIRE["600"], "fontSize": "0.78rem",
                              "fontWeight": "500"}),
            dbc.Button(html.I(className="fa-solid fa-xmark"),
                       id={"type": "athlete-clear", "k": 0}, color="link",
                       size="sm", n_clicks=0,
                       className="p-0 text-secondary mt-1",
                       title="Clear selection",
                       style={"fontSize": "0.85rem", "lineHeight": 1}),
        ], style={"display": "flex", "flexDirection": "column",
                  "alignItems": "flex-end"}),
    ], style={
        "width": "280px", "padding": "8px 12px",
        "border": f"1px solid {SLATE['200']}", "borderRadius": "8px",   # v0.24: canonical
        "backgroundColor": BG_PAGE,                                      # v0.24: theme token
        "display": "grid",
        "gridTemplateColumns": "44px 1fr auto",
        "gap": "10px", "alignItems": "center",
    })


def _athlete_row_button(hit: dict):
    """One row in the roster / search-results list — click to pick."""
    photo = hit.get("photo_url") or hit.get("imageUrl")
    name = hit.get("full_name") or hit.get("name") or "(unnamed)"
    sub_bits = []
    if hit.get("mrn"):
        sub_bits.append(f"MRN {hit['mrn']}")
    if hit.get("sport") and not hit.get("_hide_sport"):
        sub_bits.append(str(hit["sport"]))
    pid = hit.get("player_id") or hit.get("athlete_id") or hit.get("id")
    return dbc.Button(
        html.Div([
            athlete_avatar(photo, name, size="sm"),
            html.Div([
                html.Div(name, className="fw-semibold"),
                html.Div(" · ".join(sub_bits) if sub_bits else "",
                         className="text-muted small"),
            ], style={"flex": "1", "marginLeft": "12px", "textAlign": "left"}),
        ], style={"display": "flex", "alignItems": "center"}),
        id={"type": "athlete-pick", "pid": int(pid) if pid else 0},
        color="light", className="w-100 mb-1 text-start athlete-row-btn",
        style={"borderRadius": 0, "border": "none"},
        n_clicks=0,
    )


def athlete_picker(
    sports: list[dict] | dict | None = None,
    placement: str = "end",
    width: str = "440px",
    initial_open: bool = False,
    cascade_label: str = "By sport / group",
    search_label: str = "By name",
):
    """Athlete picker widget — trigger button + offcanvas with two tabs.

    Drop the returned ``html.Div`` into your header's ``right_content``
    (or anywhere else). Selected athlete is stored in
    ``dcc.Store(id="athlete-picker-store", storage_type="session")`` —
    read it from downstream pages via
    ``Input("athlete-picker-store", "data")``.

    Wire the data callbacks via ``register_athlete_picker(app, ...)``.

    Parameters
    ----------
    sports : list[dict] | dict | None
        Sport dropdown options. Either:
          - list of ``{"label": str, "value": int|str}`` dicts, or
          - ``{sport_id: sport_name}`` dict (will be converted).
        ``None`` leaves the dropdown empty — populate via a callback
        targeting ``Output(PICKER_SPORT_DD_ID, "options")``.
    placement : str
        Offcanvas placement (``"end"`` or ``"start"``).
    width : str
        Offcanvas width.
    initial_open : bool
        For testing — open on first render.
    """
    if isinstance(sports, dict):
        sport_options = [{"label": v, "value": k} for k, v in sports.items()]
    else:
        sport_options = list(sports or [])

    cascade_view = [
        dbc.Label("Sport", className="text-muted small mb-1"),
        dcc.Dropdown(id=PICKER_SPORT_DD_ID, options=sport_options,
                     placeholder="Choose sport...", clearable=False,
                     className="mb-3"),
        dbc.Label("Filter (optional)", className="text-muted small mb-1"),
        dbc.Input(id=PICKER_ROSTER_FILTER_ID,
                  placeholder="Type to filter the roster (e.g. surname, MRN)...",
                  debounce=False, className="mb-3"),
        html.Hr(),
        html.Div([
            html.I(className="fa-solid fa-people-group me-2 text-muted"),
            html.Strong("Athletes", className="text-muted small text-uppercase"),
            html.Span(id=PICKER_ROSTER_COUNT_ID, className="text-muted small ms-2"),
        ], className="mb-2 d-flex align-items-center"),
        dcc.Store(id=PICKER_ROSTER_DATA_ID, storage_type="memory"),
        dbc.Spinner(html.Div(id=PICKER_ROSTER_ID), color="primary", size="sm"),
    ]
    search_view = [
        dbc.Label("Type a name (2+ chars)", className="text-muted small mb-1"),
        dbc.Input(id=PICKER_SEARCH_INPUT_ID, placeholder="e.g. Sulaiti", debounce=True),
        html.Hr(),
        dbc.Spinner(html.Div(id=PICKER_SEARCH_RESULTS_ID), color="primary", size="sm"),
    ]
    offcanvas = dbc.Offcanvas(
        id=PICKER_OFFCANVAS_ID,
        title=html.Div([
            html.I(className="fa-solid fa-user-magnifying-glass me-2"),
            html.Strong("Pick an athlete"),
        ]),
        placement=placement, is_open=initial_open,
        scrollable=True, backdrop=True, style={"width": width},
        children=[dbc.Tabs([
            dbc.Tab(label=cascade_label, tab_id="tab-cascade",
                    children=html.Div(cascade_view, className="pt-3")),
            dbc.Tab(label=search_label, tab_id="tab-search",
                    children=html.Div(search_view, className="pt-3")),
        ], id="athlete-picker-tabs", active_tab="tab-cascade")],
    )
    return html.Div([
        dcc.Store(id=PICKER_STORE_ID, storage_type="session"),
        html.Div(id=PICKER_DISPLAY_ID, children=_picker_trigger_button()),
        offcanvas,
    ], id=PICKER_WRAP_ID, style={"minWidth": "280px"})


def register_athlete_picker(
    app: dash.Dash,
    *,
    load_roster: Callable[[int | str], Iterable[dict]],
    search_athletes: Callable[[str], Iterable[dict]],
    resolve_athlete: Callable[[int], dict] | None = None,
    hidden_paths: Iterable[str] = (),
):
    """Wire all picker callbacks once after the Dash() instance is created.

    Parameters
    ----------
    app : Dash
    load_roster : (sport_id) -> iterable[dict]
        Function returning the full athlete roster for a sport. Each dict
        should include ``full_name`` (or ``name``), ``player_id`` (or
        ``athlete_id``), optionally ``mrn``, ``photo_url`` / ``imageUrl``.
    search_athletes : (query: str) -> iterable[dict]
        Free-text athlete search (used by the "By name" tab).
    resolve_athlete : (player_id) -> dict, optional
        Optional resolver to enrich the selection with sport, age, photo,
        is_target. If omitted, the row dict is stored directly.
    hidden_paths : iterable of str
        Pathnames where the picker should be hidden (e.g. ``("/", "/foods")``).
    """
    HIDDEN = set(hidden_paths)

    if HIDDEN:
        @app.callback(
            Output(PICKER_WRAP_ID, "style"),
            Input("url", "pathname"),
        )
        def _picker_visibility(pathname):
            relative = str(dash.strip_relative_path(pathname or "/")) or ""
            normalised = "/" + relative.lstrip("/").rstrip("/") if relative else "/"
            if relative == "":
                normalised = "/"
            base = {"minWidth": "280px"}
            if normalised in HIDDEN:
                base["display"] = "none"
            return base

    @app.callback(
        Output(PICKER_OFFCANVAS_ID, "is_open"),
        Input(PICKER_TRIGGER_ID, "n_clicks"),
        State(PICKER_OFFCANVAS_ID, "is_open"),
        prevent_initial_call=True,
    )
    def _toggle(n, is_open):
        if not n:
            return no_update
        return not bool(is_open)

    @app.callback(
        Output(PICKER_ROSTER_DATA_ID, "data"),
        Input(PICKER_SPORT_DD_ID, "value"),
        prevent_initial_call=True,
    )
    def _load_sport_roster(sport_id):
        if not sport_id:
            return []
        try:
            return list(load_roster(sport_id)) or []
        except Exception as e:
            return [{"_error": str(e)}]

    @app.callback(
        Output(PICKER_ROSTER_ID, "children"),
        Output(PICKER_ROSTER_COUNT_ID, "children"),
        Input(PICKER_ROSTER_DATA_ID, "data"),
        Input(PICKER_ROSTER_FILTER_ID, "value"),
        State(PICKER_SPORT_DD_ID, "value"),
        prevent_initial_call=True,
    )
    def _render_sport_roster(roster, filter_text, sport_id):
        if not sport_id:
            return (html.Em("Pick a sport above to see its athletes.",
                            className="text-muted small"), "")
        if not roster:
            return (html.Em("Loading roster...",
                            className="text-muted small"), "")
        if roster and isinstance(roster[0], dict) and roster[0].get("_error"):
            return (dbc.Alert(roster[0]["_error"], color="danger",
                              className="small"), "")
        q = (filter_text or "").strip().lower()
        if q:
            shown = [
                a for a in roster
                if q in (a.get("full_name") or a.get("name") or "").lower()
                or q in str(a.get("mrn") or "").lower()
            ]
        else:
            shown = roster
        if not shown:
            return (html.Em(f"No athletes match {filter_text!r}.",
                            className="text-muted small"),
                    f"({len(roster)} total)")
        rows = [_athlete_row_button(a) for a in shown]
        count = (f"({len(shown)} of {len(roster)})" if q
                 else f"({len(shown)} on roster)")
        return rows, count

    @app.callback(
        Output(PICKER_SEARCH_RESULTS_ID, "children"),
        Input(PICKER_SEARCH_INPUT_ID, "value"),
        prevent_initial_call=True,
    )
    def _search(q):
        if not q or len(q.strip()) < 2:
            return html.Em("Type 2+ characters...", className="text-muted small")
        try:
            hits = list(search_athletes(q.strip())) or []
        except Exception as e:
            return dbc.Alert(str(e), color="danger", className="small")
        if not hits:
            return html.Em(f'No matches for "{q}".', className="text-muted small")
        return [_athlete_row_button(h) for h in hits]

    @app.callback(
        Output(PICKER_STORE_ID, "data"),
        Output(PICKER_DISPLAY_ID, "children"),
        Output(PICKER_OFFCANVAS_ID, "is_open", allow_duplicate=True),
        Input({"type": "athlete-pick", "pid": dash.ALL}, "n_clicks"),
        Input({"type": "athlete-clear", "k": dash.ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def _pick_or_clear(pick_clicks, clear_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update
        triggered = ctx.triggered_id
        if not isinstance(triggered, dict):
            return no_update, no_update, no_update

        if triggered.get("type") == "athlete-clear":
            if not any(clear_clicks or []):
                return no_update, no_update, no_update
            return None, _picker_trigger_button(), no_update

        if triggered.get("type") == "athlete-pick":
            if not any(pick_clicks or []):
                return no_update, no_update, no_update
            pid = int(triggered["pid"])
            try:
                athlete = resolve_athlete(pid) if resolve_athlete else {"player_id": pid}
            except Exception:
                return no_update, no_update, no_update
            if not athlete:
                return no_update, no_update, no_update
            return athlete, _picker_selected_chip(athlete), False

        return no_update, no_update, no_update


# ── Fly-out picker shell — v0.79 ─────────────────────────────────────────────
#
# A lean "trigger button + slide-in Offcanvas" pop-out the CALLER fills with its
# OWN controls (a group filter, a clickable athlete list, ...). It reclaims canvas
# space by moving the athlete chooser off the page into a fly-out.
#
# Distinct from athlete_picker(): that is a full SAMS sport-cascade + name-search
# picker that OWNS its data wiring. This is a bring-your-own-content shell for
# apps that already have their own roster/list callbacks and just want the
# fly-out mechanics (open on a trigger, close when an item is picked). Promoted
# from development_dashboard's "Choose athlete" pop-out (Kenny 2026-09-14).
#
# Pure builders + one register helper. Ids are derived from a `prefix` so an app
# can mount more than one:
#   flyout_open_id(prefix)   -> "{prefix}-flyout-open"    (the trigger button)
#   flyout_canvas_id(prefix) -> "{prefix}-flyout-canvas"  (the Offcanvas)


def flyout_open_id(prefix: str) -> str:
    """Id of the trigger button for a fly-out with this prefix."""
    return f"{prefix}-flyout-open"


def flyout_canvas_id(prefix: str) -> str:
    """Id of the Offcanvas for a fly-out with this prefix."""
    return f"{prefix}-flyout-canvas"


def flyout_trigger(prefix: str, *, label: str = "Choose athlete",
                   icon: str | None = "fa-solid fa-user-group",
                   color: str = "primary", outline: bool = True,
                   size: str | None = "sm", **button_kwargs):
    """The button that opens the fly-out. Drop it wherever the trigger belongs
    (a top bar, a filter row). Extra dbc.Button kwargs pass through."""
    kids: list = []
    if icon:
        kids.append(html.I(className=icon, style={"marginRight": "6px"}))
    kids.append(label)
    style = {"whiteSpace": "nowrap", **button_kwargs.pop("style", {})}
    return dbc.Button(kids, id=flyout_open_id(prefix), n_clicks=0, color=color,
                      outline=outline, size=size, style=style, **button_kwargs)


def flyout_canvas(prefix: str, children, *, title: str = "Select athlete",
                  placement: str = "start", scrollable: bool = True,
                  **offcanvas_kwargs):
    """The slide-in Offcanvas holding the caller's own controls. Mount it in the
    page body; it starts closed and is toggled by :func:`register_flyout`."""
    return dbc.Offcanvas(children, id=flyout_canvas_id(prefix), title=title,
                         placement=placement, is_open=False, scrollable=scrollable,
                         **offcanvas_kwargs)


def register_flyout(app, prefix: str, *, item_type: str | None = None) -> None:
    """Wire the fly-out's open/close once after ``Dash()`` is created.

    Opens on the trigger button; closes when a pickable item inside the canvas is
    clicked. ``item_type`` is the ``type`` of the pattern-matching id on those
    items (``{"type": item_type, "index": ...}``); it defaults to
    ``f"{prefix}-item"``. Pass ``item_type=""`` (falsy) to skip close-on-pick and
    only wire the toggle.

    The trigger commonly re-mounts (e.g. it lives in a page-scoped top bar), which
    fires a spurious 0-click; that is guarded, so the fly-out never auto-opens on
    mount. Group changes / list rebuilds fire all-zero item clicks; those are
    ignored too, so only a real pick closes it.
    """
    if item_type is None:
        item_type = f"{prefix}-item"
    open_id, canvas_id = flyout_open_id(prefix), flyout_canvas_id(prefix)

    if item_type:
        @app.callback(
            Output(canvas_id, "is_open"),
            Input(open_id, "n_clicks"),
            Input({"type": item_type, "index": ALL}, "n_clicks"),
            State(canvas_id, "is_open"),
            prevent_initial_call=True)
        def _toggle(open_clicks, item_clicks, is_open):
            trig = callback_context.triggered_id
            if trig == open_id:
                if not open_clicks:      # spurious 0-click on (re)mount
                    return no_update
                return not is_open
            if (isinstance(trig, dict) and trig.get("type") == item_type
                    and item_clicks and any(c for c in item_clicks if c)):
                return False             # a real pick closes the fly-out
            return no_update
    else:
        @app.callback(
            Output(canvas_id, "is_open"),
            Input(open_id, "n_clicks"),
            State(canvas_id, "is_open"),
            prevent_initial_call=True)
        def _toggle_only(open_clicks, is_open):
            if not open_clicks:
                return no_update
            return not is_open


# ── Last-test-date dropdown options (sort by recent) ───────────────────────

def athlete_options_with_recency(
    profiles: list[dict],
    last_test_dates: dict[str, str | None] | None = None,
    *,
    id_field: str = "profileId",
    name_field: str = "fullName",
    label_date_fmt: str = "%d %b",
) -> list[dict]:
    """Build dropdown options sorted by most-recent test, with the date
    appended to the label.

    Example output::

        [
            {"label": "Aleix Paris (15 Nov)", "value": "abc-123"},
            {"label": "Mohamed Noufal (12 Oct)", "value": "def-456"},
            {"label": "Bob Stale", "value": "ghi-789"},  # no recent date
        ]

    Args:
        profiles:        list of athlete dicts (anything with ``id_field``
                          and ``name_field``).
        last_test_dates: mapping ``profileId → ISO date "YYYY-MM-DD"``.
                          Athletes missing from the map (or with ``None``)
                          fall to the bottom alphabetically.
        id_field:        which dict key holds the unique id (default
                          ``profileId`` — VALD shape). Override for SAMS
                          (``playerId``), Whoop (``user_id``), etc.
        name_field:      which dict key holds the display name.
        label_date_fmt:  strftime format for the date suffix
                          (default "%d %b" → "15 Nov").

    Caller owns the cache for ``last_test_dates`` — see DASH_VALD's
    ``helpers._fetch_last_test_date_snapshot`` for a 30-min TTL pattern.
    """
    from datetime import datetime as _dt

    last = last_test_dates or {}

    def _sort_key(p):
        d = last.get(p.get(id_field))
        if d:
            try:
                # Negative ordinal → ascending sort yields recent-first
                return (0, -_dt.strptime(d, "%Y-%m-%d").toordinal(),
                          p.get(name_field, ""))
            except ValueError:
                pass
        return (1, 0, p.get(name_field, ""))

    def _fmt(iso: str) -> str:
        try:
            return _dt.strptime(iso, "%Y-%m-%d").strftime(label_date_fmt)
        except Exception:
            return iso

    out: list[dict] = []
    for p in sorted(profiles, key=_sort_key):
        name = p.get(name_field, "?")
        d = last.get(p.get(id_field))
        label = f"{name} ({_fmt(d)})" if d else name
        out.append({"label": label, "value": p.get(id_field)})
    return out


# ── Selected athlete banner — v0.37 ───────────────────────────────────────
#
# A persistent page-top banner that re-renders the picked athlete OUTSIDE
# any step-card collapse, so picking an athlete (and the picker step
# auto-collapsing) still leaves the athlete card visible. The banner is
# an empty div that the registered callback fills from the chosen store.
#
# Promoted from aspire-nutrition's athlete_picker.selected_athlete_banner
# + _render_athlete_banner + _selected_chip (with missing-MRN warning).

# ── Thin identity banner (pure render) ──────────────────────────────────────
# IOC 3-letter nationality code -> ISO 3166-1 alpha-2, so a code becomes a flag
# emoji (regional-indicator pair). Covers Aspire's squads + common athletics
# nations; an unmapped code just shows without a flag.
# Nationality 3-letter code -> ISO 3166-1 alpha-2 (drives the flag emoji / image).
# Covers BOTH the IOC codes (KSA, IRI, NGR, PLE, SUD...) and the ISO 3166-1 alpha-3
# codes SAMS actually emits (SAU, IRN, NGA, PSE, SDN...), because Aspire's athlete
# feed is ISO3 while world-athletics data is IOC — an app should not have to know
# which it holds. An unmapped code just shows without a flag.
_IOC_ISO2 = {
    # ── IOC codes ──
    "QAT": "QA", "KSA": "SA", "UAE": "AE", "BRN": "BH", "KUW": "KW", "OMA": "OM",
    "IRQ": "IQ", "JOR": "JO", "SYR": "SY", "LBN": "LB", "YEM": "YE", "PLE": "PS",
    "MAR": "MA", "ALG": "DZ", "TUN": "TN", "LBA": "LY", "EGY": "EG", "SUD": "SD",
    "DJI": "DJ", "SOM": "SO", "ERI": "ER", "ETH": "ET", "KEN": "KE", "UGA": "UG",
    "NGR": "NG", "GHA": "GH", "SEN": "SN", "CIV": "CI", "CMR": "CM", "RSA": "ZA",
    "FRA": "FR", "GBR": "GB", "ESP": "ES", "ITA": "IT", "GER": "DE", "USA": "US",
    "IND": "IN", "PAK": "PK", "BAN": "BD", "SRI": "LK", "IRI": "IR", "TUR": "TR",
    "AUS": "AU", "CAN": "CA", "BRA": "BR", "JPN": "JP", "CHN": "CN", "KOR": "KR",
    # ── ISO 3166-1 alpha-3 aliases (SAMS) where they differ from the IOC code ──
    "SAU": "SA", "ARE": "AE", "BHR": "BH", "KWT": "KW", "OMN": "OM", "DZA": "DZ",
    "LBY": "LY", "SDN": "SD", "IRN": "IR", "NGA": "NG", "PSE": "PS", "PAL": "PS",
    "ZAF": "ZA", "BGD": "BD", "LKA": "LK", "DEU": "DE",
}


def nationality_flag(nat: str | None) -> str:
    """Flag EMOJI for an IOC 3-letter nationality code (e.g. 'KSA' -> 🇸🇦), or ''
    when unmapped. NB: Windows/Chrome renders flag emoji as plain letters — prefer
    :func:`nationality_flag_img` in the UI; this stays for text/label use."""
    iso = _IOC_ISO2.get((nat or "").strip().upper())
    if not iso or len(iso) != 2 or not iso.isalpha():
        return ""
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in iso.upper())


def nationality_flag_img(nat: str | None, height: int = 13):
    """Small flag IMAGE for an IOC code (flagcdn.com PNG), or None when unmapped.
    Renders on every OS including Windows, where flag emoji do not. Callers should
    still show the country code alongside so a blocked image degrades gracefully."""
    iso = _IOC_ISO2.get((nat or "").strip().upper())
    if not iso:
        return None
    return html.Img(src=f"https://flagcdn.com/h20/{iso.lower()}.png", alt="",
                    style={"height": f"{height}px", "width": "auto", "borderRadius": "2px",
                           "boxShadow": "0 0 0 1px rgba(0,0,0,0.10)", "verticalAlign": "middle"})


def athletics_age_band(age) -> str | None:
    """World Athletics age group for an age: U16 / U18 / U20 / Senior. None if the
    age is missing / non-numeric."""
    if not isinstance(age, (int, float)):
        return None
    if age < 16:
        return "U16"
    if age < 18:
        return "U18"
    if age < 20:
        return "U20"
    return "Senior"


def _banner_fmt_dob(v) -> str | None:
    if not v:
        return None
    try:
        if hasattr(v, "strftime"):
            return v.strftime("%d-%b-%Y")
        from datetime import datetime
        return datetime.strptime(str(v)[:10], "%Y-%m-%d").strftime("%d-%b-%Y")
    except Exception:  # noqa: BLE001
        return str(v)


def _banner_tag(text, kind="neutral"):
    palette = {
        "target": ("#fef3c7", "#8a6500", "transparent"),
        "future": ("#e7effb", "#1d4ed8", "transparent"),
    }.get(kind, ("#f8fafc", SLATE["500"], "#e2e8f0"))
    bg, fg, border = palette
    star = html.I(className="fas fa-star",
                  style={"fontSize": "8px", "marginRight": "5px"}) if kind == "target" else None
    return html.Span([star, text] if star else text, style={
        "fontSize": "11.5px", "fontWeight": "700", "padding": "3px 11px", "borderRadius": "999px",
        "background": bg, "color": fg, "border": "1px solid " + border, "whiteSpace": "nowrap"})


def athlete_banner(
    *, name: str, event: str | None = None, nationality: str | None = None,
    sex: str | None = None, age=None, date_of_birth=None, age_group: str | None = None,
    photo_url: str | None = None, is_target: bool = False, pathway: str | None = None,
    margin_bottom: str = "12px",
) -> html.Div:
    """Thin athlete identity banner (one low card): a ringed avatar, the name + an
    event accent chip, then flag-tagged nationality / sex / age with an age-group
    pill and a muted DOB, and status tags (Target / pathway) on the right.

    A pure render helper — pass the fields; no store / callback wiring. ``age_group``
    defaults to :func:`athletics_age_band` of ``age``; ``nationality`` is shown with
    its :func:`nationality_flag`. Replaces per-app hand-rolled identity headers.
    """
    name = name or "Unknown"
    band = age_group if age_group is not None else athletics_age_band(age)
    ring = "#e0b53a" if is_target else ("#3b82f6" if pathway == "Future Target" else "#cbd5e1")
    sz = 42
    common = {"width": f"{sz}px", "height": f"{sz}px", "flex": f"0 0 {sz}px",
              "borderRadius": "50%", "border": f"2px solid {ring}",
              "boxShadow": "0 0 0 3px #ffffff, 0 1px 3px rgba(2,23,60,0.18)"}
    if photo_url:
        avatar = html.Img(src=photo_url, alt="",
                          style={**common, "objectFit": "cover", "objectPosition": "center 20%"})
    else:
        avatar = html.Div(_initials(name), style={
            **common, "display": "flex", "alignItems": "center", "justifyContent": "center",
            "background": f"linear-gradient(135deg, {ASPIRE}, #001d3d)", "color": "white",
            "fontWeight": "700", "fontSize": "15px"})

    dot = html.Span("·", style={"color": "#cbd5e1", "margin": "0 1px"})
    meta = []
    if nationality:
        flag_img = nationality_flag_img(nationality)
        nat_kids = ([flag_img, html.Span(nationality, style={"marginLeft": "5px"})]
                    if flag_img is not None else [html.Span(nationality)])
        meta.append(html.Span(nat_kids, style={
            "fontWeight": "600", "color": SLATE["900"],
            "display": "inline-flex", "alignItems": "center"}))
    if sex:
        meta += [dot, html.Span(sex)]
    if isinstance(age, (int, float)):
        meta += [dot, html.Span(f"{age:.1f}y")]
    if band:
        meta.append(html.Span(band, style={
            "fontSize": "11px", "fontWeight": "700", "padding": "1px 8px", "marginLeft": "6px",
            "borderRadius": "999px", "background": "#eef2f7", "color": "#334155"}))
    dob_txt = _banner_fmt_dob(date_of_birth)
    if dob_txt:
        meta.append(html.Span(f"DOB {dob_txt}", style={
            "marginLeft": "8px", "fontSize": "11.5px", "color": "#94a3b8"}))

    event_chip = html.Span(event, style={
        "fontSize": "12px", "fontWeight": "700", "padding": "2px 9px", "borderRadius": "6px",
        "background": "#e7effb", "color": ASPIRE, "whiteSpace": "nowrap"}) if event else None

    ident = html.Div(style={"flex": "1", "minWidth": "0", "display": "flex",
                            "alignItems": "center", "gap": "9px", "flexWrap": "wrap"}, children=[
        html.Span(name, style={"fontSize": "16.5px", "fontWeight": "700",
                               "color": SLATE["900"], "whiteSpace": "nowrap"}),
        event_chip,
        html.Span(meta, style={"fontSize": "12.5px", "color": SLATE["500"], "display": "flex",
                               "alignItems": "center", "gap": "4px", "flexWrap": "wrap"}),
    ])

    # Target status shows as ONE gold chip (it already carries a star icon). A
    # `pathway` of "Target" is the same fact as `is_target`, so it must NOT render
    # a second, grey "Target" chip (that produced the duplicate Kenny flagged
    # 2026-09-14). Render the pathway chip only when it says something the gold
    # chip doesn't (e.g. "Future Target").
    tags = []
    if is_target or pathway == "Target":
        tags.append(_banner_tag("Target", kind="target"))
    elif pathway and pathway != "Non-Target":
        tags.append(_banner_tag(pathway, kind="future" if pathway == "Future Target" else "neutral"))

    return html.Div(className="card", style={
        "marginBottom": margin_bottom, "padding": "9px 15px",
        "borderLeft": f"3px solid {ASPIRE}"}, children=[
        html.Div([avatar, ident,
                  html.Div(tags, style={"display": "flex", "gap": "6px", "flexWrap": "wrap"})],
                 style={"display": "flex", "gap": "13px", "alignItems": "center"}),
    ])


BANNER_ID = "selected-athlete-banner"


def selected_athlete_banner(
    store_id: str = "athlete-store",
    banner_id: str = BANNER_ID,
) -> html.Div:
    """Empty div that auto-fills with an ``aspire_dash.athlete_card``
    whenever the bound store contains a real athlete (gated on
    ``player_id``, NOT on ``mrn`` — SAMS can return players whose MRN
    hasn't been linked yet, and we still want the card visible so the
    missing-MRN warning surfaces inline).

    Mount this near the top of any page driving off ``athlete-store``.
    Wire the fill callback ONCE per app via :func:`register_athlete_banner`.

    Parameters
    ----------
    store_id : str
        ``dcc.Store`` id holding the selected athlete dict. The store
        itself must be mounted elsewhere (typically at app level so it
        survives page navigation).
    banner_id : str
        ``html.Div`` id — the callback writes ``children`` here.

    Example::

        from aspire_dash.athlete import (
            selected_athlete_banner, register_athlete_banner,
        )

        # In layout — near the page top:
        layout = html.Div([
            selected_athlete_banner(),
            ...rest of page...,
        ])

        # Once after Dash() is created:
        register_athlete_banner(app)
    """
    return html.Div(id=banner_id, className="mb-3")


def register_athlete_banner(
    app,
    *,
    store_id: str = "athlete-store",
    banner_id: str = BANNER_ID,
    on_missing_mrn_warn: bool = True,
    extra_actions=None,
) -> None:
    """Wire the callback that fills :func:`selected_athlete_banner`.

    Idempotent enough to call once per app even if multiple pages mount
    the banner div — the callback writes the same banner from one store
    so the data is consistent across the app.

    Parameters
    ----------
    app : dash.Dash
        The app instance.
    store_id : str
        ``dcc.Store`` id holding the selected athlete dict.
    banner_id : str
        ``html.Div`` id mounted by ``selected_athlete_banner``.
    on_missing_mrn_warn : bool
        If True (default), append a warning Alert beneath the card when
        the athlete has a ``player_id`` but no ``mrn`` (a known SAMS
        edge case — capture flows that need an MRN can't bind without
        one).
    extra_actions : Component | callable(athlete) -> Component | list | None
        Optional consumer-supplied action buttons rendered BENEATH the
        card and BENEATH the missing-MRN warning. Two supported shapes:

        - **Component / list of components** — static; same actions for
          every athlete. Good for "Change / Clear" pairs whose ids are
          fixed.
        - **Callable** — ``fn(athlete: dict) -> Component | list`` —
          called per render so actions can be MRN-aware or athlete-
          specific (e.g. show Clear only when an athlete is picked).

        The result is wrapped in
        ``html.Div(className="d-flex align-items-center mt-2")`` so
        consumers don't have to repeat the row styling. Pass ``None``
        (default) to omit the actions row entirely — backwards-
        compatible with v0.37 callers.

    Examples
    --------
    Static actions::

        from dash import html
        import dash_bootstrap_components as dbc

        register_athlete_banner(
            app,
            extra_actions=dbc.Button("Reload", id="reload-athlete",
                                     color="link", size="sm"),
        )

    Per-athlete callable (the Change + Clear pattern used by
    aspire-nutrition)::

        def _actions(athlete):
            return [
                dbc.Button("Change", id="picker-trigger",
                           color="link", size="sm", className="me-3"),
                dbc.Button("Clear",  id={"type": "athlete-clear", "k": 0},
                           color="link", size="sm"),
            ]

        register_athlete_banner(app, extra_actions=_actions)
    """
    from .v12_helpers import athlete_card as _athlete_card

    @app.callback(
        Output(banner_id, "children"),
        Input(store_id, "data"),
    )
    def _render_athlete_banner(athlete):
        # Gate on player_id, not mrn — SAMS may return an athlete with
        # no MRN linked yet, and we still want the card visible (the
        # warning surfaces the missing-MRN state inline so the user
        # knows why downstream saves are disabled).
        if (not athlete or not isinstance(athlete, dict)
                or not athlete.get("player_id")):
            return None

        name      = athlete.get("full_name") or athlete.get("name") or "—"
        photo     = athlete.get("photo_url") or athlete.get("imageUrl")
        sport     = (athlete.get("sport") or "").upper()
        age       = athlete.get("age")
        is_target = bool(athlete.get("is_target"))
        has_mrn   = bool(athlete.get("mrn"))

        meta_parts = []
        if sport:
            meta_parts.append(sport)
        if age:
            meta_parts.append(f"age {age}")
        if is_target:
            meta_parts.append("TARGET")
        meta = " · ".join(meta_parts) if meta_parts else "Aspire athlete"

        children = [
            _athlete_card(
                name,
                photo_url=photo,
                meta=meta,
                tone="good" if is_target else "aspire",
            ),
        ]
        if on_missing_mrn_warn and not has_mrn:
            children.append(dbc.Alert(
                [html.I(className="fa-solid fa-triangle-exclamation me-2"),
                 html.Strong("No MRN registered in SAMS. "),
                 "Capture & save are blocked until SAMS links an MRN to "
                 "this athlete. Analysis-only views still work."],
                color="warning", className="mt-2 mb-0 py-2",
                style={"fontSize": "0.82rem"},
            ))

        # v0.38 — optional consumer action row beneath the card. Skipped
        # entirely when extra_actions is None so the DOM is identical to
        # v0.37 for existing callers.
        if extra_actions is not None:
            actions = (extra_actions(athlete) if callable(extra_actions)
                       else extra_actions)
            if actions is not None:
                children.append(html.Div(
                    actions,
                    className="d-flex align-items-center mt-2",
                ))
        return html.Div(children, style={"maxWidth": "420px"})
