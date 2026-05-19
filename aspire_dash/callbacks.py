"""Reusable Dash callback registrators.

Each function takes the Dash `app` instance and registers a callback
that wires a common Aspire pattern. The goal: skip the
mostly-identical 30-line callback every app re-implements.

PUBLIC API
==========

    register_period_filter(app, store_id, period_select_id,
                           start_input_id, end_input_id,
                           today=None)

        Period-select dropdown → resolve start/end dates → write to a
        Store + sync two date pickers. Supports presets: today,
        last_7, last_30, last_90, ytd, last_12m, custom.

    register_toast(app, toast_id, store_id="toast-trigger")

        Listens to a dcc.Store whose data is a dict {header, msg,
        icon} and flips the toast open with those values. Other
        callbacks call `dispatch_toast(header, msg, icon)` to fire.

    dispatch_toast(header, msg, icon="primary") -> dict

        Build the dict payload for a toast trigger.

    register_pdf_download(app, button_id, download_id, fetcher)

        button click → call `fetcher()` → returns (bytes, filename)
        → dcc.Download fires. Caller supplies the API call.

    register_url_active_nav(app, nav_items, url_id="url")

        Class-toggle the active sidebar/topnav link based on URL
        pathname. Already provided for topnav as register_topnav_active;
        this is the generic sidebar variant.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Callable

import dash
from dash import Input, Output, State

log = logging.getLogger("aspire_dash.callbacks")


# ---------- Period filter ----------

PERIOD_PRESETS = {
    "today":      ("Today",            lambda t: (t, t)),
    "yesterday":  ("Yesterday",        lambda t: (t - timedelta(days=1), t - timedelta(days=1))),
    "last_7":     ("Last 7 days",      lambda t: (t - timedelta(days=6),  t)),
    "last_30":    ("Last 30 days",     lambda t: (t - timedelta(days=29), t)),
    "last_90":    ("Last 90 days",     lambda t: (t - timedelta(days=89), t)),
    "this_month": ("This month",       lambda t: (t.replace(day=1), t)),
    "ytd":        ("Year to date",     lambda t: (date(t.year, 1, 1), t)),
    "last_12m":   ("Last 12 months",   lambda t: (t.replace(year=t.year - 1) if t.month < 12 else date(t.year, 1, 1), t)),
    "all_time":   ("All time",         lambda t: (date(2000, 1, 1), t)),
    "custom":     ("Custom range",     None),
}


def period_preset_options() -> list[dict]:
    """Convenience: dropdown options for the period select."""
    return [{"label": label, "value": key}
            for key, (label, _) in PERIOD_PRESETS.items()]


def resolve_period(preset: str, today: date | None = None) -> tuple[date | None, date | None]:
    """Resolve a preset key to (start, end). Returns (None, None) for
    'custom' so the caller knows to read the date pickers directly."""
    today = today or date.today()
    spec = PERIOD_PRESETS.get(preset)
    if not spec or spec[1] is None:
        return None, None
    return spec[1](today)


def register_period_filter(
    app,
    *,
    store_id: str,
    period_select_id: str,
    start_input_id: str,
    end_input_id: str,
):
    """When the preset dropdown changes, resolve to (start, end) and
    write that into the store + sync the two date pickers."""

    @app.callback(
        Output(store_id, "data"),
        Output(start_input_id, "date"),
        Output(end_input_id, "date"),
        Input(period_select_id, "value"),
        Input(start_input_id, "date"),
        Input(end_input_id, "date"),
        prevent_initial_call=False,
    )
    def _on_period_change(preset, start_picker, end_picker):
        # If a preset is chosen, compute from it. Custom -> use pickers.
        if preset and preset != "custom":
            start, end = resolve_period(preset)
            if start and end:
                return ({"preset": preset, "start": start.isoformat(),
                         "end": end.isoformat()},
                        start.isoformat(), end.isoformat())
        # Custom or empty preset -> trust pickers
        return ({"preset": "custom", "start": start_picker,
                 "end": end_picker},
                start_picker, end_picker)


# ---------- Toast ----------

def dispatch_toast(header: str, msg: str, icon: str = "primary") -> dict:
    """Build the payload for a toast-trigger store. Returns a dict
    that, when written into the trigger store, causes register_toast
    to open the toast with the given header / message / icon."""
    return {"header": header, "msg": msg, "icon": icon,
            "ts": dash.callback_context.timing_information if hasattr(dash, "callback_context") else 0}


def register_toast(app, *, toast_id: str, trigger_store_id: str):
    """Wire a dcc.Toast (id=toast_id) to a dcc.Store (id=trigger_store_id).
    Other callbacks dispatch by writing `dispatch_toast(...)` into the
    trigger store."""

    @app.callback(
        Output(toast_id, "is_open"),
        Output(toast_id, "header"),
        Output(toast_id, "children"),
        Output(toast_id, "icon"),
        Input(trigger_store_id, "data"),
        prevent_initial_call=True,
    )
    def _show_toast(payload):
        if not payload:
            return False, "", "", "primary"
        return (True,
                payload.get("header", ""),
                payload.get("msg", ""),
                payload.get("icon", "primary"))


# ---------- PDF download ----------

def register_pdf_download(
    app,
    *,
    button_id: str,
    download_id: str,
    fetcher: Callable[[], tuple[bytes, str]],
):
    """Button click -> call fetcher() -> stream bytes via dcc.Download.

    fetcher signature: () -> (bytes, filename). The caller is
    responsible for the API call + auth (httpx client etc).
    """
    from dash import dcc

    @app.callback(
        Output(download_id, "data"),
        Input(button_id, "n_clicks"),
        prevent_initial_call=True,
    )
    def _download(n_clicks):
        if not n_clicks:
            return dash.no_update
        try:
            content, filename = fetcher()
        except Exception as e:  # noqa: BLE001
            log.warning("PDF fetcher failed: %s", e)
            return dash.no_update
        return dcc.send_bytes(content, filename=filename)


# ---------- URL → active nav (sidebar variant) ----------

def register_url_active_nav(app, *, nav_items: list[dict], url_id: str = "url"):
    """For sidebar nav: class-toggle the active link based on the URL.

    Mirrors register_topnav_active() but for the sidebar pattern where
    each nav item is a `dcc.Link` with `id=item['id']`.
    """
    from dash import clientside_callback

    link_ids = [item["id"] for item in nav_items if "id" in item]
    path_map = {item["href"]: item["id"]
                 for item in nav_items if "id" in item and "href" in item}

    clientside_callback(
        """
        function(pathname) {
            const linkMap = """ + str(path_map).replace("'", '"') + """;
            const allIds  = """ + str(link_ids).replace("'", '"') + """;
            let activeId = linkMap[pathname] || null;
            if (!activeId) {
                for (const [path, id] of Object.entries(linkMap)) {
                    if (path !== "/" && pathname.startsWith(path)) { activeId = id; break; }
                }
            }
            allIds.forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                el.className = (id === activeId) ? "sidebar-link active" : "sidebar-link";
            });
            return window.dash_clientside.no_update;
        }
        """,
        Output(url_id, "search"),
        Input(url_id, "pathname"),
    )
