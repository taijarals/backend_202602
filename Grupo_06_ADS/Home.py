"""
EduGame Platform - Main Streamlit Application.

Educational Gamification Platform with Dark Theme.

Usage:
    streamlit run Home.py
"""
import streamlit as st
from pages import (
    SessionManager, apply_dark_theme,
    render_login_page, render_dashboard,
    render_challenges_page, render_create_desafio_page,
    render_gamification_page, render_miniprovas_page,
    render_teams_page, render_missions_page, render_polls_page
)


def main():
    """Main application entry point."""
    # Apply dark theme
    apply_dark_theme()

    # Initialize session
    SessionManager.init_session()

    # Check authentication
    if not SessionManager.is_authenticated():
        render_login_page()
        return

    # Get current user
    user = SessionManager.get_user()

    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; margin-bottom: 1rem;
             background: linear-gradient(135deg, #1a1f2e, #16202a);
             border-radius: 16px; border: 1px solid #3B82F6;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                {'P' if user.role == 'professor' else 'A'}
            </div>
            <div style="font-weight: 600; color: #ffffff;">{user.nome.split()[0]}</div>
            <div style="font-size: 0.75rem; color: #8b98a5;">{user.email}</div>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Nivel", user.nivel, f"{user.pontuacao_total} pts")

        st.markdown("---")

        # Navigation menu
        nav_options = {
            "Dashboard": "D",
            "Desafios": "C",
            "Mini Provas": "P",
            "Missoes": "G",
            "Equipes": "T",
            "Rankings": "R",
            "Enquetes": "E",
        }

        for page_name, icon in nav_options.items():
            if st.button(f"{icon}  {page_name}", use_container_width=True,
                        key=f"nav_{page_name}"):
                SessionManager.set_page(page_name)

        st.markdown("---")

        # Logout
        if st.button("Sair", use_container_width=True):
            SessionManager.logout()
            st.rerun()

    # Main content based on current page
    current_page = SessionManager.get_page()

    if current_page == "Dashboard":
        render_dashboard()

    elif current_page == "Desafios":
        render_challenges_page()

    elif current_page == "Criar Desafio":
        render_create_desafio_page()

    elif current_page == "Mini Provas":
        render_miniprovas_page()

    elif current_page == "Missoes":
        render_missions_page()

    elif current_page == "Equipes":
        render_teams_page()

    elif current_page == "Rankings":
        render_gamification_page()

    elif current_page == "Enquetes":
        render_polls_page()

    else:
        render_dashboard()


if __name__ == "__main__":
    main()
