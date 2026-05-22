"""PDF + Excel + Word exports — branded with Aspire chrome.

Lifted from sams-training-dashboard/pdf_report.py and the budget app's
excel download path. The PDF builder is sport-agnostic: pass any
DataFrame + title + period label and you get an A4-landscape PDF with
the Aspire logo header, navy title bar, gold rule under section
headers, and slate-on-white tables matching the brand.

Note: ``pdf_export`` requires ``reportlab``. Add to your app's
``requirements.txt`` if you use it (``aspire_dash`` itself does not
list reportlab as a hard dep — it's an optional extra).
"""
from __future__ import annotations

import io
import os
from datetime import datetime, date
from typing import Iterable

from dash import dcc, html

from .theme import ASPIRE_NAVY, ASPIRE_BLUE, GOLD, SLATE


# ── Excel export button ────────────────────────────────────────────────────

def excel_export_button(
    id: str,
    label: str = "Download Excel",
    icon: str = "fa-solid fa-file-excel",
    color: str | None = None,
):
    """Branded Excel-download button + paired ``dcc.Download``.

    Wires up two components: the button and its download. The button id
    is ``id`` (so ``Input(id, "n_clicks")`` triggers the callback) and
    the download id is ``f"{id}-download"``.

    In your callback, return ``dcc.send_data_frame(df.to_excel, "out.xlsx", index=False)``
    against ``Output(f"{id}-download", "data")``.

    Parameters
    ----------
    id : str
        Component id for the button (e.g. ``"budget-xlsx"``).
    label : str
        Visible button text.
    icon : str
        FontAwesome icon class (defaults to file-excel).
    color : str or None
        Background hex. Defaults to Aspire blue.
    """
    bg = color or ASPIRE_BLUE
    return html.Div([
        html.Button(
            [html.I(className=icon, style={"marginRight": "8px"}), label],
            id=id, n_clicks=0,
            style={
                "padding": "8px 16px", "cursor": "pointer",
                "background": bg, "color": "white",
                "border": "none", "borderRadius": "8px",
                "fontWeight": "600", "fontSize": "13px",
            },
        ),
        dcc.Download(id=f"{id}-download"),
    ], style={"display": "inline-block"})


def pdf_download_button(
    id: str,
    label: str = "Download PDF",
    icon: str = "fa-solid fa-file-pdf",
    color: str | None = None,
):
    """Branded PDF-download button + paired ``dcc.Download``.

    Use this in tandem with ``pdf_export`` in your callback. Same id
    convention as ``excel_export_button``.
    """
    bg = color or ASPIRE_NAVY
    return html.Div([
        html.Button(
            [html.I(className=icon, style={"marginRight": "8px"}), label],
            id=id, n_clicks=0,
            style={
                "padding": "8px 16px", "cursor": "pointer",
                "background": bg, "color": "white",
                "border": "none", "borderRadius": "8px",
                "fontWeight": "600", "fontSize": "13px",
            },
        ),
        dcc.Download(id=f"{id}-download"),
    ], style={"display": "inline-block"})


# ── PDF builder ────────────────────────────────────────────────────────────

DEFAULT_LOGO_PATH = os.path.join(
    os.path.dirname(__file__), "assets", "aspire-logo.png",
)


def pdf_export(
    title: str,
    sections: list[dict],
    period_label: str | None = None,
    meta: dict | None = None,
    *,
    logo_path: str | None = None,
    orientation: str = "landscape",
    footer_text: str | None = None,
) -> bytes:
    """Render a multi-section A4 PDF report with Aspire branding.

    Parameters
    ----------
    title : str
        Big report title at the top.
    sections : list of dict
        Each section is one of::

            {"heading": "Lunch",
             "table": pandas.DataFrame,   # required for a table section
             "totals_row": True,           # add a navy totals row at the bottom
             "highlight": "Athletics"}      # gold highlight on this row label

        or::

            {"heading": "Notes",
             "paragraphs": ["Free-text paragraph 1", "..."]}
    period_label : str or None
        Rendered under the title (e.g. ``"Sun 17 – Sat 23 May 2026"``).
    meta : dict or None
        ``{"Group": "U16 Boys", "Sport": "Athletics"}`` — rendered as a
        comma-separated meta-strip under the period.
    logo_path : str or None
        Override the Aspire logo. Defaults to the packaged ``aspire-logo.png``.
    orientation : "landscape" | "portrait"
        Page orientation.
    footer_text : str or None
        Override the auto-generated footer (defaults to a generated/source
        stamp).

    Returns
    -------
    bytes — PDF byte string suitable for ``dcc.send_bytes``.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image,
    )

    NAVY = colors.HexColor(ASPIRE_NAVY)
    BLUE = colors.HexColor(ASPIRE_BLUE)
    GOLD_C = colors.HexColor(GOLD)
    SLATE_LINE = colors.HexColor(SLATE["200"])
    SLATE_BG = colors.HexColor(SLATE["100"])
    SLATE_TXT = colors.HexColor(SLATE["800"])

    page_size = landscape(A4) if orientation == "landscape" else A4
    usable_w_cm = 27.3 if orientation == "landscape" else 18.0

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=page_size,
        leftMargin=1.2 * cm, rightMargin=1.2 * cm,
        topMargin=1.2 * cm, bottomMargin=1.2 * cm,
        title=title,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=15,
                        textColor=NAVY, spaceAfter=4)
    meta_style = ParagraphStyle("meta", parent=styles["Normal"], fontSize=9,
                                textColor=SLATE_TXT, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11,
                        textColor=NAVY, spaceAfter=3, spaceBefore=8)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10,
                          textColor=SLATE_TXT, spaceAfter=4)
    footer = ParagraphStyle("footer", parent=styles["Normal"], fontSize=7,
                            textColor=colors.HexColor(SLATE["400"]),
                            alignment=2, spaceBefore=6)

    story = []

    # Header row: title left, logo right
    logo = None
    lp = logo_path or DEFAULT_LOGO_PATH
    if os.path.exists(lp):
        logo = Image(lp, width=2.0 * cm, height=2.0 * cm)

    if logo is not None:
        header_tbl = Table([[Paragraph(title, h1), logo]],
                           colWidths=[(usable_w_cm - 2.5) * cm, 2.5 * cm])
        header_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
            ("VALIGN", (1, 0), (1, 0), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(header_tbl)
    else:
        story.append(Paragraph(title, h1))

    # Period + meta line
    if period_label or meta:
        bits = []
        if period_label:
            bits.append(f"<b>Period:</b> {period_label}")
        if meta:
            for k, v in meta.items():
                bits.append(f"<b>{k}:</b> {v}")
        story.append(Paragraph(" &nbsp; &nbsp; ".join(bits), meta_style))

    # Gold rule under the header strip
    rule = Table([[" "]], colWidths=[usable_w_cm * cm], rowHeights=[0.05 * cm])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GOLD_C)]))
    story.append(rule)
    story.append(Spacer(1, 0.3 * cm))

    # Sections
    for section in sections:
        heading = section.get("heading")
        if heading:
            story.append(Paragraph(heading, h2))

        if "paragraphs" in section:
            for p in section["paragraphs"]:
                story.append(Paragraph(str(p), body))
            story.append(Spacer(1, 0.3 * cm))
            continue

        df = section.get("table")
        if df is None or len(df) == 0:
            story.append(Paragraph("<i>No data.</i>", body))
            story.append(Spacer(1, 0.3 * cm))
            continue

        columns = [str(c) for c in df.columns]
        rows = [columns]
        for _, r in df.iterrows():
            rows.append([
                ("" if v is None else str(v)) for v in r.tolist()
            ])
        totals_row = None
        if section.get("totals_row"):
            totals = ["Total"]
            for col in columns[1:]:
                try:
                    totals.append(str(int(df[col].sum())))
                except Exception:
                    totals.append("")
            totals_row = totals
            rows.append(totals)

        n_cols = len(columns)
        first_w = 3.8 * cm if n_cols > 4 else 5.0 * cm
        rest_w = (usable_w_cm * cm - first_w) / max(1, n_cols - 1)
        col_widths = [first_w] + [rest_w] * (n_cols - 1)

        tbl = Table(rows, colWidths=col_widths, repeatRows=1)
        style = TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.3, SLATE_LINE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2 if totals_row else -1),
             [SLATE_BG, colors.white]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (0, -1), 8),
        ])
        if totals_row:
            style.add("BACKGROUND", (0, -1), (-1, -1), NAVY)
            style.add("TEXTCOLOR", (0, -1), (-1, -1), colors.white)
            style.add("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold")
            style.add("LINEABOVE", (0, -1), (-1, -1), 0.8, NAVY)
        # Highlight specific first-column value
        highlight = section.get("highlight")
        if highlight:
            for i, row in enumerate(rows[1:], start=1):
                if row and row[0] == highlight and row is not totals_row:
                    style.add("BACKGROUND", (0, i), (-1, i),
                              colors.HexColor("#fff8e1"))
        tbl.setStyle(style)
        story.append(tbl)
        story.append(Spacer(1, 0.4 * cm))

    # Footer
    ftxt = footer_text or (
        f"Generated {datetime.now().strftime('%d %b %Y %H:%M')} · "
        f"Aspire Academy"
    )
    story.append(Paragraph(ftxt, footer))

    doc.build(story)
    return buf.getvalue()


def send_pdf(pdf_bytes: bytes, filename: str):
    """Wrap ``pdf_export`` output for ``dcc.Download.data``.

    Example::

        @callback(Output("budget-pdf-download", "data"),
                  Input("budget-pdf", "n_clicks"),
                  prevent_initial_call=True)
        def _dl(_n):
            pdf = pdf_export("Budget FY2026", sections=[...])
            return send_pdf(pdf, "budget_fy2026.pdf")
    """
    return dcc.send_bytes(pdf_bytes, filename)
