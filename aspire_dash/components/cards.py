"""Cards: card, summary_card (deprecated), graph_card, info_box, file_upload_card, connect_user_chip, linear_step_card.

Auto-split from the legacy single-file components.py during the
0.8 → 1.0 refactor. Backwards-compatible: `from aspire_dash.components
import X` keeps working via the package __init__.
"""
import dash
from dash import html, dcc, clientside_callback, Input, Output, State
import dash_bootstrap_components as dbc

from ..theme import (
    SIDEBAR_WIDTH, SIDEBAR_BG, SIDEBAR_BORDER, SIDEBAR_LINK_COLOR,
    SIDEBAR_LINK_HOVER_BG, SIDEBAR_LINK_ACTIVE_BG,
    FONT_FAMILY, ACCENT, ACCENT_HOVER,
    LOGO_FILENAME, LOGO_ALT, SLATE, ASPIRE,
    SHADOW_SM, SHADOW_MD, RADIUS_LG, RADIUS_FULL,
)


__all__ = ['card', 'summary_card', 'graph_card', 'info_box', 'file_upload_card', 'connect_user_chip', 'linear_step_card']

# ── Cards ────────────────────────────────────────────────────────────────────

def card(children, className="", style=None, **kwargs):
    """Standard white card — 12px radius, shadow-sm."""
    base_style = {
        "background": "white",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "16px",
        "marginBottom": "24px",
        "boxShadow": SHADOW_SM,
    }
    if style:
        base_style.update(style)
    return html.Div(children, className=f"card {className}".strip(), style=base_style, **kwargs)


def summary_card(label, value, sub=None, icon=None, color_class=""):
    """KPI summary card (label + big value + optional subtitle).

    .. deprecated:: 0.8
        Use :func:`kpi_tile` for new code. ``summary_card`` lacks the
        left-accent stripe, vs-target progress bar, and size variants
        that the rest of the Aspire stack now standardises on.
        Kept as an alias-with-warning through 0.x — will be removed
        at 1.0.
    """
    import warnings
    warnings.warn(
        "aspire_dash.components.summary_card is deprecated; use kpi_tile() "
        "for the new Aspire signature (left-accent stripe + optional "
        "vs-target progress bar). summary_card will be removed at 1.0.",
        DeprecationWarning, stacklevel=2,
    )
    icon_el = html.I(className=icon, style={
        "fontSize": "12px", "marginRight": "4px",
    }) if icon else None

    return html.Div([
        html.Div([icon_el, label] if icon_el else label, className="card-label", style={
            "fontSize": "12px", "fontWeight": "500", "textTransform": "uppercase",
            "letterSpacing": "0.3px", "color": SLATE["500"], "marginBottom": "4px",
            "display": "flex", "alignItems": "center", "gap": "4px",
        }),
        html.Div(str(value), className="card-value", style={
            "fontSize": "22px", "fontWeight": "700", "color": SLATE["800"],
            "letterSpacing": "-0.02em", "fontVariantNumeric": "tabular-nums",
        }),
        html.Div(sub, className="card-sub", style={
            "fontSize": "12px", "color": SLATE["400"], "marginTop": "2px",
        }) if sub else None,
    ], className=f"budget-card {color_class}".strip(), style={
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": "8px",
        "padding": "16px 20px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)",
        "transition": "box-shadow 0.2s",
    })



# ── Graph Card ──────────────────────────────────────────────────────────────

def graph_card(figure, config=None, title=None, style=None, **graph_kwargs):
    """Wrap a dcc.Graph in a card with rounded corners, border, and shadow.

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        The Plotly figure to render.
    config : dict or None
        dcc.Graph config (modebar settings, etc.).
    title : str or None
        Optional title above the chart.
    style : dict or None
        Extra style overrides for the card container.
    **graph_kwargs
        Additional kwargs passed to dcc.Graph (e.g. id, className).
    """
    card_style = {
        "background": "white",
        "borderRadius": f"{RADIUS_LG}px",
        "border": f"1px solid {SLATE['200']}",
        "boxShadow": SHADOW_MD,
        "padding": "12px",
        "marginBottom": "16px",
        "overflow": "hidden",
    }
    if style:
        card_style.update(style)

    children = []
    if title:
        children.append(html.Div(title, style={
            "fontSize": "14px", "fontWeight": "600", "color": SLATE["700"],
            "padding": "4px 4px 8px",
        }))
    children.append(dcc.Graph(figure=figure, config=config or {}, **graph_kwargs))

    return html.Div(children, style=card_style)



# ── Info Box ─────────────────────────────────────────────────────────────────

def info_box(title, children, icon="fa-solid fa-circle-info"):
    """Blue info/tip box (like the Budget app status guide)."""
    return html.Div([
        html.Div([
            html.I(className=icon, style={"color": "#3b82f6", "marginRight": "8px"}),
            html.Strong(title, style={"color": "#1e40af"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
        html.Div(children),
    ], style={
        "background": "#eff6ff", "border": "1px solid #bfdbfe",
        "borderRadius": "8px", "padding": "12px 16px", "marginBottom": "16px",
    })



# ── File upload card ──────────────────────────────────────────────────────

def file_upload_card(
    id: str,
    label: str = "Drag and drop or click to upload",
    accept: str | None = None,
    icon: str = "fa-solid fa-cloud-arrow-up",
    multiple: bool = False,
    height: str = "120px",
):
    """Branded ``dcc.Upload`` dropzone with Aspire styling.

    Pattern from iso-leg-press (.dat parse) and aspire-nutrition (diary upload).
    Returns a ``dcc.Upload`` with the Aspire blue dashed border + cloud icon
    + label. Read the upload via ``Input(id, "contents")``.

    Parameters
    ----------
    id : str
        Component id for the upload.
    label : str
        Drop-zone instructions.
    accept : str or None
        MIME type / extension filter (e.g. ``".csv,.xlsx"`` or ``"image/*"``).
    icon : str
        FontAwesome class (defaults to cloud-arrow-up).
    multiple : bool
        Allow multiple files.
    height : str
        CSS height of the dropzone.
    """
    return dcc.Upload(
        id=id,
        accept=accept,
        multiple=multiple,
        children=html.Div([
            html.I(className=icon, style={
                "fontSize": "32px", "color": ASPIRE["600"], "marginBottom": "8px",
            }),
            html.Div(label, style={
                "fontSize": "13px", "color": SLATE["600"], "fontWeight": "500",
            }),
        ], style={
            "display": "flex", "flexDirection": "column",
            "alignItems": "center", "justifyContent": "center",
            "height": "100%", "textAlign": "center",
        }),
        style={
            "width": "100%",
            "height": height,
            "border": f"2px dashed {ASPIRE['400']}",
            "borderRadius": f"{RADIUS_LG}px",
            "background": "#f8fafc",
            "cursor": "pointer",
            "transition": "background-color 150ms, border-color 150ms",
        },
        style_active={
            "background": ASPIRE["50"],
            "border": f"2px dashed {ASPIRE['600']}",
        },
    )



# ── Connect user chip ─────────────────────────────────────────────────────

def connect_user_chip(default: str = "anonymous", icon: str = "fa-solid fa-user"):
    """Inline chip showing the Posit Connect-authenticated user.

    Reads the ``RSTUDIO_USER_NAME`` environment variable that Connect
    injects into every running content process. Falls back to
    ``default`` locally where the env var is unset.

    Used in mapping_app for ``updated_by`` audit, in nutrition for
    edit-attribution display. Drop into a header's ``right_content``.
    """
    import os as _os
    user = _os.environ.get("RSTUDIO_USER_NAME") or default
    return html.Span([
        html.I(className=icon, style={
            "marginRight": "6px", "fontSize": "11px", "color": SLATE["500"],
        }),
        user,
    ], style={
        "display": "inline-flex", "alignItems": "center",
        "padding": "4px 10px",
        "background": SLATE["100"],
        "color": SLATE["700"],
        "borderRadius": "999px",
        "fontSize": "12px", "fontWeight": "600",
        "fontFamily": FONT_FAMILY,
    })



# ── Linear step card (numbered) ────────────────────────────────────────────

def linear_step_card(
    step_num: int,
    title: str,
    children=None,
    description: str | None = None,
    *,
    state: str = "active",
):
    """Numbered card for linear workflows (Step 1 → 2 → 3).

    Pattern from aspire-nutrition's diary upload (Steps 1–5) and target
    setup. Numbered badge + heading + optional description + body slot.

    Parameters
    ----------
    step_num : int
        The step number rendered in the badge.
    title : str
        Heading text.
    children : object
        Body content (form fields, instructions, action buttons).
    description : str or None
        Optional one-line description below the heading.
    state : "active" | "complete" | "pending"
        Visual state. ``complete`` shows a check, ``pending`` is muted.
    """
    if state == "complete":
        badge_bg, badge_fg, badge_content = (
            "#dcfce7", "#166534",
            html.I(className="fa-solid fa-check"),
        )
    elif state == "pending":
        badge_bg, badge_fg, badge_content = (
            SLATE["100"], SLATE["500"], str(step_num),
        )
    else:
        badge_bg, badge_fg, badge_content = (
            ASPIRE["600"], "white", str(step_num),
        )

    return html.Div([
        html.Div([
            html.Div(badge_content, style={
                "width": "28px", "height": "28px", "borderRadius": "50%",
                "background": badge_bg, "color": badge_fg,
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontWeight": "700", "fontSize": "13px",
                "flexShrink": "0",
            }),
            html.Div([
                html.Div(title, style={
                    "fontSize": "15px", "fontWeight": "700",
                    "color": SLATE["800"] if state != "pending" else SLATE["400"],
                }),
                html.Div(description, style={
                    "fontSize": "12px", "color": SLATE["500"], "marginTop": "2px",
                }) if description else None,
            ], style={"marginLeft": "12px", "flex": "1"}),
        ], style={"display": "flex", "alignItems": "flex-start", "marginBottom": "10px"}),
        html.Div(children, style={"marginLeft": "40px"}) if children else None,
    ], style={
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "14px 16px",
        "boxShadow": SHADOW_SM,
        "marginBottom": "12px",
        "opacity": "0.65" if state == "pending" else "1",
    })
