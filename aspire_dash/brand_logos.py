"""Aspire Academy + Qatar federation logo catalogue.

Sniffed from www.aspire.qa/Home partners section. 15 federations +
2 ministries + the Aspire mark. Files live in
``assets/brand/partners/`` and are auto-shipped by ``setup_app()``.

Usage::

    from aspire_dash.brand_logos import partner_logo, PARTNER_LOGOS

    html.Img(src=partner_logo("fencing"), style={"height": "48px"})

    # Or iterate the catalogue
    for key, meta in PARTNER_LOGOS.items():
        print(meta["name"], meta["file"])

Keys are short slugs (`fencing`, `swimming`, `oly`, `moe`...) so the
calling code stays readable. Match the federation Kenny actually uses
in MEMORY → sports skill (the existing FIE/PSA/ITTF source_badge map).
"""
from __future__ import annotations

from dash import html
import dash


# Slug -> {name, file, sport_category}
PARTNER_LOGOS = {
    # Aspire mark
    "aspire": {
        "name": "Aspire Academy",
        "file": "brand/partners/aspire-academy-logo.svg",
        "category": "academy",
    },
    # Ministries
    "moe": {
        "name": "Ministry of Education",
        "file": "brand/partners/qa_ministry_education.jpg",
        "category": "ministry",
    },
    "mos": {
        "name": "Ministry of Sports and Youth",
        "file": "brand/partners/qa_ministry_sports.jpg",
        "category": "ministry",
    },
    # Olympic / multi-sport
    "oly": {
        "name": "Qatar Olympic Committee",
        "file": "brand/partners/qa_olympic_committee.png",
        "category": "multi-sport",
    },
    "sc": {
        "name": "Supreme Committee for Delivery & Legacy",
        "file": "brand/partners/qa_supreme_committee.png",
        "category": "multi-sport",
    },
    # Per-sport federations (Aspire portfolio — football excluded by design)
    "athletics": {
        "name": "Qatar Athletics Federation",
        "file": "brand/partners/qa_athletics_federation.png",
        "category": "federation",
    },
    "tt": {
        "name": "Qatar Table Tennis Association",
        "file": "brand/partners/qa_table_tennis_association.png",
        "category": "federation",
    },
    "squash": {
        "name": "Qatar Squash Federation",
        "file": "brand/partners/qa_squash_federation.png",
        "category": "federation",
    },
    "fencing": {
        "name": "Qatar Fencing Federation",
        "file": "brand/partners/qa_fencing_federation.png",
        "category": "federation",
    },
    "gymnastics": {
        "name": "Qatar Gymnastics Federation",
        "file": "brand/partners/qa_gymnastics_federation.jpg",
        "category": "federation",
    },
    "swimming": {
        "name": "Qatar Swimming Association",
        "file": "brand/partners/qa_swimming_association.png",
        "category": "federation",
    },
    "shooting": {
        "name": "Qatar Shooting & Archery Association",
        "file": "brand/partners/qa_shooting_archery_association.png",
        "category": "federation",
    },
    "golf": {
        "name": "Qatar Golf Association",
        "file": "brand/partners/qa_golf_association.png",
        "category": "federation",
    },
    "motor": {
        "name": "Qatar Motor & Motorcycle Federation",
        "file": "brand/partners/qa_motor_motorcycle_federation.png",
        "category": "federation",
    },
    # International partner / award
    "kas_eupen": {
        "name": "KAS Eupen",
        "file": "brand/partners/intl_kas_eupen.jpg",
        "category": "international",
    },
    "leonesa": {
        "name": "Cultural y Deportiva Leonesa",
        "file": "brand/partners/intl_leonesa.jpg",
        "category": "international",
    },
    "inspirational_leader": {
        "name": "Inspirational Leader Award",
        "file": "brand/partners/award_inspirational_leader.jpg",
        "category": "award",
    },
}


# Sport hero photos — sniffed from aspire.qa/Sports/* pages.
# Use as page banners, card backgrounds, sport-page heroes.
SPORT_HEROES = {
    # Football intentionally excluded — Aspire portfolio is non-football focus
    "athletics":     ["brand/sports/athletics1.jpg",
                       "brand/sports/athletics2.jpg",
                       "brand/sports/athletics3.jpg"],
    "fencing":       ["brand/sports/fencing1.jpg",
                       "brand/sports/fencing2.jpg",
                       "brand/sports/fencing3.jpg"],
    "squash":        ["brand/sports/squash1.jpg",
                       "brand/sports/squash2.jpg",
                       "brand/sports/squash3.jpg"],
    "table_tennis":  ["brand/sports/table-tennis1.jpg",
                       "brand/sports/table-tennis2.jpg",
                       "brand/sports/table-tennis3.jpg"],
    "facility":      ["brand/sports/facility1.jpg",
                       "brand/sports/facility2.jpg",
                       "brand/sports/facility3.jpg",
                       "brand/sports/facility4.jpg",
                       "brand/sports/facility5.jpg"],
}


def sport_hero(sport: str, index: int = 0) -> str:
    """Return the Connect-safe asset URL for a sport hero shot.

    >>> sport_hero("fencing")     # first fencing shot
    >>> sport_hero("athletics", 2)  # third athletics shot
    """
    files = SPORT_HEROES.get(sport.lower().replace("-", "_"))
    if not files:
        return ""
    return _safe_relative(f"/assets/{files[index % len(files)]}")


def sport_hero_img(sport: str, index: int = 0, *,
                    height: int | None = None,
                    width: str | None = "100%"):
    """`html.Img` wrapped sport hero shot. Use as a page banner."""
    src = sport_hero(sport, index)
    if not src:
        return html.Span(f"[no hero: {sport}]")
    style = {"width": width, "objectFit": "cover", "display": "block"}
    if height is not None:
        style["height"] = f"{height}px"
    return html.Img(src=src, style=style,
                     alt=f"{sport.replace('_', ' ').title()} at Aspire Academy")


def _safe_relative(path: str) -> str:
    """`dash.get_relative_path` with a fallback for non-app contexts."""
    try:
        return dash.get_relative_path(path)
    except Exception:
        return path


def partner_logo(slug: str) -> str:
    """Return the Connect-safe asset URL for a partner logo slug.

    >>> partner_logo("fencing")
    '/assets/brand/partners/qa_fencing_federation.png'
    """
    meta = PARTNER_LOGOS.get(slug.lower())
    if not meta:
        return ""
    return _safe_relative(f"/assets/{meta['file']}")


def partner_logo_img(slug: str, *, height: int = 48, **kwargs):
    """Convenience — returns an `html.Img` with the resolved src + alt.

    >>> partner_logo_img("fencing", height=60)
    """
    meta = PARTNER_LOGOS.get(slug.lower())
    if not meta:
        return html.Span(f"[no logo: {slug}]")
    return html.Img(
        src=_safe_relative(f"/assets/{meta['file']}"),
        alt=meta["name"],
        style={"height": f"{height}px", "width": "auto",
                **kwargs.pop("style", {})},
        **kwargs,
    )


def partners_strip(slugs: list[str] | None = None, *, height: int = 40):
    """Horizontal strip of partner logos. If ``slugs`` is None, shows all
    federations + ministries (good for footers + about pages).
    """
    if slugs is None:
        slugs = [k for k, v in PARTNER_LOGOS.items()
                  if v["category"] in ("federation", "ministry",
                                        "multi-sport")]
    return html.Div(
        [partner_logo_img(s, height=height) for s in slugs],
        style={"display": "flex", "flexWrap": "wrap",
                "gap": "20px", "alignItems": "center",
                "padding": "12px"},
    )
