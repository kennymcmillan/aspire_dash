"""Render percentile_age_chart to standalone HTML to screenshot + iterate.
Exercises the flexible API: bands built from a raw population via
age_percentile_bands, marks with CUSTOM column names, multiple athlete series,
lower_is_better y-flip (time event), and several benchmark reference lines."""
import random
import sys
from aspire_dash.plots import percentile_age_chart, age_percentile_bands

# --- raw population of 800m times by age -> bands via the helper -------------
random.seed(7)
POP = []
for age in range(14, 21):
    centre = 138 - (age - 14) * 2.2
    for _ in range(40):
        POP.append({"age_years": age + random.uniform(-0.4, 0.4),
                    "time_s": centre + random.gauss(0, 5)})
bands = age_percentile_bands(POP, age_col="age_years", value_col="time_s",
                             age_step=1.0, lower_is_better=True)

# --- two athletes, with CUSTOM column names (no renaming needed) -------------
ATHLETE_A = [
    {"yrs": 14.2, "time": 132.0, "best": True},
    {"yrs": 15.1, "time": 128.4, "best": False},
    {"yrs": 16.0, "time": 122.1, "best": True},
    {"yrs": 17.3, "time": 116.8, "best": True},
    {"yrs": 18.1, "time": 112.3, "best": True},
]
ATHLETE_B = [
    {"yrs": 14.5, "time": 136.0, "best": True},
    {"yrs": 15.6, "time": 130.2, "best": True},
    {"yrs": 16.7, "time": 126.5, "best": True},
    {"yrs": 17.8, "time": 121.0, "best": True},
]
marks = [
    {"name": "Abdulrahman M.", "data": ATHLETE_A, "color": "#fbb800"},
    {"name": "Squad mate", "data": ATHLETE_B, "color": "#1876ab"},
]

REF = [
    {"y": 110.0, "label": "World U20 entry standard (1:50.00)"},
    {"y": 104.0, "label": "Asian U20 record (1:44.0)"},
    {"y": 100.9, "label": "World record (1:40.91)"},
]

fig = percentile_age_chart(
    bands, marks,
    reference_lines=REF,
    age_col="yrs", value_col="time", pb_col="best",  # connect any column names
    lower_is_better=True,                              # time event: faster = up
    value_format="time",                               # axis + hover as 1:50.00
    title="800m progression vs age percentiles",
    y_title="800m time",
)
out = sys.argv[1] if len(sys.argv) > 1 else "forge_chart.html"
fig.write_html(out, include_plotlyjs="cdn", full_html=True)
print("wrote", out, "| band rows:", len(bands))
