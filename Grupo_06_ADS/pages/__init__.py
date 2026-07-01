"""Pages package initialization."""
from .styles import apply_dark_theme, DARK_THEME_CSS, COLORS
from .session import SessionManager, APIClient, api
from .components import (
    render_card, render_metric_cards, render_leaderboard_item,
    render_progress_bar, render_badge, render_medal,
    render_desafio_card, render_stat_card, render_avatar,
    render_empty_state, render_tabs, show_success, show_error, show_info
)
from .login_page import render_login_page
from .dashboard import render_dashboard
from .challenges_page import render_challenges_page, render_create_desafio_page
from .gamification_page import render_gamification_page
from .miniprovas_page import render_miniprovas_page
from .teams_page import render_teams_page
from .missions_page import render_missions_page
from .polls_page import render_polls_page

__all__ = [
    'apply_dark_theme', 'DARK_THEME_CSS', 'COLORS',
    'SessionManager', 'APIClient', 'api',
    'render_card', 'render_metric_cards', 'render_leaderboard_item',
    'render_progress_bar', 'render_badge', 'render_medal',
    'render_desafio_card', 'render_stat_card', 'render_avatar',
    'render_empty_state', 'render_tabs', 'show_success', 'show_error', 'show_info',
    'render_login_page', 'render_dashboard',
    'render_challenges_page', 'render_create_desafio_page',
    'render_gamification_page', 'render_miniprovas_page',
    'render_teams_page', 'render_missions_page', 'render_polls_page'
]
