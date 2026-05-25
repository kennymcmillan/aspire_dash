"""Ranked dropdown — multi-pick menu with tone-coloured sublabels.

Promoted in v0.37 from aspire-nutrition's diary "alternates" cell, where
each row offers the user N ranked food-match alternates with a tone-
coloured strength label. Replaces the inline outline-light chip pattern
that suffered white-text-on-white-card."""
import dash
from dash import html

from aspire_dash.components import ranked_dropdown

from ._shared import section, example

dash.register_page(__name__, path="/ranked-dropdown",
                   title="Ranked dropdown", name="Ranked dropdown")


def layout():
    return html.Div([
        html.H1("Ranked dropdown",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Bootstrap DropdownMenu where each item carries a dict id "
               "(for pattern-matched callbacks) and renders a bold "
               "primary label + an optional tone-coloured sublabel. "
               "Use it for ranked alternates, pick-from-N candidates, "
               "any 'change selection' UX where the choices have a "
               "second line of context.",
               style={"color": "#64748b", "fontSize": "14px",
                      "marginBottom": "24px"}),

        section("Ranked food matches (the source pattern)",
                 "RAG candidates ranked by score. Tone reflects strength: "
                 "success (≥ Good), warning (Borderline), danger (Weak)."),
        example(
            "Click 'Change (3 alts)' to see the menu",
            html.Div([
                html.Span("Top match:  ",
                          className="text-muted small me-2"),
                html.Span("Chicken breast, raw  ·  Generic",
                          className="fw-semibold me-3"),
                ranked_dropdown(
                    label="Change (3 alts)",
                    items=[
                        {"label": "Chicken breast, grilled",
                         "sublabel": "Good  ·  M&S Cook With",
                         "tone": "success",
                         "id_kwargs": {"type": "demo-pick-alt",
                                        "i": 1, "food_id": 102}},
                        {"label": "Chicken thigh, raw",
                         "sublabel": "Borderline  ·  Generic",
                         "tone": "warning",
                         "id_kwargs": {"type": "demo-pick-alt",
                                        "i": 1, "food_id": 103}},
                        {"label": "Chicken nuggets, frozen",
                         "sublabel": "Weak  ·  Birds Eye",
                         "tone": "danger",
                         "id_kwargs": {"type": "demo-pick-alt",
                                        "i": 1, "food_id": 104}},
                    ],
                ),
            ], style={"display": "flex", "alignItems": "center"}),
            "from aspire_dash.components import ranked_dropdown\n\n"
            "ranked_dropdown(\n"
            "    label=f'Change ({len(alts)} alts)',\n"
            "    items=[\n"
            "        {\n"
            "            'label':    alt['name'],\n"
            "            'sublabel': f'{strength}  ·  {alt[\"brand\"]}',\n"
            "            'tone':     tone_color,  # success / warning / danger\n"
            "            'id_kwargs': {'type': 'diary-pick-alt',\n"
            "                          'i': row_idx, 'food_id': alt['id']},\n"
            "        }\n"
            "        for alt, strength, tone_color in ranked\n"
            "    ],\n"
            ")\n\n"
            "# In a callback, react to clicks:\n"
            "@callback(\n"
            "    Output('diary-store', 'data'),\n"
            "    Input({'type': 'diary-pick-alt', 'i': ALL,\n"
            "           'food_id': ALL}, 'n_clicks'),\n"
            ")\n"
            "def _pick(_clicks):\n"
            "    triggered = ctx.triggered_id\n"
            "    if not triggered:\n"
            "        return no_update\n"
            "    # triggered = {'type': 'diary-pick-alt',\n"
            "    #              'i': 1, 'food_id': 102}\n"
            "    ...",
        ),

        section("Empty state",
                 "Returns a muted-italic placeholder when items=[] so the "
                 "cell never collapses to zero width."),
        example(
            "items=[] -> '—'",
            ranked_dropdown(label="Change", items=[], empty_label="—"),
            "ranked_dropdown(label='Change', items=[], empty_label='—')",
        ),

        section("Single tone — neutral picker",
                 "When ranks aren't applicable, leave tone='secondary' to "
                 "render plain muted sublabels."),
        example(
            "Neutral alternates",
            ranked_dropdown(
                label="Change region",
                items=[
                    {"label": "Knee", "sublabel": "Lower limb",
                     "tone": "secondary",
                     "id_kwargs": {"type": "demo-region", "code": "KNE"}},
                    {"label": "Ankle", "sublabel": "Lower limb",
                     "tone": "secondary",
                     "id_kwargs": {"type": "demo-region", "code": "ANK"}},
                    {"label": "Shoulder", "sublabel": "Upper limb",
                     "tone": "secondary",
                     "id_kwargs": {"type": "demo-region", "code": "SHO"}},
                ],
            ),
            "ranked_dropdown(\n"
            "    label='Change region',\n"
            "    items=[\n"
            "        {'label': 'Knee', 'sublabel': 'Lower limb',\n"
            "         'tone': 'secondary', 'id_kwargs': {...}},\n"
            "        ...\n"
            "    ],\n"
            ")",
        ),

    ], style={"maxWidth": "1100px"})
