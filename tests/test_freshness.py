"""v0.92 'Data as of' badge (components/freshness.py)."""
import json

from dash import Dash

from aspire_dash.components import data_as_of_badge, data_as_of_text, register_data_as_of

NOW = 1_790_000_000.0   # fixed epoch; the badge renders it in Asia/Qatar


def test_text_live_fresh_stale():
    assert data_as_of_text(None)[0] == "Live data"
    text, cls, title = data_as_of_text(NOW - 600, now=NOW)
    assert text.startswith("Data as of ") and "stale" not in cls and "10 min ago" in title
    text, cls, title = data_as_of_text(NOW - 7200, now=NOW)
    assert "aspire-asof--stale" in cls and "2 h ago" in title


def test_qatar_time_regardless_of_server_clock():
    # 1_790_000_000 = 2026-09-21 14:13:20 UTC = 17:13 in Qatar (UTC+3, no DST)
    assert data_as_of_text(NOW, now=NOW)[0] == "Data as of 17:13"


def test_badge_and_callback_wire_up():
    app = Dash(__name__)
    app.layout = data_as_of_badge()
    register_data_as_of(app)
    blob = json.dumps(app.layout.to_plotly_json(), default=str)
    assert "aspire-data-as-of" in blob and "aspire-data-as-of-tick" in blob
    assert any("aspire-data-as-of" in k for k in app.callback_map)


def test_callback_uses_aspire_data_cache(monkeypatch):
    import time
    import aspire_data.cache as adc
    monkeypatch.setattr(adc, "data_as_of", lambda *f: time.time() - 60)   # real clock: fresh
    app = Dash(__name__)
    app.layout = data_as_of_badge()
    fn = register_data_as_of(app)
    text, cls, _ = fn(0)
    assert text.startswith("Data as of") and "stale" not in cls
