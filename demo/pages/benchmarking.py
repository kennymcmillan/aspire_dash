"""Benchmarking — performance vs age, percentiles, standards and records.

Home of `percentile_age_chart` + `age_percentile_bands`: the sport-agnostic
"how good is this for the athlete's age" visual. One athlete (or a squad) plotted
over a shaded age-percentile corridor, with any number of benchmark lines
(qualifying standards, world / continental / championship records). Works for
runs (faster is better, time labels) and jumps / throws / scores (higher is
better), and connects to data of any shape (column mapping + a bands helper).
"""
import dash
import numpy as np
from dash import dcc, html

from aspire_dash.plots import percentile_age_chart, age_percentile_bands
from aspire_dash.sports import benchmark_table

from ._shared import section, code_block

dash.register_page(__name__, path="/benchmarking", title="Benchmarking",
                   name="✨ Benchmarking")


def _g(fig, code):
    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False}),
        code_block(code),
    ], className="card", style={"marginBottom": "16px"})


# --- Running event: 800m. Faster is better (lower_is_better), time labels, ----
# records + standard, corridor built from a raw population, two athletes.
_r = np.random.default_rng(3)
_POP = []
for _a in range(14, 21):
    _c = 138 - (_a - 14) * 2.2
    for _t in _c + _r.normal(0, 5, 30):
        _POP.append({"age": _a + float(_r.uniform(-0.4, 0.4)), "t": float(_t)})
_BANDS_800 = age_percentile_bands(_POP, age_col="age", value_col="t",
                                  age_step=1.0, lower_is_better=True)
_ATH_A = [
    {"yrs": 14.2, "time": 132.0, "best": True}, {"yrs": 15.6, "time": 126.4, "best": False},
    {"yrs": 16.4, "time": 120.1, "best": True}, {"yrs": 17.5, "time": 114.8, "best": True},
    {"yrs": 18.2, "time": 111.3, "best": True},
]
_ATH_B = [
    {"yrs": 14.6, "time": 135.5, "best": True}, {"yrs": 15.8, "time": 129.0, "best": True},
    {"yrs": 16.9, "time": 124.2, "best": True}, {"yrs": 17.9, "time": 118.6, "best": True},
]
_REF_800 = [
    {"y": 110.0, "label": "World U20 standard (1:50.00)"},
    {"y": 104.0, "label": "Asian U20 record (1:44.0)"},
    {"y": 100.9, "label": "World record (1:40.91)"},
]

# --- Field event: High Jump. Higher is better, metres, one athlete + overlay. -
# p100 = the elite ceiling: percentile_age_chart draws it as the gold dashed
# "100th percentile (elite)" line (the world-class target the marks chase).
_HJ_BANDS = [
    {"age": 13, "p10": 1.25, "p25": 1.35, "p50": 1.45, "p75": 1.58, "p90": 1.65, "p100": 1.80},
    {"age": 14, "p10": 1.35, "p25": 1.45, "p50": 1.55, "p75": 1.65, "p90": 1.72, "p100": 1.88},
    {"age": 15, "p10": 1.45, "p25": 1.55, "p50": 1.66, "p75": 1.78, "p90": 1.86, "p100": 2.02},
    {"age": 16, "p10": 1.55, "p25": 1.66, "p50": 1.78, "p75": 1.92, "p90": 2.00, "p100": 2.14},
    {"age": 17, "p10": 1.62, "p25": 1.74, "p50": 1.86, "p75": 2.00, "p90": 2.08, "p100": 2.24},
    {"age": 18, "p10": 1.66, "p25": 1.80, "p50": 1.92, "p75": 2.06, "p90": 2.13, "p100": 2.31},
]
_HJ_MARKS = [{"age": 15, "mark": 1.70}, {"age": 16, "mark": 1.85},
             {"age": 17, "mark": 1.97}, {"age": 18, "mark": 2.07, "pb": True}]
_HJ_OVERLAY = {"name": "Legend (same age)", "points": [
    {"age": 16, "mark": 2.06}, {"age": 17, "mark": 2.14}, {"age": 18, "mark": 2.27}]}

# --- Age-band PBs: percentile stars + the benchmark table (v0.70 / v0.71) ------
# Shape produced by aspire_data.benchmarks.best_pb_by_ageband(with_percentile=True):
# the best PB in each Power-of-10 age band + its percentile vs the historical norms.
_BAND_PBS = [
    {"age_band_label": "13.5 - 14.5", "age": 14.2, "mark": 132.0, "date": "2022-04-06", "n": 2, "percentile": 22},
    {"age_band_label": "14.5 - 15.5", "age": 15.6, "mark": 126.4, "date": "2023-03-10", "n": 4, "percentile": 41},
    {"age_band_label": "15.5 - 16.5", "age": 16.4, "mark": 120.1, "date": "2024-02-23", "n": 5, "percentile": 64},
    {"age_band_label": "16.5 - 17.5", "age": 17.5, "mark": 114.8, "date": "2025-01-15", "n": 3, "percentile": 78},
    {"age_band_label": "17.5 - 18.5", "age": 18.2, "mark": 111.3, "date": "2026-02-01", "n": 2, "percentile": 88},
]
# Chart marks: every result a mark, the band best a percentile-sized star.
_PCT_MARKS = (
    [{"age": r["age"], "mark": r["mark"], "pb": True, "percentile": r["percentile"]}
     for r in _BAND_PBS]
    + [{"age": 15.0, "mark": 130.0}, {"age": 16.0, "mark": 123.2},
       {"age": 17.0, "mark": 117.1}, {"age": 18.0, "mark": 113.0}]   # other results
)


def layout():
    return html.Div([
        html.H1("Benchmarking", style={"fontSize": "28px", "fontWeight": 700,
                                       "marginBottom": "8px"}),
        html.P("Performance vs age, against percentile bands and any set of "
                "standards or records. Sport-agnostic: faster-is-better runs or "
                "higher-is-better jumps and throws, with proper unit labels.",
                style={"color": "#64748b", "fontSize": "14px", "marginBottom": "24px"}),

        section("Running event (faster is better, time labels, records)"),
        _g(percentile_age_chart(
            _BANDS_800,
            [{"name": "Athlete A", "data": _ATH_A, "color": "#fbb800"},
             {"name": "Athlete B", "data": _ATH_B, "color": "#1876ab"}],
            reference_lines=_REF_800,
            age_col="yrs", value_col="time", pb_col="best",
            lower_is_better=True, value_format="time",
            y_title="800m time", title="800m progression vs age percentiles",
        ),
            "bands = age_percentile_bands(pop, age_col='age', value_col='t',\n"
            "                             lower_is_better=True)\n"
            "percentile_age_chart(\n"
            "    bands,\n"
            "    [{'name': 'Athlete A', 'data': marks_a, 'color': '#fbb800'},\n"
            "     {'name': 'Athlete B', 'data': marks_b, 'color': '#1876ab'}],\n"
            "    reference_lines=[{'y': 110.0, 'label': 'World U20 (1:50.00)'}, ...],\n"
            "    age_col='yrs', value_col='time', pb_col='best',\n"
            "    lower_is_better=True, value_format='time')"),

        section("Field event (higher is better, metres, elite ceiling, overlay)"),
        _g(percentile_age_chart(
            _HJ_BANDS, _HJ_MARKS,
            reference_lines=[{"y": 2.08, "label": "U20 qualifying 2.08 m"}],
            overlay=_HJ_OVERLAY,
            y_title="Height (m)", title="High Jump mark vs age",
        ),
            "percentile_age_chart(bands, marks,   # bands carry p100 -> elite line\n"
            "    reference_lines=[{'y': 2.08, 'label': 'U20 qualifying 2.08 m'}],\n"
            "    overlay={'name': 'Legend', 'points': [...]})   # higher is better"),

        section("Age-band PBs: percentile stars + benchmark table (v0.70 / v0.71)"),
        html.P("The best PB in each Power-of-10 age band, scored against the "
                "historical norms. On the chart every result is a mark and the "
                "band best is a star sized by its percentile (best-for-age = "
                "biggest); the table lists the same per-band bests with a "
                "tier-tinted percentile badge. Both read off one "
                "best_pb_by_ageband(with_percentile=True) call.",
                style={"color": "#64748b", "fontSize": "13px", "marginBottom": "8px"}),
        _g(percentile_age_chart(
            _BANDS_800, _PCT_MARKS,
            reference_lines=[{"y": 110.0, "label": "World U20 standard (1:50.00)"}],
            lower_is_better=True, value_format="time", pct_col="percentile",
            y_title="800m time", title="Age-band PBs sized by percentile",
        ),
            "marks = best_pb_by_ageband(results_df, dob, event='800m',\n"
            "                           with_percentile=True)   # per-band best + pct\n"
            "percentile_age_chart(bands, marks, pct_col='percentile',\n"
            "    lower_is_better=True, value_format='time')   # star size = percentile"),
        html.Div([
            html.Div("PB percentile by age band", className="stat-label",
                     style={"margin": "4px 0 8px", "fontWeight": 600}),
            benchmark_table(_BAND_PBS, value_format="time", value_label="Best 800m"),
            code_block(
                "from aspire_dash.sports import benchmark_table\n"
                "benchmark_table(best_pb_by_ageband(df, dob, event='800m',\n"
                "                                   with_percentile=True),\n"
                "                value_format='time', value_label='Best 800m')"),
        ], className="card", style={"marginBottom": "16px"}),

        section("Production bands: the historical norms table (aspire_data)"),
        html.P("In an app the corridor and elite line come straight from the "
                "historical percentile norms in Oracle "
                "(aspire_data_event_percentiles, EVENT x AGE_BIN at every 5%), "
                "via aspire_data.benchmarks. One call shapes marks + bands + "
                "standard line + direction + time formatting for any sport.",
                style={"color": "#64748b", "fontSize": "13px", "marginBottom": "8px"}),
        code_block(
            "from aspire_data.benchmarks import benchmark_inputs, standard_bands\n"
            "\n"
            "# bands straight from the Oracle historical norms (incl. p100 elite):\n"
            "bands = standard_bands('800m')          # age + p10..p90 + p100\n"
            "\n"
            "# or one call for a whole athlete + event (marks, bands, U20 line):\n"
            "inp = benchmark_inputs(results_df, dob='2008-04-14', sex='M',\n"
            "                       event='800m')\n"
            "percentile_age_chart(\n"
            "    bands=inp['bands'], marks=inp['marks'],\n"
            "    reference_lines=inp['reference_lines'], pct=inp['pct'],\n"
            "    lower_is_better=inp['lower_is_better'],\n"
            "    value_format=inp['value_format'])   # elite_line=100 by default"),
    ], style={"padding": "24px"})
