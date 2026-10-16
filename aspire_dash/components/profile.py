"""Athlete profile components (v0.108, promoted from High Management Overview).

    podium(items, title=...)            the top N as big band-tinted cards (who is good, at a glance)
    profile_hero(name, ...)             the athlete page hero: tinted frame, ONE big number, identity,
                                        pills, form strip, next step, medals slot, six chips
    profile_pill(text, tone, icon)      a pill for the hero's pill row
    form_strip(items, label)            last results as chips: W / L or a place (medal colours)
    form_from_results(rows, n)          read form items off a results table [date, comp, event, round, opp, result]

Bands are the same data as the squad tier card (components/squad.py): ``band="<key>"`` gives class
``ad-band-<key>`` and its four ``--ad-tier*`` variables. Shipped keys: target, future, squad; an app adds
its own (HMO adds its six classes) in its own CSS. Every value is passed in: nothing here invents a
number, and a missing one is left out or shown as a quiet dash. Styling: assets/08_profile.css.
"""
from __future__ import annotations

import re
from typing import Optional

from dash import dcc, html

from ..athlete import athlete_avatar
from .squad import _band_cls, meta_line

__all__ = ["podium", "profile_hero", "profile_pill", "form_strip", "form_from_results", "FORM_KINDS"]

FORM_KINDS = ("win", "loss", "gold", "silver", "bronze", "place")
_MEDAL_KIND = {1: "gold", 2: "silver", 3: "bronze"}
PILL_TONES = ("plain", "level", "ok", "warn")


def _icon(name: Optional[str]):
    return html.I(className=f"fa-solid {name}", **{"aria-hidden": "true"}) if name else None


def _link(children, href, link, className, aria=None):
    kw = {"aria-label": aria} if aria else {}
    if href is None:
        return html.Div(children, className=className, **kw)
    if link == "dcc":
        return dcc.Link(children, href=href, className=className, **kw)
    return html.A(children, href=href, className=className, **kw)


# --------------------------------------------------------------------------- podium
def podium(items: list, *, title: Optional[str] = "At the top right now", n: int = 5, link: str = "dcc",
           aria_label: str = "Top athletes"):
    """The top ``n`` athletes as big band-tinted cards, best first. Each item is a dict:
    ``name``, ``photo``, ``band``, ``band_label``, ``value`` + ``scope`` (the big number, e.g. '#6' 'world'),
    ``sub`` (one string or a list for ``meta_line``), ``note`` (one quiet line, e.g. the level now), ``href``.
    Items without a ``value`` are skipped (the podium only shows athletes with a real number).
    Returns None when nobody has one, so a page can leave the section out."""
    top = [it for it in (items or []) if it and it.get("value") not in (None, "")][:n]
    if not top:
        return None
    cards = []
    for i, it in enumerate(top, 1):
        sub = it.get("sub")
        cards.append(_link([
            html.Div([html.Span(str(i), className="ad-pod-pos"),
                      html.Span(it.get("band_label") or "", className="ad-pod-cls")], className="ad-pod-band"),
            html.Div(athlete_avatar(it.get("photo"), it.get("name"), size="lg"), className="ad-pod-ph"),
            html.Div([html.Div(str(it["value"]), className="ad-pod-num"),
                      html.Div(it.get("scope") or "", className="ad-pod-scope")], className="ad-pod-big"),
            html.B(it.get("name") or "Unknown", className="ad-pod-name"),
            html.Span(meta_line(sub) if isinstance(sub, (list, tuple)) else (sub or ""), className="ad-pod-sub"),
            html.Span(it.get("note") or "", className="ad-pod-note"),
        ], it.get("href"), link, f"ad-pod {_band_cls(it.get('band') or 'squad')}"))
    return html.Section([html.H2(title, className="ad-pod-title") if title else None,
                         html.Div(cards, className="ad-pod-strip", role="list")],
                        className="ad-podium", **{"aria-label": aria_label})


# --------------------------------------------------------------------------- form strip
def form_from_results(rows, n: int = 5) -> list[dict]:
    """Form items from a results table, newest first. Rows are ``[date, competition, event, round, opponent,
    result]``; result 'Won 3-0' / 'Lost 1-3' gives W / L, '1st, 47.82' or '11th' gives the place (1-3 in medal
    colours). Rows that are neither are skipped."""
    out = []
    for r in (rows or [])[:n]:
        if not isinstance(r, (list, tuple)) or len(r) < 6:
            continue
        res = str(r[5] or "")
        title = " · ".join(str(x) for x in (r[0], r[1], r[3], f"v {r[4]}" if r[4] else "", res) if x)
        low = res.strip().lower()
        if low.startswith("won"):
            out.append({"text": "W", "kind": "win", "title": title})
        elif low.startswith("lost"):
            out.append({"text": "L", "kind": "loss", "title": title})
        else:
            m = re.match(r"\s*(\d+)", res)
            if m:
                place = int(m.group(1))
                out.append({"text": str(place), "kind": _MEDAL_KIND.get(place, "place"), "title": title})
    return out


def form_strip(items, label: str = "Form"):
    """Chips for the last results (``form_from_results`` output or your own ``{text, kind, title}``).
    None when empty."""
    items = [it for it in (items or []) if it and it.get("text")]
    if not items:
        return None
    return html.Div([html.Span(label, className="ad-ph-cl")] +
                    [html.Span(it["text"], className=f"ad-form is-{it.get('kind') if it.get('kind') in FORM_KINDS else 'place'}",
                               title=it.get("title")) for it in items],
                    className="ad-ph-form", **{"aria-label": "Latest results, newest first"})


# --------------------------------------------------------------------------- hero
def profile_pill(text, tone: str = "plain", icon: Optional[str] = None):
    """A hero pill. ``tone``: plain | level (band-tinted) | ok (green) | warn (amber). ``icon``: a Font Awesome
    name such as 'fa-clock'. None when there is no text."""
    if text in (None, ""):
        return None
    return html.Span([_icon(icon), f" {text}" if icon else text],
                     className=f"ad-ph-pill is-{tone if tone in PILL_TONES else 'plain'}")


def _chip(c: dict):
    return html.Div([html.Div(c.get("label"), className="ad-ph-cl"), html.Div(str(c.get("value")), className="ad-ph-cv"),
                     html.Div(c["sub"], className="ad-ph-cs") if c.get("sub") else None], className="ad-ph-chip")


def profile_hero(name, *, photo=None, band: str = "squad", band_label: Optional[str] = None, value=None,
                 scope: Optional[str] = None, of=None, empty_text: str = "No ranking on file", meta=None,
                 pills=None, headline: Optional[str] = None, form=None, next_step=None,
                 next_label: str = "Next step", medals=None, chips=None, max_chips: int = 6,
                 is_target: bool = False, aria_label: str = "Athlete"):
    """The athlete page hero.

    Left: a band-tinted photo frame with ``band_label`` on its foot. Then ONE big number: ``value`` + ``scope``
    (+ ' · of N' when ``of`` is given); ``value=None`` shows ``empty_text`` instead (never an invented rating).
    Identity: ``name``, ``meta`` (a list of strings joined with soft dots, or components), ``pills`` (components,
    e.g. ``profile_pill``; None items dropped), ``headline`` (one sentence), ``form`` (items for ``form_strip``),
    ``next_step`` (any component, shown under ``next_label``). ``medals``: any component (a medal tally).
    ``chips``: up to ``max_chips`` dicts ``{label, value, sub}``. Pass only what you have; every part left out
    when empty."""
    if value is not None and value != "":
        scope_txt = (scope or "") + (f" · of {of:,}" if isinstance(of, int) else (f" · of {of}" if of else ""))
        number = html.Div([html.Div(str(value), className="ad-ph-num"),
                           html.Div(scope_txt, className="ad-ph-scope") if scope_txt else None], className="ad-ph-big")
    else:
        number = html.Div(html.Div(empty_text, className="ad-ph-scope"), className="ad-ph-big is-empty")
    if isinstance(meta, (list, tuple)) and all(isinstance(m, str) for m in meta):
        meta_el = html.Div(html.Span(" · ".join(m for m in meta if m)), className="ad-ph-meta")
    else:
        meta_el = html.Div(meta, className="ad-ph-meta") if meta else None
    pill_els = [p for p in (pills or []) if p is not None]
    chip_els = [_chip(c) for c in (chips or []) if c and c.get("value") not in (None, "")][:max_chips]
    return html.Section([
        html.Div([html.Div(athlete_avatar(photo, name, size="lg", is_target=is_target), className="ad-ph-photo"),
                  html.Div(band_label, className="ad-ph-tag") if band_label else None], className="ad-ph-frame"),
        number,
        html.Div([html.H2(name or "Unknown", className="ad-ph-name"),
                  meta_el,
                  html.Div(pill_els, className="ad-ph-pills") if pill_els else None,
                  html.P(headline, className="ad-ph-headline") if headline else None,
                  form_strip(form),
                  html.Div([html.Span(next_label, className="ad-ph-cl"), next_step], className="ad-ph-next")
                  if next_step is not None else None],
                 className="ad-ph-id"),
        html.Div(medals, className="ad-ph-medals") if medals is not None else None,
        html.Div(chip_els, className="ad-ph-chips") if chip_els else None,
    ], className=f"ad-ph {_band_cls(band)}", **{"aria-label": aria_label})
