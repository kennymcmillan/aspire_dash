"""Brand hero: the 3D spinning Aspire Academy badge as a landing-page hero (v0.102.0).

The badge is an 8 s seamless loop (chrome crest, blue enamel, gleam, "SPORTS DEPT. · DATA ANALYTICS"),
rendered with HyperFrames + Three.js from a redrawn vector crest. Render recipes (index.html in each):
``C:\\Users\\kenny\\code\\videos\\aspire-badge-3d`` (opaque master) and ``...\\aspire-badge-3d-alpha``
(transparent background: the WebM shipped here; the Safari MP4 is that render composited over the stage gradient).

The media lives in ``aspire_dash/media/``, NOT ``assets/``: ``setup_app`` copies the whole assets tree into
every app, and a video there would bloat every Connect bundle. ``brand_hero()`` copies the three files into
``<app assets>/aspire-media/`` the first time an app actually uses it.

    from aspire_dash.components import brand_hero
    layout = brand_hero(html.Div([...buttons / nav cards...]))
"""
import os
import shutil

import dash
from dash import html

_MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
_SUBDIR = "aspire-media"
BRAND_HERO_MP4 = "aspire-badge-3d.mp4"
BRAND_HERO_WEBM = "aspire-badge-3d.webm"
BRAND_HERO_POSTER = "aspire-badge-3d-poster.jpg"
BRAND_HERO_FILES = (BRAND_HERO_MP4, BRAND_HERO_WEBM, BRAND_HERO_POSTER)


def brand_media_path(name):
    """Absolute path of a packaged brand media file (for reports, decks, emails)."""
    if name not in BRAND_HERO_FILES:
        raise ValueError(f"unknown brand media file {name!r}; expected one of {BRAND_HERO_FILES}")
    return os.path.join(_MEDIA_DIR, name)


def _assets_folder(app):
    folder = None
    try:
        folder = app.config.get("assets_folder")
    except Exception:  # noqa: BLE001 - a non-Dash object: fall back to ./assets
        folder = None
    return folder or os.path.join(os.getcwd(), "assets")


def ensure_brand_media(app=None):
    """Copy the hero media into ``<assets>/aspire-media/`` (idempotent; newer package files win).

    Returns the destination folder, or None when no Dash app is available yet (e.g. imported at module load
    before ``Dash()`` exists); ``brand_hero()`` calls this again at render time, so the copy still happens.
    """
    if app is None:
        try:
            app = dash.get_app()
        except Exception:  # noqa: BLE001 - no app constructed yet
            return None
    dst_dir = os.path.join(_assets_folder(app), _SUBDIR)
    os.makedirs(dst_dir, exist_ok=True)
    for name in BRAND_HERO_FILES:
        src, dst = os.path.join(_MEDIA_DIR, name), os.path.join(dst_dir, name)
        if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
            shutil.copy2(src, dst)
    return dst_dir


def _asset_url(name):
    path = f"{_SUBDIR}/{name}"
    try:
        return dash.get_asset_url(path)          # honours requests_pathname_prefix (Connect /content/<guid>/)
    except Exception:  # noqa: BLE001 - no app context (unit tests, docs)
        return f"/assets/{path}"


def brand_hero(children=None, *, id="aspire-brand-hero",
               label="Aspire Academy, Sports Dept. Data Analytics", min_height=None, app=None):
    """Full-bleed landing hero: the spinning 3D Aspire badge on matching brand blue.

    children   optional content under the badge (buttons, nav cards, a welcome line).
    label      the text alternative: rendered as a visually hidden <h1>, so screen readers and search get the
               page title the video shows; the video itself is decorative (aria-hidden).
    min_height CSS min-height of the hero (default ``min(78vh, 760px)`` via the stylesheet).
    app        the Dash app, when calling before ``dash.get_app()`` works.

    Autoplays muted and looped on desktop and iOS (``assets/aspire_brand_hero.js`` sets ``muted`` and
    ``playsinline`` as attributes, which React does not). With ``prefers-reduced-motion`` the still poster
    shows instead of the video.
    """
    ensure_brand_media(app)
    poster = _asset_url(BRAND_HERO_POSTER)
    style = {"minHeight": min_height} if min_height else None
    video = html.Video(
        [html.Source(src=_asset_url(BRAND_HERO_WEBM), type="video/webm"),
         html.Source(src=_asset_url(BRAND_HERO_MP4), type="video/mp4")],
        className="aspire-brand-hero__video", autoPlay=True, muted=True, loop=True,
        preload="auto", poster=poster, **{"aria-hidden": "true"},
    )
    still = html.Img(src=poster, alt="", className="aspire-brand-hero__still", **{"aria-hidden": "true"})
    body = [html.H1(label, className="aspire-visually-hidden"),
            html.Div([video, still], className="aspire-brand-hero__stage")]
    if children is not None:
        body.append(html.Div(children, className="aspire-brand-hero__content"))
    return html.Section(body, id=id, className="aspire-brand-hero", style=style)


__all__ = ["brand_hero", "ensure_brand_media", "brand_media_path",
           "BRAND_HERO_MP4", "BRAND_HERO_WEBM", "BRAND_HERO_POSTER", "BRAND_HERO_FILES"]
