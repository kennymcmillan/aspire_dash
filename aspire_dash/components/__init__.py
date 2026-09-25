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
from .chat import chat_panel, register_chat_panel, chips_from_done, trace_text  # noqa: F401  (v0.75 M7)
from .help import help_drawer, help_button, welcome_modal, register_help  # noqa: F401  (v0.76)
from .search import search_box, search_hit, search_hit_id, hit_list  # noqa: F401  (v0.76)
# v0.90 — hover-out popouts promoted from endurance-dashboard. Importing these
# modules AUTO-REGISTERS their callbacks on Dash's global callback registry.
from .history import history_trigger, history_modal  # noqa: F401  (v0.90)
from .hovercard import (hovercard_graph, render_card, HOVERCARD_ARROW)  # noqa: F401  (v0.90)
from .freshness import data_as_of_badge, data_as_of_text, register_data_as_of  # noqa: F401  (v0.92)

# v0.37 — re-export athlete banner helpers under components so
# `from aspire_dash.components import selected_athlete_banner,
# register_athlete_banner` works alongside the canonical
# `aspire_dash.athlete` location.
from ..athlete import selected_athlete_banner, register_athlete_banner  # noqa: F401, E402
from ..athlete import athlete_banner, nationality_flag, nationality_flag_img, athletics_age_band  # noqa: F401, E402
from ..athlete import (flyout_trigger, flyout_canvas, register_flyout,  # noqa: F401, E402
                       flyout_open_id, flyout_canvas_id)
from ..tables import roster_table  # noqa: F401, E402  (v0.89, promoted from development_dashboard)


__all__ = [
    'roster_table',
    'topnav', 'register_topnav_active', 'sidebar', 'hamburger_button',
    'register_sidebar_toggle', 'header',
    'data_as_of_badge', 'data_as_of_text', 'register_data_as_of',
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
    'athlete_banner', 'nationality_flag', 'nationality_flag_img', 'athletics_age_band',
    'flyout_trigger', 'flyout_canvas', 'register_flyout',
    'flyout_open_id', 'flyout_canvas_id',
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
    # chat (v0.75, M7 2026-08-30): the sports chatbot embedded in any app
    'chat_panel', 'register_chat_panel', 'chips_from_done', 'trace_text',
    # help + search (v0.76, promoted from the Data Explorer app 2026-09-12)
    'help_drawer', 'help_button', 'welcome_modal', 'register_help',
    'search_box', 'search_hit', 'search_hit_id', 'hit_list',
    # hover-out popouts (v0.90, promoted from endurance-dashboard)
    'history_trigger', 'history_modal',
    'hovercard_graph', 'render_card', 'HOVERCARD_ARROW',
]
