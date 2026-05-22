"""Athlete components — avatar + profile header."""
import dash
from dash import html

from aspire_dash.athlete import athlete_avatar, athlete_profile_header

from ._shared import section, example

dash.register_page(__name__, path="/athlete", title="Athlete", name="Athlete")


_SAMPLE_PHOTO = ("https://aspirepictures.blob.core.windows.net/"
                  "shared/aspire-academy-logo.png")  # SAMS-style public URL


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
    ], style={"padding": "24px"})
