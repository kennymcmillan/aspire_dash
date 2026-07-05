"""Athlete components — avatar + profile header + banner with actions."""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from aspire_dash.athlete import (
    athlete_avatar, athlete_profile_header, athlete_hero,
    selected_athlete_banner, register_athlete_banner,
)

from ._shared import section, example, code_block

dash.register_page(__name__, path="/athlete", title="Athlete", name="Athlete")


_SAMPLE_PHOTO = ("https://aspirepictures.blob.core.windows.net/"
                  "shared/aspire-academy-logo.png")  # SAMS-style public URL


# v0.38 — wire two demo banners against two distinct stores so the page
# can show both the static-actions and the per-athlete-callable shapes
# side-by-side. Each banner mounts an `html.Div(id=...)` and the
# upstream callback fills it from the bound store's data.
_DEMO_STORE_STATIC = "demo-athlete-store-static"
_DEMO_BANNER_STATIC = "demo-athlete-banner-static"
_DEMO_STORE_CALL = "demo-athlete-store-call"
_DEMO_BANNER_CALL = "demo-athlete-banner-call"

_DEMO_ATHLETE = {
    "player_id": 1234,
    "full_name": "Mohammed AlHazaa",
    "sport": "Fencing",
    "age": 17,
    "mrn": "MRN-9001",
    "is_target": True,
}


def _demo_actions(_athlete):
    """Per-athlete callable shape — Change / Clear pair."""
    return [
        dbc.Button(
            [html.I(className="fa-solid fa-pen-to-square me-1"), "Change"],
            id="demo-banner-change", color="link", size="sm",
            n_clicks=0,
            className="p-0 text-decoration-none me-3",
            style={"color": "#004185", "fontSize": "0.8rem",
                   "fontWeight": "500"},
        ),
        dbc.Button(
            [html.I(className="fa-solid fa-xmark me-1"), "Clear"],
            id="demo-banner-clear", color="link", size="sm",
            n_clicks=0,
            className="p-0 text-decoration-none text-secondary",
            title="Clear selection",
            style={"fontSize": "0.8rem"},
        ),
    ]


# Register both banner callbacks once at import. The demo app calls
# `setup_app` before pages register, so this fires during page
# discovery — same pattern any consumer would use after `Dash(...)`.
try:
    _app = dash.get_app()
    register_athlete_banner(
        _app,
        store_id=_DEMO_STORE_STATIC,
        banner_id=_DEMO_BANNER_STATIC,
        extra_actions=dbc.Button(
            [html.I(className="fa-solid fa-rotate me-1"), "Reload"],
            id="demo-banner-reload", color="link", size="sm",
            n_clicks=0,
            className="p-0 text-decoration-none",
            style={"color": "#004185", "fontSize": "0.8rem"},
        ),
    )
    register_athlete_banner(
        _app,
        store_id=_DEMO_STORE_CALL,
        banner_id=_DEMO_BANNER_CALL,
        extra_actions=_demo_actions,
    )
except Exception:  # noqa: BLE001
    # If page imports outside a Dash app context (sweep test, docs build,
    # etc), the demo just renders without live banner data.
    pass


def layout():
    return html.Div([
        html.H1("Athlete Components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Avatars and profile headers — used in every per-athlete page "
                "(medical, nutrition, endurance, attendance, whoop).",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("athlete_avatar",
                 "Photo if available, initials circle fallback. Pass the "
                 "SAMS imageUrl directly — browser fetches from azfpictures."),
        example(
            "Sizes — initials fallback",
            html.Div([
                athlete_avatar(None, name="Ali Turki Owaida", size="sm"),
                athlete_avatar(None, name="Khaled Hussein",   size="md"),
                athlete_avatar(None, name="Abdalla Khalifa",  size="lg"),
            ], style={"display": "flex", "gap": "12px",
                       "alignItems": "center"}),
            'athlete_avatar(None, name="Ali Turki", size="sm")\n'
            'athlete_avatar(None, name="Khaled",    size="md")\n'
            'athlete_avatar(None, name="Abdalla",   size="lg")',
        ),
        example(
            "With photo (real SAMS imageUrl in your app)",
            html.Div([
                athlete_avatar(_SAMPLE_PHOTO, name="With photo", size="md"),
                athlete_avatar(_SAMPLE_PHOTO, name="Target", size="md",
                                is_target=True),
            ], style={"display": "flex", "gap": "12px",
                       "alignItems": "center"}),
            'athlete_avatar(profile["imageUrl"], profile["fullName"], size="md")\n'
            'athlete_avatar(url, name, size="md", is_target=True)  # gold ring',
        ),

        section("athlete_profile_header",
                 "Hero banner used at the top of per-athlete pages."),
        example(
            "Profile header",
            athlete_profile_header(
                name="Ali Turki Owaida",
                photo_url=None,
                sport="Fencing",
                subtitle="SENIOR · Sobirov Abror",
            ),
            'athlete_profile_header(\n'
            '    name="Ali Turki Owaida",\n'
            '    photo_url=profile.get("imageUrl"),\n'
            '    sport="Fencing",\n'
            '    subtitle="SENIOR · Sobirov Abror",\n'
            ')',
        ),
        example(
            "With badges + target ring",
            athlete_profile_header(
                name="Mohammed AlHazaa",
                photo_url=None,
                sport="Fencing",
                subtitle="SENIOR · National squad",
                is_target=True,
                badges=[
                    html.Span("Captain",
                               style={"background": "#dbeafe",
                                       "color": "#0369a1",
                                       "padding": "2px 8px",
                                       "borderRadius": "10px",
                                       "fontSize": "11px",
                                       "fontWeight": 600}),
                ],
            ),
            'athlete_profile_header(\n'
            '    name="Mohammed AlHazaa",\n'
            '    sport="Fencing",\n'
            '    subtitle="SENIOR · National squad",\n'
            '    is_target=True,  # gold ring\n'
            '    badges=[html.Span("Captain", ...)],\n'
            ')',
        ),

        section("athlete_hero",
                 "Richer profile-top strip (promoted from the Athletics "
                 "Benchmarking app): rectangular photo with a status-tone rim "
                 "glow, name + optional flag, and a row of labelled key/value "
                 "fields. Pure data → component."),
        example(
            "Hero with field row + availability rim",
            athlete_hero(
                name="Mutaz Essa Barshim",
                photo_url=None,
                status_tone="good",
                fields=[
                    ("Event", "High Jump"),
                    ("Age", "34y 2m"),
                    ("Date of birth", "1991-06-24"),
                    ("Coach", "Stanley Franks"),
                    ("Pathway", "Elite"),
                ],
            ),
            'athlete_hero(\n'
            '    name=profile["fullName"],\n'
            '    photo_url=profile.get("imageUrl"),\n'
            '    status_tone="good",  # good/great green · warn amber · bad red · neutral grey\n'
            '    fields=[\n'
            '        ("Event", "High Jump"),\n'
            '        ("Age", "34y 2m"),\n'
            '        ("Coach", "Stanley Franks"),\n'
            '    ],\n'
            ')',
        ),
        example(
            "Unavailable tone (red rim) + initials fallback",
            athlete_hero(
                name="Ali Turki Owaida",
                photo_url=None,
                status_tone="bad",
                fields=[
                    ("Event", "Long Jump"),
                    ("Age", "19y 8m"),
                    ("Status", "In rehab — hamstring"),
                ],
            ),
            'athlete_hero(name="Ali Turki Owaida", status_tone="bad",\n'
            '             fields=[("Event", "Long Jump"), ("Age", "19y 8m")])',
        ),

        # v0.38 — selected_athlete_banner + register_athlete_banner with
        # the new extra_actions slot.
        section("selected_athlete_banner + register_athlete_banner",
                 "v0.38 — persistent page-top banner driven by an "
                 "athlete-store. New extra_actions= slot lets consumers "
                 "add buttons (Change / Clear / Reload) beneath the card."),

        # Mock the two stores with a pre-filled athlete dict so the
        # banners render without a real picker on this demo page.
        dcc.Store(id=_DEMO_STORE_STATIC, data=_DEMO_ATHLETE),
        dcc.Store(id=_DEMO_STORE_CALL, data=_DEMO_ATHLETE),

        example(
            "Static actions — single reusable component",
            html.Div([selected_athlete_banner(
                store_id=_DEMO_STORE_STATIC,
                banner_id=_DEMO_BANNER_STATIC,
            )]),
            "register_athlete_banner(\n"
            "    app,\n"
            "    store_id='athlete-store',\n"
            "    extra_actions=dbc.Button('Reload', id='reload-athlete',\n"
            "                              color='link', size='sm'),\n"
            ")",
        ),
        example(
            "Per-athlete callable — Change + Clear pair",
            html.Div([selected_athlete_banner(
                store_id=_DEMO_STORE_CALL,
                banner_id=_DEMO_BANNER_CALL,
            )]),
            "def _actions(athlete):\n"
            "    return [\n"
            "        dbc.Button('Change', id='picker-trigger', ...),\n"
            "        dbc.Button('Clear',  id={'type': 'athlete-clear',\n"
            "                                  'k': 0}, ...),\n"
            "    ]\n\n"
            "register_athlete_banner(app, extra_actions=_actions)",
        ),
        html.P("Pass `extra_actions=None` (default) to keep v0.37 behaviour "
                "exactly — no action row, identical DOM.",
                style={"color": "#64748b", "fontSize": "13px",
                       "marginTop": "8px"}),
    ], style={"padding": "24px"})
