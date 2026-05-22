"""Regression tests for `normalised_path` — the helper that sits in every
router callback.

The bug history (CHANGELOG):
  * v0.12.3 — added the helper
  * v0.22.2 — fixed CRITICAL crash when pathname is already bare on
              Connect (Dash auto-strips requests_pathname_prefix before
              calling callbacks, so /content/<GUID>/whoop arrived as
              just /whoop — and the previous `dash.strip_relative_path`
              call raised UnsupportedRelativePath).

These tests pin the contract so the bug never returns. If anyone
modifies normalised_path and breaks one of these cases, the next
deploy will block on red tests instead of 500-ing in production.
"""
import dash
import pytest

from aspire_dash import normalised_path


# Each test runs against TWO Dash app contexts:
# - "/"           — local development (requests_pathname_prefix = "/")
# - "/content/G/" — Posit Connect deploy (subpath mount)
@pytest.fixture(params=["/", "/content/abc-def-123/"])
def app_ctx(request):
    """Activate a Dash app with the given pathname prefix.
    Dash reads `requests_pathname_prefix` at Dash() init time and
    `strip_relative_path` uses it via the global app context."""
    a = dash.Dash(
        __name__,
        requests_pathname_prefix=request.param,
        routes_pathname_prefix=request.param,
        # Suppress so we don't have to register every test page
        suppress_callback_exceptions=True,
    )
    yield request.param
    # Dash holds onto the singleton — clear it for the next test
    if hasattr(dash, "_dash_get_paths"):
        dash._dash_get_paths.CONFIG.requests_pathname_prefix = "/"


# ── 1. Bare paths (what callbacks actually receive) ─────────────────────────

@pytest.mark.parametrize("bare,expected", [
    ("/",             "/"),
    ("/whoop",        "/whoop"),
    ("/whoop/",       "/whoop"),
    ("/athletes",     "/athletes"),
    ("/sport/Fencing", "/sport/Fencing"),
    ("",              "/"),
    (None,            "/"),
])
def test_bare_path_passthrough(app_ctx, bare, expected):
    """Dash auto-strips the prefix before calling callbacks, so the
    helper must accept already-bare paths without raising.
    This is what the v0.22.2 fix is about."""
    assert normalised_path(bare) == expected


# ── 2. Already-prefixed paths (defensive — local code might pass full URL) ──

def test_prefixed_path_under_connect_subpath():
    """When the app is mounted at /content/<GUID>/ and someone passes
    the FULL URL to the helper, the prefix must be stripped cleanly."""
    a = dash.Dash(
        __name__,
        requests_pathname_prefix="/content/abc-def-123/",
        routes_pathname_prefix="/content/abc-def-123/",
        suppress_callback_exceptions=True,
    )
    assert normalised_path("/content/abc-def-123/whoop") == "/whoop"
    assert normalised_path("/content/abc-def-123/")      == "/"
    assert normalised_path("/content/abc-def-123/sport/Fencing") == "/sport/Fencing"


# ── 3. Idempotence — the bug we just fixed ──────────────────────────────────

def test_idempotent_on_bare_paths_under_connect():
    """The exact pathological case from the bug report. App mounted at
    a Connect subpath, but the pathname arrives already bare. Previous
    versions raised UnsupportedRelativePath. This test would have
    caught the v0.22.0 regression before deploy."""
    a = dash.Dash(
        __name__,
        requests_pathname_prefix="/content/ff25919f-6e90-4e5b-b8d3-efa02f9f5c74/",
        routes_pathname_prefix="/content/ff25919f-6e90-4e5b-b8d3-efa02f9f5c74/",
        suppress_callback_exceptions=True,
    )
    # These are the EXACT pathnames from the Connect job log that 500'd
    assert normalised_path("/")        == "/"
    assert normalised_path("/whoop/")  == "/whoop"
    assert normalised_path("/reports") == "/reports"
    assert normalised_path("/squad")   == "/squad"


# ── 4. No-context fallback ─────────────────────────────────────────────────

def test_normalised_path_without_app_context():
    """Called from a test fixture or ad-hoc preview — no Dash app
    initialised. Must not crash; fall through to returning the input."""
    # Clear any active app context first
    if hasattr(dash, "_dash_get_paths"):
        dash._dash_get_paths.CONFIG.requests_pathname_prefix = "/"
    # These should at minimum NOT raise
    assert normalised_path("/whoop") == "/whoop"
    assert normalised_path("/")      == "/"
    assert normalised_path(None)     == "/"
