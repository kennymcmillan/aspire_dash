"""Grid filters -> safe MySQL WHERE (v0.76, promoted from the Data Explorer app).

Translate dash-ag-grid's `filterModel` (text / number / date, AND/OR per column, blank/notBlank,
v31 and legacy condition forms) plus simple {column, op, value} clauses into one AND-joined WHERE
body, with a plain-English `sentence()` and `sort_from_grid()` for the grid's columnState.

The read route takes a `where_clause` string, so we build SQL. Two guards:
  1. Column names are allowlisted against the dataset's REAL columns (never raw).
  2. Values are escaped (backslash + single-quote) and length-capped; numeric ops
     accept numbers only; identifiers are backtick-quoted.
This is defence-in-depth with the read-only route; there is no write access here.
"""
from __future__ import annotations

import re

MAX_VALUE_LEN = 200

# A plain SQL identifier is emitted bare. The REST paged route's where_guard rejects
# backticks outright (verified 2026-09-12: "`Country` = 'EGY'" -> 400), so quoting every
# identifier silently pushed every filtered public download onto the slow capped route.
# Bare is safe here because the column has already passed the allowlist.
_PLAIN_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# Range ops accept a number OR an ISO date / datetime literal.
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$")

# op -> (sql template, kind)
OPS: dict[str, tuple[str, str]] = {
    "=":           ("{c} = {v}",        "scalar"),
    "!=":          ("{c} <> {v}",       "scalar"),
    ">":           ("{c} > {v}",        "num"),
    ">=":          ("{c} >= {v}",       "num"),
    "<":           ("{c} < {v}",        "num"),
    "<=":          ("{c} <= {v}",       "num"),
    "contains":    ("{c} LIKE {v}",     "like_contains"),
    "not contains": ("{c} NOT LIKE {v}", "like_contains"),
    "starts with": ("{c} LIKE {v}",     "like_starts"),
    "ends with":   ("{c} LIKE {v}",     "like_ends"),
    "in":          ("{c} IN ({v})",     "list"),
    "not in":      ("{c} NOT IN ({v})", "list"),
    "between":     ("{c} BETWEEN {v}",  "range"),
    "is empty":    ("({c} IS NULL OR {c} = '')", "unary"),
    "not empty":   ("({c} IS NOT NULL AND {c} <> '')", "unary"),
}

# AG Grid filterModel `type` -> our op, per filterType.
_GRID_TEXT = {"contains": "contains", "notContains": "not contains", "equals": "=",
              "notEqual": "!=", "startsWith": "starts with", "endsWith": "ends with",
              "blank": "is empty", "notBlank": "not empty"}
_GRID_NUM = {"equals": "=", "notEqual": "!=", "greaterThan": ">", "greaterThanOrEqual": ">=",
             "lessThan": "<", "lessThanOrEqual": "<=", "inRange": "between",
             "blank": "is empty", "notBlank": "not empty"}
_GRID_DATE = {"equals": "=", "notEqual": "!=", "greaterThan": ">", "greaterThanOrEqual": ">=",
              "lessThan": "<", "lessThanOrEqual": "<=", "inRange": "between",
              "blank": "is empty", "notBlank": "not empty"}


def _q(s) -> str:
    """Quote a string literal for MySQL (escape backslash THEN single quote)."""
    s = str(s)[:MAX_VALUE_LEN]
    s = s.replace("\\", "\\\\").replace("'", "''")
    return "'" + s + "'"


def _ident(col: str) -> str:
    """Bare when plain; backticked only for names with spaces/dashes (tool route only)."""
    s = str(col).replace("`", "")
    return s if _PLAIN_IDENT.match(s) else "`" + s + "`"


def needs_tool_route(where: str | None) -> bool:
    """True if this WHERE can only run on the tool route (the REST guard rejects backticks)."""
    return bool(where) and "`" in where


def _as_number(v):
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return None


def _range_literal(v):
    """Number -> bare number; ISO date/datetime -> quoted literal; anything else -> None."""
    n = _as_number(v)
    if n is not None:
        return n
    s = str(v).strip()
    if _ISO_DATE.match(s):
        return _q(s)
    return None


def _compile_one(col: str, op: str, val) -> tuple[str | None, str | None]:
    """(sql, warning) for one already-allowlisted clause."""
    tmpl, kind = OPS[op]
    c = _ident(col)
    if kind == "unary":
        return tmpl.format(c=c), None
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return None, f"'{col} {op}': no value given; filter ignored"
    if kind == "scalar":
        return tmpl.format(c=c, v=_q(val)), None
    if kind == "num":
        lit = _range_literal(val)
        if lit is None:
            return None, f"'{col} {op} {val}': needs a number or a date like 2025-01-31; filter ignored"
        return tmpl.format(c=c, v=lit), None
    if kind == "range":
        lo, hi = (val if isinstance(val, (list, tuple)) and len(val) == 2
                  else (str(val).split(",", 1) + [""])[:2])
        a, b = _range_literal(lo), _range_literal(hi)
        if a is None or b is None:
            return None, f"'{col} between {lo} and {hi}': both ends need a number or a date; filter ignored"
        return tmpl.format(c=c, v=f"{a} AND {b}"), None
    if kind == "like_contains":
        return tmpl.format(c=c, v=_q("%" + str(val) + "%")), None
    if kind == "like_starts":
        return tmpl.format(c=c, v=_q(str(val) + "%")), None
    if kind == "like_ends":
        return tmpl.format(c=c, v=_q("%" + str(val))), None
    if kind == "list":
        items = (list(val) if isinstance(val, (list, tuple))
                 else [x.strip() for x in str(val).split(",")])
        items = [str(x) for x in items if str(x).strip() != ""]
        if not items:
            return None, f"'{col} {op}': no values given; filter ignored"
        return tmpl.format(c=c, v=",".join(_q(x) for x in items)), None
    return None, f"'{col}': unsupported operator kind"  # pragma: no cover


def compile_where_report(clauses: list[dict], valid_columns) -> tuple[str, list[str]]:
    """clauses = [{'column','op','value'}] or {'column','any':[{'op','value'},...]} (OR within
    one column) -> (where, warnings).

    `where` is an AND-joined body (no leading 'WHERE'), '' if nothing valid. Every dropped
    clause is named in `warnings` so the UI can say so instead of silently reporting
    "(no filter)" and handing back the whole table.
    """
    valid = set(valid_columns or [])
    parts: list[str] = []
    warnings: list[str] = []
    for cl in clauses or []:
        col = (cl or {}).get("column")
        if not col:
            continue  # an empty filter row, not an error
        if col not in valid:
            warnings.append(f"'{col}' is not a column of this dataset; filter ignored")
            continue
        subs = cl.get("any") if isinstance(cl.get("any"), list) else [cl]
        sqls: list[str] = []
        bad = False
        for s in subs:
            op = (s or {}).get("op")
            if op not in OPS:
                warnings.append(f"'{col}': unknown operator '{op}'; filter ignored")
                bad = True
                break
            sql, warn = _compile_one(col, op, (s or {}).get("value"))
            if warn:
                warnings.append(warn)
                bad = True
                break
            sqls.append(sql)
        if bad or not sqls:
            continue
        parts.append(sqls[0] if len(sqls) == 1 else "(" + " OR ".join(sqls) + ")")
    return " AND ".join(parts), warnings


# ── AG Grid filterModel -> clauses ────────────────────────────────────────────
def _grid_condition(col: str, cond: dict) -> dict | None:
    ft = (cond or {}).get("filterType", "text")
    t = (cond or {}).get("type")
    if ft == "number":
        op = _GRID_NUM.get(t)
        val = cond.get("filter")
        if op == "between":
            val = [cond.get("filter"), cond.get("filterTo")]
    elif ft == "date":
        op = _GRID_DATE.get(t)
        val = (cond.get("dateFrom") or "").strip()
        if op == "between":
            val = [(cond.get("dateFrom") or "").strip(), (cond.get("dateTo") or "").strip()]
        elif op == "=" and val:
            # a single day: the stored value may carry a time; match the whole day
            day = val[:10]
            return {"column": col, "op": "between", "value": [f"{day} 00:00:00", f"{day} 23:59:59"]}
        elif op == "!=" and val:
            return {"column": col, "op": "not contains", "value": val[:10]}
    else:
        op = _GRID_TEXT.get(t)
        val = cond.get("filter")
    if not op:
        return None
    return {"column": col, "op": op, "value": val}


def from_grid_model(model: dict | None, valid_columns) -> list[dict]:
    """Translate dash-ag-grid's `filterModel` into compile_where clauses. Handles the
    single-condition form, the v31+ combined form ({operator, conditions}) and the older
    condition1/condition2 form. Unknown columns are passed through so compile_where_report
    can name them in a warning (it never emits SQL for them)."""
    out: list[dict] = []
    for col, m in (model or {}).items():
        if not isinstance(m, dict):
            continue
        conds = m.get("conditions")
        if not conds and m.get("condition1"):
            conds = [m["condition1"]] + ([m["condition2"]] if m.get("condition2") else [])
        if conds:
            subs = [c for c in (_grid_condition(col, x) for x in conds) if c]
            if not subs:
                continue
            if (m.get("operator") or "AND").upper() == "OR" and len(subs) > 1:
                out.append({"column": col, "any": [{"op": s["op"], "value": s["value"]} for s in subs]})
            else:
                out.extend(subs)
        else:
            c = _grid_condition(col, m)
            if c:
                out.append(c)
    return out


def sort_from_grid(column_state: list | None) -> tuple[str | None, bool]:
    """(sort column, descending) from dash-ag-grid `columnState` (first sorted column)."""
    sorted_cols = [c for c in (column_state or []) if isinstance(c, dict) and c.get("sort")]
    if not sorted_cols:
        return None, False
    sorted_cols.sort(key=lambda c: c.get("sortIndex") or 0)
    c = sorted_cols[0]
    return c.get("colId"), (c.get("sort") == "desc")


def sentence(clauses: list[dict]) -> str:
    """Plain-English reading of the clauses ('Country is EGY or PAK, and Rank <= 20')."""
    words = {"=": "is", "!=": "is not", ">": ">", ">=": ">=", "<": "<", "<=": "<=",
             "contains": "contains", "not contains": "does not contain", "starts with": "starts with",
             "ends with": "ends with", "in": "is", "not in": "is not", "between": "is between",
             "is empty": "is empty", "not empty": "is not empty"}
    bits = []
    for cl in clauses or []:
        col = cl.get("column")
        subs = cl.get("any") if isinstance(cl.get("any"), list) else [cl]
        parts = []
        for s in subs:
            op, v = s.get("op"), s.get("value")
            if op in ("in", "not in") and isinstance(v, (list, tuple)):
                v = " or ".join(str(x) for x in v)
            elif op == "between" and isinstance(v, (list, tuple)):
                v = f"{v[0]} and {v[1]}"
            elif op in ("is empty", "not empty"):
                v = ""
            parts.append(f"{words.get(op, op)} {v}".strip())
        if parts:
            bits.append(f"{col} " + " or ".join(parts))
    return ", and ".join(bits)


def compile_where(clauses: list[dict], valid_columns) -> str:
    """Back-compat wrapper: the WHERE string only (see compile_where_report)."""
    return compile_where_report(clauses, valid_columns)[0]
