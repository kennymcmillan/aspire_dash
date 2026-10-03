"""brand_hero (v0.102.0): the spinning 3D Aspire badge as a landing hero."""
import os

import dash
from dash import html
import pytest

from aspire_dash.components import (brand_hero, ensure_brand_media, brand_media_path,
                                    BRAND_HERO_FILES, BRAND_HERO_MP4, BRAND_HERO_WEBM, BRAND_HERO_POSTER)
import aspire_dash

PKG = os.path.dirname(aspire_dash.__file__)


def _walk(node):
    yield node
    kids = getattr(node, "children", None)
    if kids is None:
        return
    for k in kids if isinstance(kids, (list, tuple)) else [kids]:
        if hasattr(k, "_type"):
            yield from _walk(k)


def _find(root, cls):
    return [n for n in _walk(root) if isinstance(n, cls)]


def test_media_ship_in_the_package_and_are_real_files():
    for name in BRAND_HERO_FILES:
        p = brand_media_path(name)
        assert os.path.isfile(p), p
        assert os.path.getsize(p) > 20_000, f"{name} is suspiciously small"
    assert os.path.getsize(brand_media_path(BRAND_HERO_MP4)) < 3_000_000, "keep the hero video web-sized"


def test_media_are_not_in_assets_so_setup_app_does_not_copy_them_everywhere():
    assets = os.path.join(PKG, "assets")
    for root, _dirs, files in os.walk(assets):
        for f in files:
            assert not f.endswith((".mp4", ".webm")), f"video in assets/ would ship in every app: {f}"


def test_unknown_media_name_is_refused():
    with pytest.raises(ValueError):
        brand_media_path("../../etc/passwd")


def test_hero_structure_sources_poster_and_text_alternative(tmp_path):
    app = dash.Dash(__name__, assets_folder=str(tmp_path / "assets"))
    hero = brand_hero(html.Button("Open dashboard"), app=app, label="Aspire Academy, Sports Dept. Data Analytics")
    assert hero.id == "aspire-brand-hero" and "aspire-brand-hero" in hero.className
    videos = _find(hero, html.Video)
    assert len(videos) == 1
    v = videos[0]
    assert v.autoPlay is True and v.muted is True and v.loop is True
    srcs = [s.src for s in _find(v, html.Source)]
    assert srcs[0].endswith(BRAND_HERO_WEBM) and srcs[1].endswith(BRAND_HERO_MP4)
    assert v.poster.endswith(BRAND_HERO_POSTER)
    h1 = _find(hero, html.H1)[0]
    assert h1.children == "Aspire Academy, Sports Dept. Data Analytics"
    assert "aspire-visually-hidden" in h1.className
    assert any(isinstance(b, html.Button) for b in _walk(hero)), "children render under the badge"


def test_media_are_copied_into_the_using_app_only(tmp_path):
    app = dash.Dash(__name__, assets_folder=str(tmp_path / "assets"))
    dst = ensure_brand_media(app)
    for name in BRAND_HERO_FILES:
        assert os.path.getsize(os.path.join(dst, name)) == os.path.getsize(brand_media_path(name))
    # idempotent: a second call leaves the files as they are
    before = {n: os.path.getmtime(os.path.join(dst, n)) for n in BRAND_HERO_FILES}
    ensure_brand_media(app)
    assert before == {n: os.path.getmtime(os.path.join(dst, n)) for n in BRAND_HERO_FILES}


def test_no_children_means_no_content_block(tmp_path):
    app = dash.Dash(__name__, assets_folder=str(tmp_path / "assets"))
    hero = brand_hero(app=app)
    assert not [n for n in _walk(hero) if "aspire-brand-hero__content" in (getattr(n, "className", "") or "")]


def test_media_glob_is_in_package_data():
    import ast
    tree = ast.parse(open(os.path.join(os.path.dirname(PKG), "setup.py"), encoding="utf-8-sig").read())
    globs = [c.value for c in ast.walk(tree) if isinstance(c, ast.Constant) and isinstance(c.value, str)]
    assert "media/*" in globs, "media/ must be in package_data or pip installs ship without the video"
