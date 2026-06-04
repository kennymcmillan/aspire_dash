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
             "highlight": "Athletics",      # gold highlight on this row label
             "emphasize_last_col": True}    # bold navy last column (e.g. "Result")

        or::

            {"heading": "Notes",
             "paragraphs": ["Free-text paragraph 1", "..."]}

        or a **KPI band** (a row of metric cards, navy left-rule)::

            {"kpis": [{"label": "Body Mass", "value": "72.4",
                       "unit": "kg", "sub": "Stature 181 cm"}, ...]}

        or a **callout / insight box** (tinted, blue left-border)::

            {"callout": {"label": "Key Insights",
                         "items": ["BMI 22.1 — healthy range", "..."]}}

        or **side-by-side** sections (two tables across the page width)::

            {"columns": [{"heading": "Snapshot", "table": df_a},
                         {"heading": "Bilateral", "table": df_b}]}
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
    from reportlab.pdfgen import canvas as _rl_canvas
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image,
    )

    NAVY = colors.HexColor(ASPIRE_NAVY)
    BLUE = colors.HexColor(ASPIRE_BLUE)
    GOLD_C = colors.HexColor(GOLD)
    SLATE_LINE = colors.HexColor(SLATE["200"])
    SLATE_BG = colors.HexColor(SLATE["100"])
    SLATE_TXT = colors.HexColor(SLATE["800"])
    SLATE_MUTED = colors.HexColor(SLATE["400"])
    GREEN = colors.HexColor("#059669")

    page_size = landscape(A4) if orientation == "landscape" else A4
    usable_w_cm = 27.3 if orientation == "landscape" else 18.0

    ftxt = footer_text or (
        f"Generated {datetime.now().strftime('%d %b %Y %H:%M')} · Aspire Academy"
    )

    # Page-numbered canvas — draws a gold rule + footer text + "Page X of Y" on
    # EVERY page (two-pass so the total is known). This is the headline polish
    # that lifts the report from "a stack of tables" to a finished document.
    class _NumberedCanvas(_rl_canvas.Canvas):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._saved = []

        def showPage(self):
            self._saved.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved)
            for state in self._saved:
                self.__dict__.update(state)
                self._draw_footer(total)
                super().showPage()
            super().save()

        def _draw_footer(self, total):
            w, _h = page_size
            self.saveState()
            self.setStrokeColor(GOLD_C)
            self.setLineWidth(0.6)
            self.line(1.2 * cm, 1.0 * cm, w - 1.2 * cm, 1.0 * cm)
            self.setFont("Helvetica", 7)
            self.setFillColor(SLATE_MUTED)
            self.drawString(1.2 * cm, 0.65 * cm, ftxt)
            self.drawRightString(w - 1.2 * cm, 0.65 * cm,
                                 f"Page {self._pageNumber} of {total}")
            self.restoreState()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=page_size,
        leftMargin=1.2 * cm, rightMargin=1.2 * cm,
        topMargin=1.2 * cm, bottomMargin=1.5 * cm,
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
    kpi_label_st = ParagraphStyle("kpi_label", parent=styles["Normal"],
                                  fontSize=6.8, textColor=colors.HexColor(SLATE["500"]),
                                  fontName="Helvetica-Bold", leading=8)
    kpi_value_st = ParagraphStyle("kpi_value", parent=styles["Normal"],
                                  fontSize=15, textColor=NAVY,
                                  fontName="Helvetica-Bold", leading=17)
    kpi_sub_st = ParagraphStyle("kpi_sub", parent=styles["Normal"], fontSize=6.8,
                                textColor=colors.HexColor(SLATE["500"]), leading=8)
    callout_label_st = ParagraphStyle("co_label", parent=styles["Normal"],
                                      fontSize=7.5, fontName="Helvetica-Bold",
                                      textColor=colors.HexColor("#1e40af"), leading=10)
    callout_item_st = ParagraphStyle("co_item", parent=styles["Normal"], fontSize=9,
                                     textColor=SLATE_TXT, leading=12, leftIndent=8)
    # Cell styles — cells are Paragraphs so long values (Arabic names, somatotype
    # strings, long event labels) WRAP within the column instead of clipping.
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from xml.sax.saxutils import escape as _xesc
    cell_l = ParagraphStyle("cl", parent=styles["Normal"], fontSize=8.5, leading=10.5,
                            textColor=SLATE_TXT, alignment=TA_LEFT)
    cell_lb = ParagraphStyle("clb", parent=cell_l, fontName="Helvetica-Bold")
    cell_c = ParagraphStyle("cc", parent=cell_l, alignment=TA_CENTER)
    cell_emph = ParagraphStyle("ce", parent=cell_c, fontName="Helvetica-Bold",
                               textColor=GREEN)
    cell_th = ParagraphStyle("cth", parent=cell_c, fontName="Helvetica-Bold",
                             textColor=colors.white, fontSize=8)
    cell_tot = ParagraphStyle("ct", parent=cell_c, fontName="Helvetica-Bold",
                              textColor=colors.white)

    def _cell(v, st):
        return Paragraph(_xesc("" if v is None else str(v)), st)

    # ── section flowable builders ──────────────────────────────────────────
    def _table_flowable(section, avail_cm):
        df = section.get("table")
        if df is None or len(df) == 0:
            return Paragraph("<i>No data.</i>", body)
        columns = [str(c) for c in df.columns]
        n_cols = len(columns)
        emph = bool(section.get("emphasize_last_col")) and n_cols > 1
        raw_values = [r.tolist() for _, r in df.iterrows()]
        highlight = section.get("highlight")

        # Header row (Paragraphs → wraps; white bold on the blue band)
        rows = [[_cell(c, cell_th) for c in columns]]
        highlight_idx = []
        for ri, vals in enumerate(raw_values, start=1):
            cells = []
            for ci, v in enumerate(vals):
                if ci == 0:
                    cells.append(_cell(v, cell_lb))
                elif emph and ci == n_cols - 1:
                    cells.append(_cell(v, cell_emph))
                else:
                    cells.append(_cell(v, cell_c))
            rows.append(cells)
            if highlight is not None and vals and str(vals[0]) == str(highlight):
                highlight_idx.append(ri)

        totals_row = None
        if section.get("totals_row"):
            totals = ["Total"]
            for col in columns[1:]:
                try:
                    totals.append(str(int(df[col].sum())))
                except Exception:
                    totals.append("")
            totals_row = totals
            rows.append([_cell(v, cell_tot) for v in totals])

        first_w = (3.4 if n_cols > 4 else 4.6) * cm
        first_w = min(first_w, avail_cm * cm * 0.42)
        rest_w = (avail_cm * cm - first_w) / max(1, n_cols - 1)
        col_widths = [first_w] + [rest_w] * (n_cols - 1)

        tbl = Table(rows, colWidths=col_widths, repeatRows=1)
        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("LINEBELOW", (0, 0), (-1, 0), 1.2, GOLD_C),   # gold rule under header
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
            style.add("LINEABOVE", (0, -1), (-1, -1), 0.8, NAVY)
        for ri in highlight_idx:
            style.add("BACKGROUND", (0, ri), (-1, ri), colors.HexColor("#fff8e1"))
        tbl.setStyle(style)
        return tbl

    def _section_flowables(section, avail_cm):
        out = []
        if section.get("heading"):
            out.append(Paragraph(section["heading"], h2))
        if "paragraphs" in section:
            out += [Paragraph(str(p), body) for p in section["paragraphs"]]
        else:
            out.append(_table_flowable(section, avail_cm))
        return out

    def _kpi_band(items):
        cells, n = [], len(items)
        for it in items:
            unit = (f" <font size=8 color='{SLATE['400']}'>{it['unit']}</font>"
                    if it.get("unit") else "")
            stack = [Paragraph(str(it.get("label", "")).upper(), kpi_label_st),
                     Paragraph(f"{it.get('value', '')}{unit}", kpi_value_st)]
            if it.get("sub"):
                stack.append(Paragraph(str(it["sub"]), kpi_sub_st))
            cells.append(stack)
        col_w = usable_w_cm * cm / max(1, n)
        tbl = Table([cells], colWidths=[col_w] * n)
        st = TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.4, SLATE_LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.white),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
        for i in range(n):                       # navy left-rule per card
            st.add("LINEBEFORE", (i, 0), (i, 0), 2.2, NAVY)
        tbl.setStyle(st)
        return tbl

    def _callout(c):
        label = c.get("label", "Insights") if isinstance(c, dict) else "Insights"
        items = c.get("items", []) if isinstance(c, dict) else list(c)
        inner = [Paragraph(label.upper(), callout_label_st)]
        inner += [Paragraph(f"•&nbsp; {i}", callout_item_st) for i in items]
        tbl = Table([[inner]], colWidths=[usable_w_cm * cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
            ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#3b82f6")),
            ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#dbeafe")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ]))
        return tbl

    story = []

    # Header row: title + period/meta left, logo right
    head_left = [Paragraph(title, h1)]
    if period_label or meta:
        bits = []
        if period_label:
            bits.append(f"<b>Period:</b> {period_label}")
        if meta:
            for k, v in meta.items():
                bits.append(f"<b>{k}:</b> {v}")
        head_left.append(Paragraph(" &nbsp; &nbsp; ".join(bits), meta_style))

    logo = None
    lp = logo_path or DEFAULT_LOGO_PATH
    if os.path.exists(lp):
        logo = Image(lp, width=2.0 * cm, height=2.0 * cm)
    if logo is not None:
        header_tbl = Table([[head_left, logo]],
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
        story += head_left

    # Gold rule under the header strip
    rule = Table([[" "]], colWidths=[usable_w_cm * cm], rowHeights=[0.06 * cm])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GOLD_C)]))
    story.append(rule)
    story.append(Spacer(1, 0.3 * cm))

    # Sections
    for section in sections:
        if "kpis" in section:
            if section.get("heading"):
                story.append(Paragraph(section["heading"], h2))
            story.append(_kpi_band(section["kpis"]))
            story.append(Spacer(1, 0.35 * cm))
            continue
        if "callout" in section:
            if section.get("heading"):
                story.append(Paragraph(section["heading"], h2))
            story.append(_callout(section["callout"]))
            story.append(Spacer(1, 0.35 * cm))
            continue
        if "columns" in section:
            subs = section["columns"]
            col_cm = (usable_w_cm - 0.6) / max(1, len(subs))
            cells = [_section_flowables(s, col_cm) for s in subs]
            grid = Table([cells], colWidths=[(col_cm + 0.6 / len(subs)) * cm] * len(subs))
            grid.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
            ]))
            story.append(grid)
            story.append(Spacer(1, 0.4 * cm))
            continue
        # plain table / paragraphs section
        for fl in _section_flowables(section, usable_w_cm):
            story.append(fl)
        story.append(Spacer(1, 0.4 * cm))

    doc.build(story, canvasmaker=_NumberedCanvas)
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
