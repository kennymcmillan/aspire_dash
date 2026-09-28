"""Shared app test kit (v0.95): the baseline every Aspire Dash app runs, so the same
classes of bug are caught everywhere (Kenny 2026-09-28: "make sure we have a great test
suite across apps"). Each check returns a list of problems ([] = pass) so an app test is
one line and the failure message names every offender.

    # tests/test_baseline.py in any app
    from aspire_dash.testing import baseline_problems
    def test_baseline():
        import app
        assert baseline_problems(app.app, root=".") == []

Checks (each also callable on its own):
  * callback_target_problems  every callback Output id exists in some layout (else the
                              whole callback errors and the page ships BLANK: medical
                              dashboard Bone/Growth, 2026-07-08)
  * duplicate_output_problems two callbacks writing one Output without allow_duplicate
                              (endurance competition page, 2026-09-24)
  * page_render_problems      every registered page's layout() renders without raising
  * stale_cache_problems      functools.lru_cache on a live-data reader (never expires on
                              Connect: endurance aerobic tests hidden, 2026-09-25); needs
                              aspire_data >= 0.22.1, skipped otherwise
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

__all__ = ["baseline_problems", "callback_target_problems", "duplicate_output_problems",
           "page_render_problems", "stale_cache_problems", "layout_ids"]


def _walk_ids(node: Any, out: set) -> set:
    """Collect every component id (str, or dict pattern type) in a layout tree."""
    if node is None:
        return out
    if isinstance(node, (list, tuple)):
        for n in node:
            _walk_ids(n, out)
        return out
    cid = getattr(node, "id", None)
    if isinstance(cid, str):
        out.add(cid)
    elif isinstance(cid, dict) and "type" in cid:
        out.add(("__pattern__", cid["type"]))
    for attr in ("children",):
        _walk_ids(getattr(node, attr, None), out)
    # components that hold other components in non-children props (tabs, modals...)
    for prop in getattr(node, "_prop_names", []) or []:
        if prop in ("children", "id"):
            continue
        val = getattr(node, prop, None)
        if hasattr(val, "_prop_names") or (isinstance(val, (list, tuple)) and val
                                            and hasattr(val[0], "_prop_names")):
            _walk_ids(val, out)
    return out


def _render(layout: Any) -> Any:
    return layout() if callable(layout) else layout


def layout_ids(app) -> set:
    """Ids in app.layout plus every registered page's layout (dash.page_registry)."""
    ids: set = set()
    _walk_ids(_render(app.layout), ids)
    try:
        import dash
        for page in dash.page_registry.values():
            try:
                _walk_ids(_render(page.get("layout")), ids)
            except Exception:  # noqa: BLE001 - reported by page_render_problems
                pass
    except Exception:  # noqa: BLE001
        pass
    return ids


def _callback_outputs(app) -> list[tuple[Any, str, bool]]:
    """[(component id, property, allow_duplicate)] for every callback Output: the app's
    own callback_map plus page-level @callback (dash._callback.GLOBAL_CALLBACK_LIST)."""
    outs: list = []
    specs: list = []
    try:
        from dash import _callback
        specs += list(getattr(_callback, "GLOBAL_CALLBACK_LIST", []) or [])
    except Exception:  # noqa: BLE001
        pass
    specs += list(getattr(app, "_callback_list", []) or [])
    seen = set()
    for spec in specs:
        key = spec.get("output")
        if id(spec) in seen:          # same spec object listed twice (app + global list)
            continue
        seen.add(id(spec))
        for o in spec.get("outputs") or []:
            cid = o.get("id")
            prop = o.get("property", "")
            outs.append((cid, prop, bool(o.get("allow_duplicate"))))
        if not spec.get("outputs"):
            # older Dash: "output" is "id.prop" or "..id.prop...id2.prop2.."
            raw = str(key or "")
            for part in raw.strip(".").split("..."):
                if "." in part:
                    cid, prop = part.rsplit(".", 1)
                    outs.append((cid.split("@")[0], prop.split("@")[0], "@" in part))
    return outs


def _norm_id(cid: Any):
    if isinstance(cid, dict) and "type" in cid:
        return ("__pattern__", cid["type"])
    if isinstance(cid, str) and cid.startswith("{"):
        import json
        try:
            d = json.loads(cid)
            return ("__pattern__", d.get("type"))
        except ValueError:
            return cid
    return cid


_ID_LITERAL = None
import re as _re
_STR_LITERAL = _re.compile(r"""["']([A-Za-z][A-Za-z0-9_-]{2,60})["']""")


def source_ids(root) -> set:
    """Ids constructed ANYWHERE in the app's Python source (id="x", id='x',
    {"type": "x", ...}). Apps build most content inside callbacks (athlete pages,
    tab bodies), so a static layout walk alone reports false 'missing' targets."""
    import re
    global _ID_LITERAL
    if _ID_LITERAL is None:
        _ID_LITERAL = (re.compile(r"""\bid\s*=\s*["']([^"'{}]+)["']"""),
                       re.compile(r"""["']type["']\s*:\s*["']([^"']+)["']"""),
                       re.compile(r"""\bid\s*=\s*f["']([^"'{}]+)\{"""))
    ids: set = set()
    skip = {".venv", "venv", "site-packages", "node_modules", ".git", "build", "dist",
            ".claude", "_vendor", "__pycache__"}
    for p in Path(root).rglob("*.py"):
        if skip & set(p.parts):
            continue
        try:
            src = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        ids.update(_ID_LITERAL[0].findall(src))
        ids.update(("__pattern__", t) for t in _ID_LITERAL[1].findall(src))
        ids.update(("__prefix__", t) for t in _ID_LITERAL[2].findall(src))
        # pattern-matching ids are often built from a constant (TYPE = "x"; {"type": TYPE}):
        # accept a pattern type whose name appears as any string literal in the source
        ids.update(("__pattern__", t) for t in _STR_LITERAL.findall(src))
    return ids


def callback_target_problems(app, ignore: Iterable[str] = (), root=None) -> list[str]:
    """An Output passes if its component id is in a rendered layout OR constructed
    anywhere in the source under ``root``. Fails only when NOTHING in the app creates
    that id (renamed / deleted component: the whole callback errors, the page blanks)."""
    ids = layout_ids(app) | (source_ids(root) if root is not None else set())
    ids |= source_ids(Path(__file__).resolve().parent)   # components aspire_dash itself builds
    prefixes = [t for k, t in (i for i in ids if isinstance(i, tuple)) if k == "__prefix__"]
    ign = set(ignore)
    bad = []
    for cid, prop, _dup in _callback_outputs(app):
        n = _norm_id(cid)
        if n in ign or n in ids:
            continue
        if isinstance(n, str) and any(n.startswith(pfx) for pfx in prefixes):
            continue                                # id built as f"{prefix}{...}"
        bad.append(f"callback Output {cid}.{prop} has no component in any layout")
    return sorted(set(bad))


def duplicate_output_problems(app) -> list[str]:
    counts: dict = {}
    for cid, prop, dup in _callback_outputs(app):
        if dup:
            continue
        k = (str(cid), prop)
        counts[k] = counts.get(k, 0) + 1
    return sorted(f"Output {c}.{p} written by {n} callbacks without allow_duplicate"
                  for (c, p), n in counts.items() if n > 1)


def page_render_problems() -> list[str]:
    bad = []
    try:
        import dash
        pages = list(dash.page_registry.values())
    except Exception:  # noqa: BLE001
        return []
    for page in pages:
        try:
            _render(page.get("layout"))
        except Exception as e:  # noqa: BLE001
            bad.append(f"page {page.get('path')} layout() raised {type(e).__name__}: {e}")
    return bad


def stale_cache_problems(root) -> list[str]:
    try:
        from aspire_data.cache import find_live_lru
    except ImportError:
        return []
    return [f"lru_cache on a live reader (use ttl_cache): {h}" for h in find_live_lru(Path(root))]


def baseline_problems(app, root=".", ignore_targets: Iterable[str] = ()) -> list[str]:
    """All baseline checks for one app. [] means the app passes."""
    return (callback_target_problems(app, ignore_targets, root=root)
            + duplicate_output_problems(app)
            + page_render_problems() + stale_cache_problems(root))
