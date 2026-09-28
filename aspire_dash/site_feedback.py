"""Site feedback for every Aspire Dash app (v0.96, promoted from medical-dashboard).

A floating "Feedback" button on every page opens a drawer with the CURRENT page already picked, an
optional category, a comment box and Save: open, type, Save. The /feedback page is the triage grid:
filter by status, and triage users set Open / In progress / Done / Won't do per request (one change
saves exactly that request). Admins can switch the grid to "All apps": every app's requests in one
place (aspire_data.feedback.read_all_feedback).

Storage is aspire_data.feedback.FeedbackStore (one Connect pin per app). This module is UI only and
takes any object with the same methods (load / add / set_status / pending / last_error / app).

    from aspire_data.feedback import FeedbackStore, read_all_feedback
    from aspire_dash.components import fly_toast, register_fly_toast
    from aspire_dash.site_feedback import (register_site_feedback, site_feedback_button,
                                           site_feedback_page)

    register_site_feedback(FeedbackStore("medical-dashboard"), inbox=read_all_feedback,
                           extra_pages=["Ask Medical"], notice="No athlete medical details.",
                           toast_trigger="fly-toast-trigger")
    app.layout = html.Div([..., fly_toast(), site_feedback_button()])   # once, in the shell
    # pages/feedback.py:
    dash.register_page(__name__, path="/feedback", name="Site feedback")
    def layout(**_): return site_feedback_page()

Triage users: ``can_triage(viewer) -> bool``; default = env ADMIN_USERS (comma-separated Connect
usernames / emails, case-insensitive), and everyone off Connect (local development).

Dash lessons baked in (each cost a bug once):
- every click callback checks for a REAL click (a component appearing fires with n_clicks 0);
- for an ALL pattern input Dash marks EVERY component as triggered, so the status callback diffs
  all values against the store and saves only the one that changed; several changes = a stale page,
  save nothing (so an old tab cannot undo someone else's status);
- the grid is never re-rendered inside its own change event (crashed the renderer, 2026-09-23).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

import dash
from dash import ALL, Input, Output, State, clientside_callback, dcc, html, no_update

__all__ = ["register_site_feedback", "site_feedback_button", "site_feedback_page", "connect_viewer",
           "page_for_path", "STATUSES"]

STATUSES = ("Open", "In progress", "Done", "Won't do")
_SLUG = {"Open": "open", "In progress": "in", "Done": "done", "Won't do": "wont"}   # CSS class per status
_CFG: dict = {}
_REGISTERED = {"done": False}


# ── identity + config ──────────────────────────────────────────────────────────────────────────
def connect_viewer() -> str:
    """The signed-in Connect user (RStudio-Connect-Credentials header); '' locally / outside a request."""
    try:
        from flask import request
        return json.loads(request.headers.get("RStudio-Connect-Credentials", "{}")).get("user", "") or ""
    except Exception:  # noqa: BLE001
        return ""


def _on_connect() -> bool:
    return os.environ.get("RSTUDIO_PRODUCT") == "CONNECT" or bool(os.environ.get("CONNECT_CONTENT_GUID"))


def default_can_triage(viewer: str) -> bool:
    """ADMIN_USERS (bare username or email, case-insensitive); everyone locally."""
    if not _on_connect():
        return True
    v = (viewer or "").strip().lower()
    if not v:
        return False
    admins = {a.strip().lower() for a in os.environ.get("ADMIN_USERS", "").split(",") if a.strip()}
    return v in admins or v.split("@")[0] in {a.split("@")[0] for a in admins}


def _can_triage() -> bool:
    return bool(_CFG.get("can_triage", default_can_triage)(connect_viewer()))


def page_for_path(pathname: str | None) -> str:
    """The registered page name for a URL path (Connect prefix stripped); 'Whole site' if none."""
    try:
        rel = dash.strip_relative_path(pathname or "/") or ""
    except Exception:  # noqa: BLE001  outside an app context
        rel = (pathname or "/").strip("/")
    for p in dash.page_registry.values():
        if (p.get("path") or "").strip("/") == rel:
            return p.get("name") or "Whole site"
    return "Whole site"


def _rel(href: str) -> str:
    """href under the Connect path prefix (bare href outside a running app)."""
    try:
        return dash.get_relative_path(href)
    except Exception:  # noqa: BLE001
        return href


def _page_options() -> list[str]:
    names = [p.get("name") for p in dash.page_registry.values() if p.get("name")]
    return list(dict.fromkeys([*names, *_CFG.get("extra_pages", ()), "Whole site"]))


def _toast(header: str, msg: str, icon: str):
    if not _CFG.get("toast_trigger"):
        return no_update
    from aspire_dash.components import dispatch_fly_toast
    return dispatch_fly_toast(header, msg, icon)


def _when(stamp_utc: str) -> str:
    """'2026-09-28 05:21' (UTC) -> '28-Sep-2026 08:21' (Qatar, dd-Mmm-yyyy display rule)."""
    try:
        return (datetime.strptime(stamp_utc, "%Y-%m-%d %H:%M") + timedelta(hours=3)).strftime("%d-%b-%Y %H:%M")
    except (TypeError, ValueError):
        return stamp_utc or ""


# ── layout pieces ──────────────────────────────────────────────────────────────────────────────
def site_feedback_button(label: str = "Feedback") -> html.Div:
    """The floating button + drawer. Mount ONCE in the app shell (after register_site_feedback)."""
    return html.Div([
        dcc.Location(id="sfb-url", refresh=False),
        html.Button([html.I(className="fa-solid fa-comment-dots"), html.Span(label)], id="sfb-open",
                    n_clicks=0, className="sfb-fab", title="Suggest a change to this page"),
        html.Div([
            html.Div([html.Span("Suggest a change", className="sfb-title"),
                      html.Button("Close", id="sfb-close", n_clicks=0, className="sfb-close")],
                     className="sfb-head"),
            html.Label("Page", className="sfb-label", htmlFor="sfb-page"),
            dcc.Dropdown(id="sfb-page", clearable=False, className="sfb-page"),
            dcc.RadioItems(id="sfb-cat", inline=True, className="sfb-cats", inputClassName="sfb-cat-input"),
            dcc.Textarea(id="sfb-note", placeholder="What should change?", className="sfb-note"),
            html.Div(id="sfb-notice", className="sfb-notice"),
            html.Div(id="sfb-msg", className="sfb-msg", role="status"),
            html.Div([
                html.Button("Save", id="sfb-save", n_clicks=0, className="sfb-save"),
                dcc.Link("See all requests", id="sfb-all", href="/feedback", className="sfb-all"),
            ], className="sfb-actions"),
        ], id="sfb-drawer", className="sfb-drawer", role="dialog", **{"aria-label": "Site feedback"}),
    ], className="sfb-root")


def site_feedback_page(title: str = "Site feedback") -> html.Div:
    """The triage grid for a registered page (call inside the page's layout function)."""
    inbox = bool(_CFG.get("inbox")) and _can_triage()
    return html.Div([
        html.H2(title, className="sfb-page-title"),
        html.Div("Every request stays here. Use the Feedback button on any page to add one."
                 + (" Set the status as work moves." if _can_triage() else ""), className="sfb-page-hint"),
        html.Div([
            dcc.RadioItems(id="sfb-filter", options=["Open", "In progress", "Done", "Won't do", "All"],
                           value="Open", inline=True, className="sfb-filter", inputClassName="sfb-filter-input"),
            dcc.RadioItems(id="sfb-scope", options=["This app", "All apps"], value="This app", inline=True,
                           className="sfb-filter", inputClassName="sfb-filter-input",
                           style=None if inbox else {"display": "none"}),
            html.Span(id="sfb-count", className="sfb-count"),
        ], className="sfb-toolbar"),
        html.Div(id="sfb-list", className="sfb-list"),
    ], className="sfb-page-wrap")


def _count(df) -> str:
    n = {s: int((df["status"] == s).sum()) for s in STATUSES} if not df.empty else dict.fromkeys(STATUSES, 0)
    txt = f"{n['Open']} open · {n['In progress']} in progress · {n['Done']} done · {len(df)} total"
    store = _CFG.get("store")
    if store is not None and getattr(store, "pending", lambda: 0)():
        txt += " · saving…"
    if store is not None and getattr(store, "last_error", ""):
        txt += " · last save failed, will retry with the next change"
    return txt


def _rows(df, which: str, scope: str):
    view = df if which == "All" else df[df["status"] == which]
    if view.empty:
        return html.Div(f"No {'' if which == 'All' else which.lower() + ' '}requests.", className="sfb-empty")
    edit = _can_triage() and scope == "This app"
    show_app = scope == "All apps"
    head = html.Tr([html.Th("Status"), *([html.Th("App")] if show_app else []), html.Th("Page"),
                    html.Th("Request"), html.Th("Added")])
    body = []
    for _, r in view.iterrows():
        status = dcc.Dropdown(id={"type": "sfb-status", "id": r["id"]}, options=list(STATUSES),
                              value=r["status"], clearable=False, searchable=False, className="sfb-status-dd") \
            if edit else html.Span(r["status"], className=f"sfb-chip sfb-chip--{_SLUG.get(r['status'], 'open')}")
        body.append(html.Tr([
            html.Td(status, className="sfb-td-status"),
            *([html.Td(r["app"], className="sfb-td-app")] if show_app else []),
            html.Td(r["page"] or "Whole site", className="sfb-td-page"),
            html.Td([html.Span(r["category"], className="sfb-tag") if r["category"] else None, r["note"]],
                    className="sfb-td-note"),
            html.Td([_when(r["created_utc"]), html.Div(r["by"], className="sfb-meta")], className="sfb-td-when"),
        ], className=f"sfb-row--{_SLUG.get(r['status'], 'open')}"))
    return html.Div(html.Table([html.Thead(head), html.Tbody(body)], className="sfb-table"), className="sfb-table-wrap")


# ── wiring ─────────────────────────────────────────────────────────────────────────────────────
def register_site_feedback(store, *, extra_pages=(), categories=("Bug", "Idea", "Data wrong"),
                           can_triage=None, notice: str = "", toast_trigger: str | None = "fly-toast-trigger",
                           feedback_href: str = "/feedback", inbox=None) -> None:
    """Configure + register the callbacks (once per process; calling again only updates the config)."""
    _CFG.update(store=store, extra_pages=tuple(extra_pages), categories=tuple(categories),
                can_triage=can_triage or default_can_triage, notice=notice, toast_trigger=toast_trigger,
                feedback_href=feedback_href, inbox=inbox)
    if _REGISTERED["done"]:
        return
    _REGISTERED["done"] = True

    clientside_callback(
        """function(o, c) {
            var t = (window.dash_clientside.callback_context.triggered[0] || {}).prop_id || "";
            if (t.indexOf("sfb-open") === 0 && o) { return "sfb-drawer sfb-drawer--open"; }
            if (t.indexOf("sfb-close") === 0 && c) { return "sfb-drawer"; }
            return window.dash_clientside.no_update;
        }""",
        Output("sfb-drawer", "className"), Input("sfb-open", "n_clicks"), Input("sfb-close", "n_clicks"),
        prevent_initial_call=True)

    outs = [Output("sfb-page", "options"), Output("sfb-page", "value"), Output("sfb-cat", "options"),
            Output("sfb-notice", "children"), Output("sfb-all", "href"), Output("sfb-msg", "children")]
    dash.callback(*outs, Input("sfb-open", "n_clicks"), State("sfb-url", "pathname"),
                  prevent_initial_call=True)(_open)
    save_outs = [Output("sfb-note", "value"), Output("sfb-drawer", "className", allow_duplicate=True),
                 Output("sfb-msg", "children", allow_duplicate=True)]
    if toast_trigger:
        save_outs.append(Output(toast_trigger, "data", allow_duplicate=True))
    dash.callback(*save_outs, Input("sfb-save", "n_clicks"), State("sfb-page", "value"),
                  State("sfb-cat", "value"), State("sfb-note", "value"), State("sfb-url", "pathname"),
                  prevent_initial_call=True)(_save)
    dash.callback(Output("sfb-list", "children"), Output("sfb-count", "children"),
                  Input("sfb-filter", "value"), Input("sfb-scope", "value"))(_render)
    status_outs = [Output("sfb-count", "children", allow_duplicate=True)]
    if toast_trigger:
        status_outs.append(Output(toast_trigger, "data", allow_duplicate=True))
    dash.callback(*status_outs, Input({"type": "sfb-status", "id": ALL}, "value"),
                  prevent_initial_call=True)(_status)


def _open(n, pathname):
    if not n:
        return (no_update,) * 6
    return (_page_options(), page_for_path(pathname), list(_CFG.get("categories", ())),
            _CFG.get("notice", ""), _rel(_CFG.get("feedback_href", "/feedback")), "")


def _save(n, page, category, note, pathname):
    extra = (no_update,) if _CFG.get("toast_trigger") else ()
    if not n:
        return (no_update, no_update, no_update, *extra)
    if not (note or "").strip():
        return (no_update, no_update, "Write what should change first.", *extra)
    try:
        path = dash.strip_relative_path(pathname or "/") or ""
    except Exception:  # noqa: BLE001
        path = (pathname or "").strip("/")
    try:
        _CFG["store"].add(page or page_for_path(pathname), note, by=connect_viewer(), category=category or "",
                          page_path="/" + path)
    except Exception as e:  # noqa: BLE001  never break the page over feedback storage
        return (no_update, no_update, f"Could not save ({type(e).__name__}). Please try again.", *extra)
    toast = (_toast("Thanks, saved", f"Your request for {page or 'this page'} is in the list.", "success"),) \
        if extra else ()
    return ("", "sfb-drawer", "" if extra else "Saved. Thank you.", *toast)


def _render(which, scope):
    try:
        if scope == "All apps" and _CFG.get("inbox") and _can_triage():
            df = _CFG["inbox"]()
        else:
            scope = "This app"
            df = _CFG["store"].load()
        return _rows(df, which or "Open", scope), _count(df)
    except Exception as e:  # noqa: BLE001
        return html.Div(f"Could not load requests ({type(e).__name__}).", className="sfb-empty"), ""


def _status(_values):
    extra = (no_update,) if _CFG.get("toast_trigger") else ()
    store = _CFG["store"]
    boxes = (dash.ctx.inputs_list or [[]])[0]
    current = dict(zip(*[store.load()[c] for c in ("id", "status")]))
    diffs = [(b["id"]["id"], b.get("value")) for b in boxes
             if isinstance(b.get("id"), dict) and b["id"].get("id") in current
             and b.get("value") in STATUSES and b.get("value") != current[b["id"]["id"]]]
    if not diffs:
        return (no_update, *extra)
    if not _can_triage():
        return (no_update, *((_toast("Not allowed", "Only admins can change a status.", "danger"),) if extra else ()))
    if len(diffs) > 1:
        return (no_update, *((_toast("Page out of date", "Requests changed elsewhere. Refresh, then try again.",
                                     "warning"),) if extra else ()))
    rid, status = diffs[0]
    store.set_status(rid, status, by=connect_viewer())
    return (_count(store.load()), *((_toast("Status saved", f"Marked {status}.", "success"),) if extra else ()))
