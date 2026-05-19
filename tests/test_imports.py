"""Smoke: every module imports cleanly + key public symbols exist.

A regression in a single submodule import would silently break every
downstream Aspire app at boot time. This file catches that the moment
it hits main.
"""
import importlib

import pytest


MODULES = [
    "aspire_dash",
    "aspire_dash.theme",
    "aspire_dash.charts",
    "aspire_dash.layouts",
    "aspire_dash.components",
    "aspire_dash.sports",
    "aspire_dash.firstbeat",
    "aspire_dash.viz",
    "aspire_dash.skeletons",
    "aspire_dash.observability",
    "aspire_dash.stats",
    "aspire_dash.timeseries",
    "aspire_dash.athlete",
    "aspire_dash.budget",
    "aspire_dash.export",
    "aspire_dash.tables",
    "aspire_dash.time",
    "aspire_dash.callbacks",
    "aspire_dash.cache_prewarm",
]


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module):
    importlib.import_module(module)


def test_package_version_set():
    import aspire_dash
    assert isinstance(aspire_dash.__version__, str)
    assert aspire_dash.__version__.count(".") == 2  # x.y.z


def test_stylesheets_list_includes_bootstrap_and_fa():
    from aspire_dash import STYLESHEETS
    joined = " ".join(STYLESHEETS)
    assert "bootstrap" in joined.lower() or "/css/" in joined
    # Font Awesome
    assert "font" in joined.lower() or "fa" in joined.lower()


def test_setup_app_creates_assets_folder(tmp_path, monkeypatch):
    """setup_app should copy the shared CSS into the app's assets folder."""
    from aspire_dash import setup_app

    class _FakeApp:
        config = {"assets_folder": str(tmp_path)}

    setup_app(_FakeApp())
    # At minimum the base CSS must land in the assets folder
    files = set(os.listdir(tmp_path))
    expected = {"00_aspire_base.css", "01_aspire_print.css", "aspire-logo.png"}
    missing = expected - files
    assert not missing, f"setup_app didn't copy: {missing}"


import os  # noqa: E402 — used in last test
