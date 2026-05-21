"""Charts & Data — Plotly template demo with DataTable."""

import dash
from dash import html, dcc, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from aspire_dash.components import card, filter_bar
from aspire_dash.charts import GRAPH_CONFIG
from aspire_dash.theme import CHART_COLORS, SLATE, ACCENT, SUCCESS, WARNING, DANGER

dash.register_page(__name__, path="/charts", title="Charts & Data", name="Charts & Data")

# Mock data
sports = ["Football", "Athletics", "Swimming", "Fencing", "Squash", "Padel", "Table Tennis", "Gymnastics"]
budget = [3200000, 2100000, 1800000, 1500000, 1200000, 900000, 850000, 700000]
spent = [2800000, 1600000, 1750000, 1100000, 800000, 650000, 400000, 550000]
pct = [round(s/b*100, 1) for s, b in zip(spent, budget)]

df = pd.DataFrame({"Sport": sports, "Budget": budget, "Spent": spent, "Utilisation": pct})
df["Remaining"] = df["Budget"] - df["Spent"]
df["Status"] = df["Utilisation"].apply(lambda x: "Over" if x > 100 else "Caution" if x > 85 else "On Track")

# Monthly trend data
months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
monthly_spend = [800000, 950000, 1100000, 1250000, 1400000, 1550000, 1700000, 1850000, 2000000]
monthly_budget = [1000000, 1200000, 1300000, 1400000, 1500000, 1600000, 1700000, 1800000, 1900000]


def layout(**kwargs):
    # Bar chart — budget vs spent
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df["Sport"], y=df["Budget"],
        name="Budget", marker_color=CHART_COLORS[0],
        opacity=0.3,
    ))
    fig_bar.add_trace(go.Bar(
        x=df["Sport"], y=df["Spent"],
        name="Spent", marker_color=CHART_COLORS[0],
    ))
    fig_bar.update_layout(
        barmode="overlay",
        height=350,
        margin=dict(t=30, b=40),
        legend=dict(orientation="h", y=1.05),
    )

    # Line chart — monthly trend
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=months, y=monthly_budget, name="Budget",
        mode="lines+markers",
        line=dict(color=SLATE["300"], dash="dash"),
        marker=dict(size=6),
    ))
    fig_line.add_trace(go.Scatter(
        x=months, y=monthly_spend, name="Actual Spend",
        mode="lines+markers",
        line=dict(color=ACCENT, width=2),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(0, 65, 133, 0.08)",
    ))
    fig_line.update_layout(height=300, margin=dict(t=30, b=40))

    # Donut chart
    fig_donut = go.Figure(go.Pie(
        labels=["Paid", "Encumbered", "Planned", "Remaining"],
        values=[8200000, 1850000, 900000, 1500000],
        hole=0.55,
        marker_colors=[SUCCESS, WARNING, CHART_COLORS[0], SLATE["200"]],
        textinfo="label+percent",
        textfont=dict(size=11),
    ))
    fig_donut.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20), showlegend=False)

    # Horizontal bar — utilisation
    colors = [DANGER if p > 100 else WARNING if p > 85 else SUCCESS for p in pct]
    fig_util = go.Figure(go.Bar(
        y=df["Sport"], x=df["Utilisation"],
        orientation="h",
        marker_color=colors,
        text=[f"{p}%" for p in pct],
        textposition="outside",
    ))
    fig_util.update_layout(
        height=300, margin=dict(t=20, b=30, l=100),
        xaxis=dict(range=[0, 120], title="Utilisation %"),
    )
    fig_util.add_vline(x=100, line_dash="dash", line_color=SLATE["300"])

    return html.Div([
        html.H2("Charts (Aspire Plotly Template)", className="section-title"),
        html.P("All charts use the aspire template — Inter font, brand colour palette, clean grid lines.",
               style={"fontSize": "13px", "color": SLATE["500"], "marginBottom": "16px"}),

        # Chart grid
        html.Div([
            html.Div([
                html.Div("Budget vs Actual by Sport", className="chart-title"),
                dcc.Graph(figure=fig_bar, config=GRAPH_CONFIG),
            ], className="chart-card", style={"flex": "2"}),
            html.Div([
                html.Div("Budget Breakdown", className="chart-title"),
                dcc.Graph(figure=fig_donut, config=GRAPH_CONFIG),
            ], className="chart-card", style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        html.Div([
            html.Div([
                html.Div("Monthly Spend Trend", className="chart-title"),
                dcc.Graph(figure=fig_line, config=GRAPH_CONFIG),
            ], className="chart-card", style={"flex": "1"}),
            html.Div([
                html.Div("Utilisation by Sport", className="chart-title"),
                dcc.Graph(figure=fig_util, config=GRAPH_CONFIG),
            ], className="chart-card", style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

        # DataTable
        html.H2("DataTable (AG Grid parity styling)", className="section-title"),
        html.P("Hover, sort, filter, active cell ring — all styled via base CSS.",
               style={"fontSize": "13px", "color": SLATE["500"], "marginBottom": "12px"}),

        dash_table.DataTable(
            id="demo-table",
            data=df.to_dict("records"),
            columns=[
                {"name": "Sport", "id": "Sport"},
                {"name": "Budget (QAR)", "id": "Budget", "type": "numeric", "format": {"specifier": ",.0f"}},
                {"name": "Spent (QAR)", "id": "Spent", "type": "numeric", "format": {"specifier": ",.0f"}},
                {"name": "Remaining", "id": "Remaining", "type": "numeric", "format": {"specifier": ",.0f"}},
                {"name": "Utilisation %", "id": "Utilisation", "type": "numeric", "format": {"specifier": ".1f"}},
                {"name": "Status", "id": "Status"},
            ],
            sort_action="native",
            filter_action="native",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px 12px", "fontSize": "13px", "fontFamily": "Inter, sans-serif"},
            style_header={"backgroundColor": "#f8fafc", "fontWeight": "600", "fontSize": "12px", "color": "#475569"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgba(248,250,252,0.5)"},
                {"if": {"filter_query": "{Status} = 'Over'"}, "backgroundColor": "#fef2f2", "color": "#991b1b"},
                {"if": {"filter_query": "{Status} = 'Caution'"}, "backgroundColor": "#fffbeb"},
            ],
        ),

    ], style={"maxWidth": "1200px"})
