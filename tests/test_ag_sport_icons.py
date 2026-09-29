"""v0.99: one icon per sport in the Asian Games set, incl. our own Squash (Font Awesome only has a table-tennis
paddle, which is what Squash showed before: Kenny 2026-09-29 'the squash icon looks like table tennis')."""
from __future__ import annotations

import os

from aspire_dash import asian_games as ag


def test_font_awesome_sports_by_code_or_label():
    assert ag.ag_sport_fa("Athletics") == "fa-person-running" == ag.ag_sport_fa("ATH") == ag.ag_sport_fa("athletics")
    assert ag.ag_sport_fa("Table Tennis") == "fa-table-tennis-paddle-ball"
    assert ag.ag_sport_fa("Rugby") == "fa-medal" and ag.ag_sport_fa(None, default="x") == "x"
    icon = ag.ag_sport_icon("Fencing", extra="big")
    assert icon.className == "fa-solid fa-shield-halved big"


def test_squash_has_its_own_picture_not_the_table_tennis_paddle():
    sq, tt = ag.ag_sport_icon("Squash"), ag.ag_sport_icon("TTE")
    assert sq.src.endswith("brand/sport-icons/squash.svg") and sq.style["width"] == "1em"
    assert "fa-table-tennis-paddle-ball" in tt.className
    assert ag.ag_sport_icon("SQU").src == sq.src


def test_png_for_pdfs_and_files_ship_in_the_package():
    png = ag.ag_sport_icon_png("Squash")
    assert png and os.path.exists(png) and png.endswith("squash.png")
    assert os.path.exists(png[:-3] + "svg")
    assert ag.ag_sport_icon_png("Athletics") is None and ag.ag_sport_icon_png("Rugby") is None
    with open(png, "rb") as f:
        assert f.read(8) == b"\x89PNG\r\n\x1a\n"
