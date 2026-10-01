"""Page sections that save vertical space (v0.100, the app-quality kit).

Promoted from the AG2026 showcase app (``pages/_common.py`` there), made generic:

    section_tabs   a sticky, keyboard-reachable tab row for a page's sections
    fold           a collapsible section (html.Details), closed by default
    page_head      the page's title + one-line lead; with ``setup_app(quality=True)``
                   it moves into the sticky top bar and the in-page copy is
                   visually hidden (kept for screen readers)

Styling and behaviour ship as assets copied by ``setup_app()``:
``05_aspire_quality.css``, ``aspire_section_tabs.js``, ``aspire_quality.js``.
``section_tabs`` and ``fold`` work in ANY app (their CSS/JS only match the
``aspire-section-tabs`` / ``aspire-fold`` classes they render). The page-title,
accessibility and compact-spacing rules only switch on under the opt-in
``aspire-quality`` class (``setup_app(app, quality=True)``).
"""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html

__all__ = ["section_tabs", "fold", "page_head"]


def _tab(item):
    label, key, children = item[:3]
    icon = item[3] if len(item) > 3 else None
    if icon:
        return dbc.Tab(children, label=label, tab_id=key,
                       label_class_name="aspire-section-tab aspire-section-tab--icon",
                       label_style={"--aspire-tab-icon": f"url('{icon}')"})
    return dbc.Tab(children, label=label, tab_id=key, label_class_name="aspire-section-tab")


def section_tabs(tab_id: str, items, active: str | None = None, sub: bool = False):
    """Section tabs inside a page: cuts scrolling on long pages.

    Parameters
    ----------
    tab_id : str
        Component id of the ``dbc.Tabs`` (read ``active_tab`` in callbacks, e.g. to
        render a heavy pane only when its tab opens).
    items : list of tuples
        ``(label, key, children[, icon_url])``. Every pane is rendered up front, so
        callbacks and exports inside hidden panes keep working. An item whose
        children is ``None`` is skipped. ``icon_url`` (optional, may be ``None``)
        is an SVG/PNG drawn before the label in the tab's text colour (CSS mask);
        pass it through ``dash.get_relative_path()`` so it resolves on Connect.
    active : str or None
        Key of the tab open on load (default: the first item). Make it the thing
        the reader came for.
    sub : bool
        ``True`` renders a pill sub-tab row, a level below a main row. Use it only
        inside a tab that is itself long. It sticks directly under the main row.

    Behaviour (``assets/aspire_section_tabs.js`` + ``05_aspire_quality.css``):
    the row sticks under the top bar while its section scrolls (soft shadow once
    stuck), sub rows stack under it, arrows/Home/End/Enter/Space work (roving
    tabindex), Plotly charts redraw at the right width on switch, and on phones
    the row wraps instead of hiding tabs off-screen.
    """
    kept = [i for i in items if i[2] is not None]
    if not kept:
        return html.Div()
    cls = "aspire-section-tabs aspire-section-tabs--sub" if sub else "aspire-section-tabs aspire-section-tabs--main"
    return dbc.Tabs([_tab(i) for i in kept], id=tab_id,
                    active_tab=active or kept[0][1], className=cls)


def fold(title, children, open: bool = False, icon: str | None = None):  # noqa: A002 (html attribute)
    """A collapsible section: the title stays visible, the body opens on click,
    Enter or Space (native ``<details>``). Use for secondary or explanatory blocks.

    ``icon`` is an optional Font Awesome class (``"fa-solid fa-circle-info"``).
    """
    head = [html.I(className=f"{icon} aspire-fold__icon", **{"aria-hidden": "true"})] if icon else []
    return html.Details(
        [html.Summary(head + [html.Span(title, className="aspire-fold__title")], className="aspire-fold__summary"),
         html.Div(children, className="aspire-fold__body")],
        open=open, className="aspire-fold",
    )


def page_head(title: str, lead: str | None = None, right=None):
    """The page's heading block: an ``h1``, an optional one-line lead, and an
    optional right-hand slot (export buttons).

    Without the opt-in it renders as a normal visible heading. Under
    ``setup_app(app, quality=True)`` the title and lead are copied into the
    sticky header (``#aspire-page-title`` / ``#aspire-page-subtitle``) and the
    in-page copy is visually hidden but kept in the DOM for screen readers;
    ``right`` stays at the top right of the page.
    """
    text = html.Div([html.H1(title, className="aspire-page-head__title"),
                     html.P(lead, className="aspire-page-head__lead") if lead else None],
                    className="aspire-page-head__text")
    return html.Div([text] + ([html.Div(right, className="aspire-page-head__right")] if right is not None else []),
                    className="aspire-page-head")
