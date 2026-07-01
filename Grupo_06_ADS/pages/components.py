"""
Streamlit UI Components.

Reusable UI components for the educational platform.
"""
import streamlit as st
from typing import Optional, List, Dict, Any
from .styles import COLORS, DIFFICULTY_COLORS, STATUS_COLORS, ICONS


def render_card(
    title: str,
    content: str = "",
    icon: str = "",
    value: Optional[str] = None,
    badge: Optional[str] = None,
    badge_color: str = "info",
    on_click: Optional[callable] = None,
    key: Optional[str] = None
):
    """Render a card component."""
    badge_html = ""
    if badge:
        badge_class = f"badge-{badge_color}"
        badge_html = f'<span class="badge {badge_class}">{badge}</span>'

    value_html = ""
    if value:
        value_html = f'<div style="font-size: 1.5rem; font-weight: 700; color: #ffffff;">{value}</div>'

    card_html = f"""
    <div class="card fade-in" {f'key="{key}"' if key else ''}>
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    {f'<span style="font-size: 1.5rem;">{icon}</span>' if icon else ''}
                    <h3 style="margin: 0; color: #ffffff;">{title}</h3>
                    {badge_html}
                </div>
                <p style="margin-top: 0.5rem; color: #8b98a5;">{content}</p>
                {value_html}
            </div>
        </div>
    </div>
    """

    if on_click:
        col1, col2 = st.columns([5, 1])
        col1.markdown(card_html, unsafe_allow_html=True)
        if col2.button("->", key=f"btn_{key or title}"):
            on_click()
    else:
        st.markdown(card_html, unsafe_allow_html=True)


def render_metric_cards(metrics: List[Dict[str, Any]], columns: int = 4):
    """Render multiple metric cards in a row."""
    cols = st.columns(columns)
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            st.metric(
                label=metric.get("label", ""),
                value=metric.get("value", "-"),
                delta=metric.get("delta"),
                help=metric.get("help")
            )


def render_leaderboard_item(
    rank: int,
    name: str,
    points: int,
    level: int,
    medals: int = 0,
    is_current_user: bool = False
):
    """Render a leaderboard item."""
    rank_class = "rank-default"
    if rank == 1:
        rank_class = "rank-1"
    elif rank == 2:
        rank_class = "rank-2"
    elif rank == 3:
        rank_class = "rank-3"

    border_style = "border: 2px solid #3B82F6;" if is_current_user else ""

    html = f"""
    <div class="leaderboard-item" style="{border_style}">
        <div class="leaderboard-rank {rank_class}">{rank}</div>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: #ffffff;">{name}</div>
            <div style="font-size: 0.75rem; color: #8b98a5;">Nivel {level}</div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: 700; color: #3B82F6;">{points:,} pts</div>
            <div style="font-size: 0.75rem; color: #fbbf24;">{'*' * medals}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_progress_bar(
    current: int,
    total: int,
    label: str = "Progress",
    color: str = "primary"
):
    """Render a progress bar."""
    percentage = (current / total * 100) if total > 0 else 0
    color_hex = COLORS.get(color, COLORS["primary"])

    html = f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #8b98a5;">{label}</span>
            <span style="color: #ffffff;">{current}/{total}</span>
        </div>
        <div style="background: #2f3336; border-radius: 8px; height: 8px; overflow: hidden;">
            <div style="background: {color_hex}; width: {percentage}%; height: 100%; border-radius: 8px;"></div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_badge(
    text: str,
    color: str = "info",
    icon: Optional[str] = None
):
    """Render a badge/tag."""
    badge_class = f"badge-{color}"
    icon_html = f"{icon} " if icon else ""

    html = f'<span class="badge {badge_class}">{icon_html}{text}</span>'
    st.markdown(html, unsafe_allow_html=True)


def render_medal(
    name: str,
    description: str,
    icon: str = "medal",
    color: str = "#FFD700",
    earned: bool = False
):
    """Render a medal component."""
    opacity = "1" if earned else "0.4"

    html = f"""
    <div class="card" style="opacity: {opacity};">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="medal" style="background: {color};">
                {ICONS.get(icon, 'M')}
            </div>
            <div>
                <h4 style="margin: 0; color: #ffffff;">{name}</h4>
                <p style="margin: 0; color: #8b98a5; font-size: 0.875rem;">{description}</p>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_desafio_card(
    titulo: str,
    descricao: str,
    pontos: int,
    dificuldade: str,
    prazo: Optional[str] = None,
    status: Optional[str] = None,
    on_click: Optional[callable] = None,
    key: Optional[str] = None
):
    """Render a desafio card."""
    diff_color = DIFFICULTY_COLORS.get(dificuldade, "#F59E0B")

    status_badge = ""
    if status:
        status_color = STATUS_COLORS.get(status, "#8b98a5")
        status_badge = f'<span class="badge" style="background: {status_color}22; color: {status_color}; border-color: {status_color}44;">{status}</span>'

    prazo_text = f"<span style='color: #8b98a5;'>Prazo: {prazo}</span>" if prazo else ""

    html = f"""
    <div class="card fade-in">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h3 style="margin: 0; color: #ffffff;">{titulo}</h3>
                <p style="color: #8b98a5; margin-top: 0.5rem;">{descricao[:150]}{'...' if len(descricao) > 150 else ''}</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #3B82F6;">{pontos} pts</div>
                <span class="badge" style="background: {diff_color}22; color: {diff_color}; border-color: {diff_color}44;">{dificuldade}</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
            {prazo_text}
            {status_badge}
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    if on_click:
        if st.button("Ver Detalhes", key=f"btn_{key or titulo}"):
            on_click()


def render_stat_card(
    title: str,
    value: str,
    icon: str = "",
    color: str = "primary",
    subtitle: str = ""
):
    """Render a statistic card."""
    color_hex = COLORS.get(color, COLORS["primary"])

    html = f"""
    <div style="background: linear-gradient(135deg, #1a1f2e, #16202a);
         border: 1px solid #2f3336;
         border-radius: 12px;
         padding: 1.5rem;
         text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: {color_hex};">{value}</div>
        <div style="color: #8b98a5; font-size: 0.875rem;">{title}</div>
        {f'<div style="color: #8b98a5; font-size: 0.75rem; margin-top: 0.25rem;">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_avatar(name: str, size: int = 40, online: bool = True):
    """Render an avatar with initials."""
    initials = ''.join([n[0] for n in name.split()[:2]]).upper()

    html = f"""
    <div style="display: flex; align-items: center; gap: 0.5rem;">
        <div style="width: {size}px;
             height: {size}px;
             border-radius: 50%;
             background: linear-gradient(135deg, #3B82F6, #2563EB);
             display: flex;
             align-items: center;
             justify-content: center;
             color: white;
             font-weight: 600;
             font-size: {size // 2.5}px;">
            {initials}
        </div>
        {'<div style="width: 10px; height: 10px; border-radius: 50%; background: #10B981; border: 2px solid #0f1419;"></div>' if online else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state(
    message: str,
    icon: str = "-",
    action_text: Optional[str] = None,
    on_action: Optional[callable] = None
):
    """Render an empty state placeholder."""
    html = f"""
    <div style="text-align: center; padding: 3rem;">
        <div style="font-size: 4rem; color: #2f3336; margin-bottom: 1rem;">{icon}</div>
        <p style="color: #8b98a5; font-size: 1.1rem;">{message}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    if action_text and on_action:
        if st.button(action_text, key=f"empty_action_{message}"):
            on_action()


def render_tabs(
    tabs: List[str],
    default_tab: int = 0
) -> int:
    """Render custom tabs and return selected index."""
    selected = st.tabs(tabs)
    return selected


def show_success(message: str):
    """Show success message."""
    st.success(message)


def show_error(message: str):
    """Show error message."""
    st.error(message)


def show_info(message: str):
    """Show info message."""
    st.info(message)
