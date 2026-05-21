"""Athlete components — avatar + picker + profile header."""
import dash
from dash import html

from aspire_dash.athlete import athlete_avatar, athlete_profile_header

from ._shared import section, example

dash.register_page(__name__, path="/athlete", title="Athlete", name="Athlete")


_SAMPLE = {
    "fullName": "Ali Turki Owaida",
    "playerId": 2929,
    "ageGroup": "SENIOR",
    "profileImageUrl": "https://aspirepictures.blob.core.windows.net/p/2929.jpg",
}


def layout():
    return html.Div([
        html.H1("Athlete Components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Avatars, profile headers, and the athlete picker (auto-suggest "
                "with SAMS roster — for the live registered version, see "
                "register_athlete_picker in callbacks).",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("athlete_avatar",
                 "Initials fallback when no photo, photo when available."),
        example("Sizes",
                 html.Div([
                     athlete_avatar(name="Ali Turki Owaida", size=32),
                     athlete_avatar(name="Khaled Hussein",  size=48),
                     athlete_avatar(name="Abdalla Khalifa", size=64,
                                     image_url=_SAMPLE["profileImageUrl"]),
                 ], style={"display": "flex", "gap": "12px",
                            "alignItems": "center"}),
                 "athlete_avatar(name='Ali Turki', size=48)\n"
                 "athlete_avatar(name='Khaled', size=48, image_url='https://…')"),

        section("athlete_profile_header",
                 "Banner used on per-athlete pages."),
        example("Profile header",
                 athlete_profile_header(
                     athlete=_SAMPLE,
                     show_back_link=False,
                 ),
                 "athlete_profile_header(\n"
                 "    athlete={'fullName': 'Ali Turki', 'ageGroup': 'SENIOR',\n"
                 "             'profileImageUrl': '...'},\n"
                 ")"),
    ], style={"padding": "24px"})
