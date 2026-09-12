"""Shareable view state (v0.76, promoted from the Data Explorer app): the grid filter model, applied value picks and sort, packed
into one URL parameter (`v=`) so a member can send a colleague the exact view. Decoding is
tolerant: anything malformed returns None and the page opens unfiltered. Nothing here is
trusted: the filter model still goes through the column allowlist + compiler on the server."""
from __future__ import annotations

import base64
import json
import zlib

MAX_PARAM = 2000  # keep URLs pasteable in chat/email


def encode(filter_model: dict | None, picks: dict | None, sort_col: str | None = None,
           sort_desc: bool = False) -> str:
    """Compact, URL-safe token; '' when there is nothing to carry."""
    state = {}
    if filter_model:
        state["f"] = filter_model
    if picks:
        state["p"] = {k: list(v) for k, v in picks.items() if v}
    if sort_col:
        state["s"] = [sort_col, bool(sort_desc)]
    if not state:
        return ""
    raw = json.dumps(state, separators=(",", ":"), sort_keys=True).encode("utf-8")
    tok = base64.urlsafe_b64encode(zlib.compress(raw, 9)).decode("ascii").rstrip("=")
    return tok if len(tok) <= MAX_PARAM else ""


def decode(token: str | None) -> dict | None:
    """-> {"filter_model": dict, "picks": dict, "sort_col": str|None, "sort_desc": bool} or None."""
    if not token or not isinstance(token, str) or len(token) > MAX_PARAM:
        return None
    try:
        pad = "=" * (-len(token) % 4)
        raw = zlib.decompress(base64.urlsafe_b64decode(token + pad), bufsize=65536)
        if len(raw) > 200_000:
            return None
        state = json.loads(raw.decode("utf-8"))
    except Exception:
        return None
    if not isinstance(state, dict):
        return None
    fm = state.get("f") if isinstance(state.get("f"), dict) else {}
    picks = {k: [str(x) for x in v] for k, v in (state.get("p") or {}).items()
             if isinstance(k, str) and isinstance(v, list)} if isinstance(state.get("p"), dict) else {}
    s = state.get("s")
    sort_col, sort_desc = (s[0], bool(s[1])) if isinstance(s, list) and len(s) == 2 and isinstance(s[0], str) else (None, False)
    return {"filter_model": fm, "picks": picks, "sort_col": sort_col, "sort_desc": sort_desc}


def column_state(sort_col: str | None, sort_desc: bool) -> list[dict]:
    """AG Grid columnState that applies one sort (empty list = no sort)."""
    if not sort_col:
        return []
    return [{"colId": sort_col, "sort": "desc" if sort_desc else "asc", "sortIndex": 0}]
