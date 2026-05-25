"""Reusable Dash components — split into focused submodules:

    nav            sidebar, topnav, header + active-link callbacks
    cards          card, summary_card, graph_card, info_box, linear_step_card, ...
    kpi            kpi_tile, kpi_strip, kpi_tile_row, kpi_stat
    feedback       toast, badge, empty_state, loading_overlay, status_pill,
                   freshness_banner, confirm_modal
    inputs         toggle_group, filter_bar, dark_mode_toggle, aspire_tabs
    print_export   print_header, print_footer, export_buttons, send_export

Backwards-compatible: every public function is still importable via
``from aspire_dash.components import X`` — this __init__ re-exports
the union from all submodules.

The original monolithic components.py was split at 0.8 → 0.9 — see
CHANGELOG.md.
"""
from .nav import *
from .cards import *
from .kpi import *
from .feedback import *
from .inputs import *
from .print_export import *

# v0.37 — re-export athlete banner helpers under components so
# `from aspire_dash.components import selected_athlete_banner,
# register_athlete_banner` works alongside the canonical
# `aspire_dash.athlete` location.
from ..athlete import selected_athlete_banner, register_athlete_banner  # noqa: F401, E402


__all__ = [
    'topnav', 'register_topnav_active', 'sidebar', 'hamburger_button',
    'register_sidebar_toggle', 'header',
    # cards
    'card', 'summary_card', 'graph_card', 'info_box', 'file_upload_card',
    'connect_user_chip',
    'linear_step_card',
    # v0.37 — patterns promoted from aspire-nutrition
    'linear_step_card_collapse', 'register_linear_step_toggle',
    'meta_inline_bar',
    'history_table',
    'ranked_dropdown',
    'selected_athlete_banner', 'register_athlete_banner',
    # kpi
    'kpi_tile', 'kpi_tile_row', 'kpi_strip', 'kpi_stat',
    # feedback
    'toast', 'badge', 'empty_state', 'loading_overlay', 'status_pill',
    'freshness_banner', 'confirm_modal', 'rate_limit_banner',
    # inputs
    'toggle_group', 'mode_toggle', 'filter_bar', 'dark_mode_toggle',
    'aspire_tabs',
    # print/export
    'print_header', 'print_footer', 'export_buttons', 'send_export',
]
