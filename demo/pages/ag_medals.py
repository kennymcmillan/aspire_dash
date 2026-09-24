"""Asian Games design: medal standings (rounded hero variant)."""
import dash
from dash import Input, Output, callback, dcc, html

from aspire_dash.asian_games import (
    AG_DISCIPLINES, ag_choice_id, ag_empty, ag_hero_heading, ag_hero_stats, ag_medal_table,
    ag_page_title, ag_pill_tabs, ag_results_table, ag_section_title, ag_subtitle,
)

from ._ag_common import ag_page, sample_note
from ._ag_data import MEDAL_TABLE, medallists

dash.register_page(__name__, path="/ag/medals", title="AG · Medals", name="AG Medals")

DISCS = sorted({b["code"] for r in MEDAL_TABLE for b in r["breakdown"]})


def layout(bio=None, **_):
    g = sum(r["gold"] for r in MEDAL_TABLE)
    t = sum(r["total"] for r in MEDAL_TABLE)
    hero = ag_hero_heading("Medal standings", eyebrow="Medals",
                           children=ag_hero_stats([(str(len(MEDAL_TABLE)), "NOCs on the table"),
                                                   (str(g), "Gold medals"), (str(t), "Medals in total")]))
    body = [
        html.Div(ag_pill_tabs("med-tab", ["Medal standings", "Medallists"], "Medal standings",
                              variant="outline", center=True), style={"margin": "8px 0 12px"}),
        ag_page_title("Medal standings"),
        dcc.Dropdown(id="med-disc", options=[{"label": "All disciplines", "value": "ALL"}] +
                     [{"label": AG_DISCIPLINES[d][0], "value": d} for d in DISCS],
                     value="ALL", clearable=False, className="ag-select"),
        html.Div(id="med-subtitle", style={"marginTop": "16px"}),
        html.Div(id="med-body"),
        sample_note(),
    ]
    return ag_page(body, active="/ag/medals", hero=hero, hero_variant="rounded", bio=bio)


def _table_for(disc):
    if disc in (None, "ALL"):
        return MEDAL_TABLE
    rows = []
    for r in MEDAL_TABLE:
        b = next((b for b in r["breakdown"] if b["code"] == disc), None)
        if b:
            rows.append({"noc": r["noc"], "gold": b["gold"], "silver": b["silver"], "bronze": b["bronze"],
                         "breakdown": [b]})
    rows.sort(key=lambda r: (-r["gold"], -r["silver"], -r["bronze"]))
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return rows


@callback(
    Output("med-body", "children"),
    Output("med-subtitle", "children"),
    Input(ag_choice_id("med-tab"), "data"),
    Input("med-disc", "value"),
)
def _render(tab, disc):
    label = "All disciplines" if disc in (None, "ALL") else AG_DISCIPLINES[disc][0]
    if tab == "Medallists":
        rows = medallists()
        if disc not in (None, "ALL"):
            rows = [r for r in rows if r["discipline"] == disc]
        cols = [{"key": "medal", "label": "", "kind": "medal", "width": "30px"},
                {"key": "surname", "label": "Medallist", "kind": "athlete"},
                {"key": "event", "label": "Event", "kind": "text", "width": "280px", "hide_sm": True},
                {"key": "mark", "label": "Result", "kind": "mark", "width": "120px", "align": "right"}]
        body = [ag_section_title("Medallists", aside=f"{len(rows)} from finished finals"),
                ag_results_table(cols, rows, focus_noc="QAT",
                                 empty_text="No finals in this discipline have finished in the sample data.")]
        return body, ag_subtitle(label)
    rows = _table_for(disc)
    if not rows:
        return ag_empty("No medals in this discipline yet."), ag_subtitle(label)
    return ag_medal_table(rows, focus_noc="QAT", open_noc="QAT"), ag_subtitle(label)
