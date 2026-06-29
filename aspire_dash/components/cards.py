"""Cards: card, summary_card (deprecated), graph_card, info_box,
file_upload_card, connect_user_chip, linear_step_card,
linear_step_card_collapse, meta_inline_bar, history_table, ranked_dropdown.

Auto-split from the legacy single-file components.py during the
0.8 → 1.0 refactor. Backwards-compatible: `from aspire_dash.components
import X` keeps working via the package __init__.
"""
import dash
from dash import html, dcc, clientside_callback, Input, Output, State, MATCH
import dash_bootstrap_components as dbc

from ..theme import (
    SIDEBAR_WIDTH, SIDEBAR_BG, SIDEBAR_BORDER, SIDEBAR_LINK_COLOR,
    SIDEBAR_LINK_HOVER_BG, SIDEBAR_LINK_ACTIVE_BG,
    FONT_FAMILY, ACCENT, ACCENT_HOVER,
    LOGO_FILENAME, LOGO_ALT, SLATE, ASPIRE,
    SHADOW_SM, SHADOW_MD, RADIUS_LG, RADIUS_FULL,
)


__all__ = [
    'card', 'summary_card', 'graph_card', 'info_box',
    'file_upload_card', 'connect_user_chip',
    'linear_step_card',
    # v0.37 — patterns promoted from aspire-nutrition
    'linear_step_card_collapse', 'register_linear_step_toggle',
    'meta_inline_bar',
    'history_table',
    'ranked_dropdown',
    # v0.45 — promoted from DASH_Anthro / aspire-supplements / aspire-nutrition
    'section_card',
]

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
        # v0.23: shadow + radius + bg now live in .budget-card class
        # (00_aspire_base.css). Inline override removed so hover-lift +
        # slate-tinted elev-1 work from CSS. Kept padding inline because
        # callers tune density per-page.
        "padding": "16px 20px",
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
    """Aspire-branded info/tip box. v0.32 — was Tailwind blue-500/700;
    now Aspire blue tokens so it sits in-brand."""
    from ..theme import ASPIRE
    return html.Div([
        html.Div([
            html.I(className=icon, style={"color": ASPIRE["600"], "marginRight": "8px"}),
            html.Strong(title, style={"color": ASPIRE["700"]}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
        html.Div(children),
    ], style={
        "background": "#eff6ff", "border": f"1px solid {ASPIRE['200']}",
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



# ── Linear step card (collapsible w/ summary header) — v0.37 ─────────────

def linear_step_card_collapse(
    *,
    step: int,
    title: str,
    body,
    collapse_id=None,
    summary_id: str | None = None,
    initial_open: bool = False,
    header_type: str = "linear-step-header",
):
    """Numbered step card with a click-the-header-to-toggle collapsible body.

    The header is always visible and renders:

        [step]  Title          summary-span (filled by callback)        v

    Clicking the header anywhere toggles the collapse beneath. The
    ``summary_id`` span is empty by default — consumers wire a state
    callback that writes a short one-liner ("4-day  ·  Burke standard",
    "Test Athlete  ·  ATHLETICS", "8 entries  ·  all matched", etc.) so the
    page can be scanned top-to-bottom and the user sees what's done at a
    glance.

    Promoted from the duplicate ``_step_card`` (diary.py) and
    ``_section_card`` (consultation.py) helpers in aspire-nutrition —
    same shape, same CSS, one upstream definition.

    Two integration modes are supported:

    **Mode A — string ``collapse_id`` (diary-style, custom toggle policy).**
    Pass a plain string ``collapse_id`` (e.g. ``"step-3-collapse"``). The
    consumer writes its own callback that reads
    ``Input({"type": header_type, "step": ALL}, "n_clicks")`` and writes
    ``Output("step-3-collapse", "is_open")`` — typically the same callback
    that also computes step summaries and auto-opens the next step on
    completion. Do **not** call :func:`register_linear_step_toggle` in this
    mode (the consumer owns is_open writes).

    **Mode B — pattern-matched collapse (consultation-style, plain toggle).**
    Pass ``collapse_id=None`` (default). The helper assigns a dict id
    ``{"type": header_type + "-collapse", "step": N}`` to the collapse and
    you wire one MATCH callback via :func:`register_linear_step_toggle`.
    Suited for "N independent sections, click to toggle each" pages.

    Parameters
    ----------
    step : int
        Number rendered in the badge.
    title : str
        Bold heading text next to the badge.
    body : object
        Body content inside the collapse (form, picker, table, ...).
    collapse_id : str | dict | None
        Collapse id. ``None`` (default) → auto-generated dict id wired by
        :func:`register_linear_step_toggle`. A string → mode A: consumer
        owns the toggle callback. A dict → bring-your-own pattern id.
    summary_id : str | None
        Optional string id for the summary span. If supplied, the
        consumer's state callback writes ``children`` here.
    initial_open : bool
        Whether the collapse starts open. Default False (closed).
    header_type : str
        Dict-id ``type`` field for the clickable header. Pattern-matched
        by :func:`register_linear_step_toggle`. Use a unique value per
        independent step strip (e.g. ``"consultation-section-header"``)
        when a page mounts multiple independent strips.

    Example (mode B — recommended for new code)::

        from aspire_dash.components import (
            linear_step_card_collapse, register_linear_step_toggle,
        )

        layout = html.Div([
            linear_step_card_collapse(
                step=1, title="Demographics",
                summary_id="sec-1-summary",
                initial_open=True,
                body=demographics_form(),
            ),
            linear_step_card_collapse(
                step=2, title="Context",
                body=context_form(),
            ),
            # ... more sections
        ])

        # Wire the click-to-toggle behaviour once after the Dash() instance:
        register_linear_step_toggle(app)
    """
    header_children = [
        html.Span(str(step), className="linear-step-badge capture-step-badge"),
        html.Strong(title, className="linear-step-title capture-step-title"),
    ]
    if summary_id:
        header_children.append(html.Span(
            id=summary_id,
            className="linear-step-summary capture-step-summary",
        ))
    else:
        header_children.append(html.Span(
            className="linear-step-summary capture-step-summary",
        ))
    header_children.append(html.I(
        className="fa-solid fa-chevron-down linear-step-chevron capture-step-chevron",
    ))

    if collapse_id is None:
        resolved_collapse_id = {"type": f"{header_type}-collapse", "step": int(step)}
    else:
        resolved_collapse_id = collapse_id

    return dbc.Card(
        [
            html.Div(
                header_children,
                id={"type": header_type, "step": int(step)},
                className="linear-step-header capture-step-header",
                n_clicks=0,
            ),
            dbc.Collapse(
                dbc.CardBody(body, className="pt-2"),
                id=resolved_collapse_id,
                is_open=bool(initial_open),
            ),
        ],
        className="mb-2 shadow-sm linear-step-card capture-step-card",
    )


def register_linear_step_toggle(app, *, header_type: str = "linear-step-header"):
    """Wire the pattern-matched click-to-toggle callback for a step strip.

    Mode B helper — call exactly once per ``header_type`` after the
    ``Dash()`` instance is created. Flips ``is_open`` on the collapse
    whose dict id matches the clicked header (header
    ``{"type": header_type, "step": N}`` toggles collapse
    ``{"type": header_type + "-collapse", "step": N}``).

    Skip this helper when consumers pass a string ``collapse_id`` to
    :func:`linear_step_card_collapse` — they own the toggle in that mode.

    Parameters
    ----------
    app : dash.Dash
        The app instance.
    header_type : str
        Must match the ``header_type=`` argument passed to
        ``linear_step_card_collapse`` when the cards were built.
    """
    @app.callback(
        Output({"type": f"{header_type}-collapse", "step": MATCH}, "is_open"),
        Input({"type": header_type, "step": MATCH}, "n_clicks"),
        State({"type": f"{header_type}-collapse", "step": MATCH}, "is_open"),
        prevent_initial_call=True,
    )
    def _toggle(_n_clicks, is_open):
        return not is_open


# ── Period / metadata one-line bar — v0.37 ────────────────────────────────

def meta_inline_bar(
    items,
    *,
    notes: str | None = None,
    title: str = "Metadata",
    fluid: bool = False,
):
    """Compact horizontal label:value bar wrapped in a small Card.

    Replaces the ``dbc.Row`` + md-column grids that wrapped a Notes cell
    to a second row even when empty. One row of label:value chips, plus
    an optional second row for ``notes`` when supplied. Promoted from
    aspire-nutrition's diary period-metadata card.

    Parameters
    ----------
    items : list[tuple[str, str | None]]
        ``[(label, value), ...]`` pairs. ``None`` / empty values render
        as a muted em-dash.
    notes : str | None
        Optional second-row free text. The notes row is omitted entirely
        when ``None`` / empty.
    title : str
        Card header text. Defaults to "Metadata".
    fluid : bool
        If True, drop the Card wrapper and just return the inline bar
        (useful when the bar lives inside an existing card body).

    Example::

        meta_inline_bar(
            [
                ("Period",  "4-day"),
                ("Athlete", "Test Athlete"),
                ("MRN",     "12345"),
                ("Sport",   "Athletics"),
                ("Dates",   "2026-05-01 -> 2026-05-04"),
            ],
            notes="First diary after training-camp return.",
            title="Period metadata",
        )
    """
    chips = []
    for label, value in items:
        chips.append(html.Span([
            html.Span(label, className="text-muted small text-uppercase me-1",
                      style={"letterSpacing": "0.4px"}),
            html.Span(str(value) if value else "—",
                      className="fw-semibold me-4",
                      style={"color": ASPIRE["900"]}),
        ]))

    rows = [html.Div(chips, className="d-flex flex-wrap align-items-center")]
    if notes:
        rows.append(html.Div([
            html.Span("NOTES", className="text-muted small text-uppercase me-2"),
            html.Span(notes, className="fw-semibold"),
        ], className="mt-2"))

    if fluid:
        return html.Div(rows)

    return dbc.Card([
        dbc.CardHeader(html.Strong(title)),
        dbc.CardBody(rows, className="py-2"),
    ], className="mb-3 shadow-sm")


# ── Generic history table — v0.37 ─────────────────────────────────────────

def history_table(
    rows,
    *,
    columns,
    summary_chips=None,
    status_column: str | None = None,
    status_palette: dict | None = None,
    empty_message: str = "No records to show.",
):
    """Compact striped table with optional summary chips above and a
    status-badge column driven by row data.

    Genericises aspire-nutrition's ``_render_injury_history`` pattern so
    VALD test history, training-load weeks, attendance logs, supplement
    history, etc. all share the same look + shape.

    Parameters
    ----------
    rows : list[dict]
        One dict per record. Keys reference ``columns[*]["key"]``.
    columns : list[dict]
        Column specs. Each: ``{"key": str, "label": str, "format": fn?}``.
        - ``key`` — dict key on each row.
        - ``label`` — column header.
        - ``format`` — optional callable applied to the cell value before
          rendering (e.g. date formatter). Default: ``str(value) or "—"``.
    summary_chips : list[tuple[str, str, str]] | None
        Optional summary strip above the table. Each tuple is
        ``(value, label, tone)`` where tone ∈ ``{"primary", "muted",
        "success", "warning", "danger"}``.
    status_column : str | None
        Optional column key whose value drives a Bootstrap-coloured
        ``.badge bg-…`` chip via ``status_palette``.
    status_palette : dict | None
        Mapping ``{value: bootstrap_color}`` for the status column. Eg.
        ``{"Available": "success", "Out": "danger", "Modified": "warning"}``.
    empty_message : str
        Shown when ``rows`` is empty.

    Example::

        history_table(
            injuries,
            columns=[
                {"key": "date_of_injury", "label": "Date"},
                {"key": "region",         "label": "Region"},
                {"key": "diagnosis",      "label": "Diagnosis"},
                {"key": "availability",   "label": "Status"},
                {"key": "days_lost",      "label": "Days lost"},
            ],
            summary_chips=[
                (str(len(injuries)),    "injuries",      "primary"),
                (str(total_days_lost),  "days lost",     "muted"),
                (str(currently_out),    "currently out",
                 "danger" if currently_out else "muted"),
            ],
            status_column="availability",
            status_palette={"Available": "success", "Out": "danger",
                             "Modified": "warning"},
        )
    """
    if not rows:
        return html.Div(html.Em(empty_message, className="text-muted small"))

    summary_node = None
    if summary_chips:
        tone_classes = {
            "primary": "fw-semibold me-3",
            "success": "text-success fw-semibold me-3",
            "warning": "text-warning fw-semibold me-3",
            "danger":  "text-danger fw-semibold me-3",
            "muted":   "text-muted me-3",
        }
        chip_spans = []
        for value, label, tone in summary_chips:
            cls = tone_classes.get(tone, tone_classes["muted"])
            style = {"color": ASPIRE["900"]} if tone == "primary" else None
            chip_spans.append(html.Span(
                f"{value} {label}",
                className=cls,
                style=style,
            ))
        summary_node = html.Div(chip_spans, className="mb-2 small")

    status_palette = status_palette or {}

    head = html.Thead(html.Tr([html.Th(c.get("label", c["key"])) for c in columns]))
    body_rows = []
    for row in rows:
        cells = []
        for c in columns:
            key = c["key"]
            value = row.get(key)
            fmt = c.get("format")
            if status_column and key == status_column:
                color = status_palette.get(value, "secondary")
                label = value if value is not None else "—"
                cells.append(html.Td(html.Span(str(label), className=f"badge bg-{color}")))
                continue
            if fmt:
                try:
                    rendered = fmt(value)
                except Exception:
                    rendered = "—" if value is None else str(value)
            else:
                rendered = "—" if value is None else str(value)
            cells.append(html.Td(
                rendered,
                style={"whiteSpace": "nowrap"} if isinstance(value, (int, float)) else None,
            ))
        body_rows.append(html.Tr(cells))

    table = dbc.Table(
        [head, html.Tbody(body_rows)],
        bordered=False, hover=True, striped=True,
        responsive=True, size="sm", className="mb-0",
    )

    children = []
    if summary_node is not None:
        children.append(summary_node)
    children.append(table)
    return html.Div(children)


# ── Ranked dropdown — v0.37 ───────────────────────────────────────────────

def ranked_dropdown(
    *,
    label: str,
    items,
    toggle_color: str = "secondary",
    size: str = "sm",
    empty_label: str = "—",
):
    """Bootstrap ``DropdownMenu`` where each item carries a dict id (for
    pattern-matched callbacks) and renders a bold primary label + an
    optional tone-coloured sublabel beneath.

    Replaces the inline ``outline-light`` chip pattern that suffered
    white-text-on-white-card. Promoted from aspire-nutrition's diary
    "alternates" cell where the user picks a different food match per
    diary row.

    Parameters
    ----------
    label : str
        Dropdown toggle text (e.g. ``"Change (4 alts)"``).
    items : list[dict]
        Each item:
            ``{"label": str, "sublabel": str | None, "tone": str,
               "id_kwargs": dict}``
        - ``label`` — primary line, navy + bold.
        - ``sublabel`` — optional muted line beneath, coloured by ``tone``.
        - ``tone`` — Bootstrap colour token (``"success"`` / ``"warning"`` /
          ``"danger"`` / ``"secondary"`` / ...). Drives the sublabel
          ``text-{tone}`` class.
        - ``id_kwargs`` — dict merged into the item's pattern id. The
          ``type`` key falls back to ``"ranked-dropdown-pick"`` if the
          caller omits it; callers normally pass their own
          (e.g. ``{"type": "diary-pick-alt", "i": 7, "food_id": 42}``).
    toggle_color : str
        Bootstrap colour for the dropdown toggle button.
    size : str
        Bootstrap size (``"sm"`` / ``"md"`` / ``"lg"``).
    empty_label : str
        Rendered (as muted italic) when ``items`` is empty so the
        cell never collapses to zero width.

    Returns ``dbc.DropdownMenu`` when there are items, otherwise an
    ``html.Em`` placeholder.

    Example::

        ranked_dropdown(
            label=f"Change ({len(alts)} alts)",
            items=[
                {
                    "label": alt["name"],
                    "sublabel": f"{strength}  ·  {alt['brand']}",
                    "tone": tone_color,
                    "id_kwargs": {"type": "diary-pick-alt",
                                   "i": row_idx, "food_id": alt["food_id"]},
                }
                for alt, strength, tone_color in ranked
            ],
        )
    """
    if not items:
        return html.Em(empty_label, className="text-muted small")

    menu_items = []
    for it in items:
        item_label = it.get("label") or "—"
        sublabel = it.get("sublabel")
        tone = it.get("tone") or "secondary"
        id_kwargs = dict(it.get("id_kwargs") or {})
        id_kwargs.setdefault("type", "ranked-dropdown-pick")
        children = [html.Div(
            item_label,
            className="fw-semibold",
            style={"color": ASPIRE["900"], "whiteSpace": "normal"},
        )]
        if sublabel:
            children.append(html.Div(sublabel, className=f"small text-{tone}"))
        menu_items.append(dbc.DropdownMenuItem(
            children,
            id=id_kwargs,
            n_clicks=0,
        ))

    return dbc.DropdownMenu(
        label=label,
        children=menu_items,
        size=size,
        color=toggle_color,
        toggleClassName="py-0 px-2",
        style={"fontSize": "0.78rem"},
        in_navbar=False,
    )


# ── Section card (v0.45 — promoted from DASH_Anthro + aspire-supplements) ───

def section_card(title, children, *, icon: str | None = None,
                 badge_text: str | None = None, accent_color: str | None = None,
                 className: str = "", style: dict | None = None):
    """Titled card with a branded section header — the pattern three apps
    (DASH_Anthro, aspire-supplements, aspire-nutrition) each rebuilt.

    Parameters
    ----------
    title : str — uppercase tracked header text.
    children : Dash tree — the card body.
    icon : FontAwesome class (e.g. "fa-solid fa-boxes-stacked"), optional.
    badge_text : small pill rendered after the title, optional.
    accent_color : hex/var() — adds a 4px left stripe so urgency reads at
        a glance (red = low stock, amber = expiring, gold = anchor card).
    """
    head = []
    if icon:
        head.append(html.I(className=f"{icon}",
                           style={"color": ASPIRE["600"], "marginRight": "8px"}))
    head.append(html.Span(title, style={
        "textTransform": "uppercase", "letterSpacing": "1px",
        "fontSize": "12.5px", "fontWeight": "600", "color": ASPIRE["800"],
    }))
    if badge_text:
        head.append(html.Span(badge_text, className="badge", style={
            "marginLeft": "8px", "fontSize": "10px", "fontWeight": "600",
            "padding": "2px 8px", "borderRadius": "999px",
            "background": SLATE["100"], "color": SLATE["600"],
        }))
    base_style = {
        "background": "white", "borderRadius": f"{RADIUS_LG}px",
        "padding": "16px 20px", "boxShadow": SHADOW_SM,
    }
    if accent_color:
        base_style["borderLeft"] = f"4px solid {accent_color}"
    if style:
        base_style.update(style)
    return html.Div([
        html.Div(head, className="section-header", style={
            "display": "flex", "alignItems": "center",
            "borderBottom": f"2px solid {ASPIRE['600']}",
            "paddingBottom": "6px", "marginBottom": "14px",
        }),
        html.Div(children, className="card-body"),
    ], className=f"card section-card {className}".strip(), style=base_style)
