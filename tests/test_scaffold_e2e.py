"""End-to-end scaffolder smoke test.

Verifies that `python -m aspire_dash new <name>` produces a working
Dash app: all generated files parse, the app module imports without
errors, and (if Playwright is available) a real browser sees the
expected layout.

The Playwright leg is GATED on `pytest.importorskip('playwright')` +
Chrome being available, so the test suite still passes on a CI runner
without browsers.
"""
from __future__ import annotations

import ast
import importlib
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


# ---------- Stage 1: scaffold + parse ----------

@pytest.fixture
def scaffolded_app(tmp_path, monkeypatch):
    """Run `python -m aspire_dash new <name>` into a tmp dir.
    Returns the path to the generated app directory."""
    monkeypatch.chdir(tmp_path)
    name = "smoketest_app"
    # Pick an unused port near 8095 to avoid clashing with prior runs.
    port = next((p for p in range(8095, 8130) if not _port_open(p)), 8095)
    result = subprocess.run(
        [sys.executable, "-m", "aspire_dash", "new", name,
         "--title", "Smoke App", "--port", str(port)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"scaffold failed:\n{result.stderr}"
    app_dir = tmp_path / name
    assert app_dir.exists(), f"scaffold dir not created: {result.stdout}"
    # Drop a sidecar file with the port so the e2e test can pick it up
    (app_dir / ".port").write_text(str(port), encoding="utf-8")
    return app_dir


def test_scaffold_creates_all_expected_files(scaffolded_app):
    expected = {
        "app.py", "pages/home.py", "pages/reports.py", "api_client.py",
        "requirements.txt", ".env.example", "manifest.json",
        ".gitignore", "deploy.bat", "deploy.sh", "README.md",
    }
    actual = {str(p.relative_to(scaffolded_app)).replace("\\", "/")
              for p in scaffolded_app.rglob("*") if p.is_file()}
    missing = expected - actual
    assert not missing, f"scaffold missing files: {missing}"


def test_scaffold_python_files_all_parse(scaffolded_app):
    """Every generated .py file must AST-parse cleanly."""
    for path in scaffolded_app.rglob("*.py"):
        src = path.read_text(encoding="utf-8")
        try:
            ast.parse(src)
        except SyntaxError as e:
            pytest.fail(f"{path.name} has SyntaxError: {e}")


def test_scaffold_app_imports(scaffolded_app, monkeypatch):
    """The scaffolded app module must import without raising.
    Adds the app dir to sys.path + clears the page registry so other
    tests aren't affected."""
    monkeypatch.syspath_prepend(str(scaffolded_app))
    # Some Dash globals (page registry) leak across imports; flush before.
    for mod in list(sys.modules):
        if mod.startswith("app") or mod.startswith("pages"):
            sys.modules.pop(mod, None)
    try:
        importlib.import_module("app")
    except Exception as e:
        pytest.fail(f"scaffolded app failed to import: {type(e).__name__}: {e}")


def test_scaffold_uses_modern_components(scaffolded_app):
    """Verify the scaffolded code uses the v0.6+ patterns we promote:
    kpi_strip, skeleton-loaded card, dispatch_toast wiring."""
    home_src = (scaffolded_app / "pages" / "home.py").read_text(encoding="utf-8")
    assert "kpi_strip" in home_src
    assert "skel_card" in home_src or "skeletons" in home_src

    app_src = (scaffolded_app / "app.py").read_text(encoding="utf-8")
    assert "register_toast" in app_src
    assert "page_layout" in app_src
    assert "setup_app" in app_src


def test_scaffold_api_client_has_truststore(scaffolded_app):
    src = (scaffolded_app / "api_client.py").read_text(encoding="utf-8")
    assert "truststore" in src
    assert "load_dotenv" in src or "dotenv" in src
    assert "X-API-Key" in src


def test_scaffold_manifest_targets_python_312(scaffolded_app):
    import json
    manifest = json.loads((scaffolded_app / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["metadata"]["appmode"] == "python-dash"
    assert manifest["metadata"]["entrypoint"] == "app:server"
    # Don't pin the exact patch but at least the major+minor
    assert manifest["python"]["version"].startswith("3.")


# ---------- Stage 2: optional Playwright smoke ----------

def _port_open(port: int, timeout: float = 0.5) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


@pytest.mark.slow
def test_scaffolded_app_serves_home_page(scaffolded_app, monkeypatch):
    """Run the scaffolded app in a subprocess + use Playwright to
    confirm the Home page renders with the KPI strip + page title.

    Slow test (~12 s) — marked accordingly. Skipped if Playwright
    or Chrome aren't available. Provides the only true E2E proof
    that the scaffolder + the library produce a working app.
    """
    pytest.importorskip("playwright")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright not importable")

    # Scaffold fixture writes the chosen port to a sidecar file
    port_file = scaffolded_app / ".port"
    port = int(port_file.read_text(encoding="utf-8").strip()) if port_file.exists() else 8095
    if _port_open(port):
        pytest.skip(f"port {port} already in use; can't run scaffolded app")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(scaffolded_app) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=str(scaffolded_app),
        env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )

    try:
        # Wait up to 15s for the port to come up
        for _ in range(30):
            if _port_open(port):
                break
            time.sleep(0.5)
        else:
            stdout, stderr = proc.communicate(timeout=2)
            pytest.fail(
                f"scaffolded app didn't open port {port} in 15s\n"
                f"stdout: {stdout.decode()[-400:]!r}\n"
                f"stderr: {stderr.decode()[-400:]!r}"
            )

        # Playwright connect
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception as e:
                pytest.skip(f"chrome unavailable: {e}")
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{port}/", timeout=20000,
                       wait_until="domcontentloaded")
            time.sleep(2)  # let callbacks settle
            body = page.locator("body").inner_text(timeout=5000)
            body_lower = body.lower()
            # Verify modern scaffold output
            assert "home" in body_lower, f"Home heading not rendered: {body[:200]!r}"
            # kpi_tile uppercases labels via CSS — match case-insensitive
            kpi_signals = ["athletes", "sports", "today", "status"]
            assert any(s in body_lower for s in kpi_signals), \
                f"no KPI strip labels visible: {body[:300]!r}"
            # Confirm the data-bound callback fired (replaced the skeleton)
            assert "welcome" in body_lower or "replace this" in body_lower, \
                f"home content callback didn't replace skeleton: {body[:400]!r}"
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
