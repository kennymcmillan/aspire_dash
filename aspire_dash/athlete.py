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
from dash import (Input, Output, State, callback_context, dcc, html, no_update)
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
