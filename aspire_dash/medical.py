"""Medical-domain components — body silhouette + injury list helpers.

Promoted from medical-dashboard so any Aspire app that touches injury,
load, or body-region data can render a consistent heatmap. Reuse
candidates: attendance (sickness/injury overlay), training-load
(soreness logged per region), athlete profile (longitudinal injury
history).

Body silhouette source SVG: etal/bodymap (MIT) — anatomical body map
with named IDs per region. We map SAMS region names onto sets of
bodymap IDs, then string-replace `fill` attributes to produce a
colourised SVG.
"""
from __future__ import annotations
import re
from pathlib import Path

import pandas as pd

# Map: SAMS region name → list of bodymap SVG element IDs to fill.
# Both views (front / back) are filled where applicable.
SAMS_TO_BODYMAP = {
    "HEAD":      ["head_front", "head_back"],
    "NECK":      ["neck_front", "neck_back"],
    "SHOULDER":  ["shoulder_left_front", "shoulder_right_front",
                   "shoulder_left_back",  "shoulder_right_back",
                   "deltoid_left_front", "deltoid_right_front"],
    "CHEST/RIBS/UPPER BACK": [
        "chest_left_front", "chest_right_front",
        "midtorso_left_front", "midtorso_right_front",
        "upperback_left", "upperback_right",
        "midback_left", "midback_right",
    ],
    "ABDOMEN":   ["abdomen_left_front", "abdomen_right_front"],
    "PELVIS/LOW BACK": ["lowerback_left", "lowerback_right",
                         "gluteal_left", "gluteal_right"],
    "HIP/GROIN": ["pelvis_left_front", "pelvis_right_front"],
    "ELBOW":     ["elbow_left_front", "elbow_right_front",
                   "elbow_left_back",  "elbow_right_back"],
    "FOREARM":   ["forearm_left_front", "forearm_right_front",
                   "forearm_left_back",  "forearm_right_back",
                   "arm_left_front", "arm_right_front",
                   "arm_left_back",  "arm_right_back"],
    "WRIST":     [],   # bodymap has no wrist node — collapse into hand
    "HAND":      ["hand_left_palm", "hand_right_palm",
                   "hand_left_back", "hand_right_back"],
    "THIGH":     ["thigh_left_front", "thigh_right_front",
                   "thigh_left_back",  "thigh_right_back"],
    "KNEE":      ["knee_left_front", "knee_right_front",
                   "knee_left_back",  "knee_right_back"],
    "LOWER LEG": ["calf_left_front", "calf_right_front",
                   "calf_left_back",  "calf_right_back",
                   "lowercalf_left_front", "lowercalf_right_front",
                   "lowercalf_left_back",  "lowercalf_right_back"],
    "ANKLE":     [],   # bodymap has no ankle node — fold into foot
    "FOOT":      ["foot_left_front", "foot_right_front",
                   "foot_left_back",  "foot_right_back"],
}


_SVG_PATH = Path(__file__).resolve().parent / "assets" / "body-bodymap.svg"


def _load_svg() -> str:
    """Load the bodymap SVG and strip Inkscape metadata so it embeds
    cleanly via dcc.Markdown."""
    svg = _SVG_PATH.read_text(encoding="utf-8")
    # Remove XML declaration
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    # Remove DOCTYPE if any
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg)
    # Remove the entire <metadata>...</metadata> block (RDF/Dublin Core junk)
    svg = re.sub(r"<metadata[^>]*>.*?</metadata>", "",
                 svg, flags=re.DOTALL)
    # Remove the empty <defs>...</defs> if present (Inkscape adds one)
    svg = re.sub(r"<defs[^>]*/>", "", svg)
    svg = re.sub(r"<defs[^>]*>\s*</defs>", "", svg)
    # Strip Inkscape and Sodipodi namespaces from attributes
    svg = re.sub(r'\sxmlns:(dc|cc|rdf|inkscape|sodipodi)="[^"]*"', "", svg)
    svg = re.sub(r'\s(inkscape|sodipodi):[\w-]+="[^"]*"', "", svg)
    # Remove sodipodi:namedview elements
    svg = re.sub(r"<sodipodi:namedview[^/]*/>", "", svg)
    svg = re.sub(r"<sodipodi:namedview[^>]*>.*?</sodipodi:namedview>", "",
                 svg, flags=re.DOTALL)
    # Constrain width so it fits the card
    svg = re.sub(r'<svg([^>]*)\swidth="[^"]*"', r'<svg\1', svg, count=1)
    svg = re.sub(r'<svg([^>]*)\sheight="[^"]*"', r'<svg\1', svg, count=1)
    svg = re.sub(r'<svg(\s[^>]*)>',
                 r'<svg\1 style="width:100%;max-width:780px;height:auto">',
                 svg, count=1)
    return svg


def _interp_colour(t: float) -> str:
    """0..1 → light-blue → Aspire navy gradient."""
    t = max(0.0, min(1.0, t))
    if t <= 0.5:
        f = t / 0.5
        r = int(0xdb + (0x60 - 0xdb) * f)
        g = int(0xea + (0xa5 - 0xea) * f)
        b = int(0xfe + (0xfa - 0xfe) * f)
    else:
        f = (t - 0.5) / 0.5
        r = int(0x60 + (0x1e - 0x60) * f)
        g = int(0xa5 + (0x3a - 0xa5) * f)
        b = int(0xfa + (0x8a - 0xfa) * f)
    return f"#{r:02x}{g:02x}{b:02x}"


_NEUTRAL_FILL = "#f1f5f9"   # regions with no data


def _set_fill(svg: str, element_id: str, fill: str) -> str:
    """Set/replace fill on a single element, identified by id="...".
    Adds a `style="fill:..."` if not present, otherwise rewrites it."""
    pattern = re.compile(
        rf'(<[^>]*\bid="{re.escape(element_id)}"[^>]*?)(/?>)',
        flags=re.DOTALL,
    )

    def _repl(m: re.Match) -> str:
        opening, closing = m.group(1), m.group(2)
        # Remove any existing fill in either attribute or inline style
        opening = re.sub(r'\sfill="[^"]*"', "", opening)
        opening = re.sub(r'fill\s*:\s*[^;"]+;?', "", opening)
        # Append fresh style fill (overrides any class fill)
        if 'style="' in opening:
            opening = re.sub(r'style="', f'style="fill:{fill};', opening,
                             count=1)
        else:
            opening = opening + f' style="fill:{fill}"'
        return opening + closing

    return pattern.sub(_repl, svg, count=1)


def render_svg(region_metric: dict[str, float],
               max_value: float | None = None) -> str:
    """Return the bodymap SVG with regions filled by metric value.

    Parameters
    ----------
    region_metric : {SAMS region name: metric value}
        e.g. {"THIGH": 4.5, "ANKLE": 0.3, "PELVIS/LOW BACK": 3.2}.
        Regions absent from the dict (or zero) get the neutral fill.
    max_value : float or None
        If provided, used as the colour-scale top. Otherwise max of values.
    """
    svg = _load_svg()

    # Strip the outer <?xml ... ?> declaration so it embeds cleanly in HTML
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)

    if not region_metric:
        # All regions get neutral
        for ids in SAMS_TO_BODYMAP.values():
            for eid in ids:
                svg = _set_fill(svg, eid, _NEUTRAL_FILL)
        return svg

    if max_value is None:
        non_zero = [v for v in region_metric.values() if v]
        max_value = max(non_zero) if non_zero else 1.0
    if max_value <= 0:
        max_value = 1.0

    for region, ids in SAMS_TO_BODYMAP.items():
        v = region_metric.get(region, 0) or 0
        fill = _interp_colour(v / max_value) if v else _NEUTRAL_FILL
        for eid in ids:
            svg = _set_fill(svg, eid, fill)
    return svg


# ── Ready-to-drop helpers ──────────────────────────────────────────────────

def body_silhouette(region_metric: dict[str, float],
                     max_value: float | None = None,
                     *, title: str | None = "Body region heatmap"):
    """Branded body-region heatmap card — title strip + SVG.

    Drop-in for any page that needs to show injury count / soreness /
    load by body region. Pass a dict ``{SAMS region: metric value}``.

    >>> from aspire_dash.medical import body_silhouette
    >>>
    >>> body_silhouette({
    ...     "THIGH": 4.5,
    ...     "ANKLE": 0.3,
    ...     "PELVIS/LOW BACK": 3.2,
    ... })
    """
    from dash import html, dcc
    children = []
    if title:
        children.append(html.Div(title, style={
            "fontSize": "11px", "fontWeight": 600,
            "textTransform": "uppercase", "letterSpacing": "0.05em",
            "color": "#64748b", "marginBottom": "8px",
        }))
    children.append(dcc.Markdown(
        render_svg(region_metric, max_value=max_value),
        dangerously_allow_html=True,
        style={"textAlign": "center"},
    ))
    # v0.19 — use medical-body-card scope for centered SVG + brand-tinted
    # drop shadow (audit recommendation, applied portfolio-wide).
    return html.Div(children, className="medical-body-card")


def injury_list(injuries: list[dict]):
    """Multi-injury container. Each row is a v0.12 ``injury_card``.

    >>> from aspire_dash.medical import injury_list
    >>>
    >>> injury_list([
    ...     {"body_part": "L Hamstring", "severity": "severe",
    ...      "status": "Out 4 wk", "detail": "Grade II strain.",
    ...      "onset_date": "2026-05-15", "days_out": 7},
    ...     ...
    ... ])
    """
    from dash import html
    from .v12_helpers import injury_card
    if not injuries:
        from .v12_helpers import aspire_empty
        return aspire_empty("No active injuries",
                             hint="All squad members fit to train.",
                             icon="fa-circle-check")
    return html.Div(
        [injury_card(**i) for i in injuries],
        style={"display": "grid",
                "gridTemplateColumns": "repeat(auto-fill, minmax(280px, 1fr))",
                "gap": "12px"},
    )
