"""
Dashboard Page - Main landing page after login.
"""
import streamlit as st
from .session import SessionManager, api
from .styles import apply_dark_theme
from .components import (
    render_metric_cards, render_stat_card,
    render_leaderboard_item, render_empty_state,
    show_error
)


def render_dashboard():
    """Render the main dashboard."""
    apply_dark_theme()
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        st.warning("Por favor, faca login para continuar")
        return

    user = SessionManager.get_user()

    # Page header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"Ola, {user.nome.split()[0]}!")
        st.markdown(f"<span class='badge badge-info'>{user.role == 'professor' and 'Professor' or 'Aluno'}</span>", unsafe_allow_html=True)

    with col2:
        st.metric("Nivel", user.nivel, f"{user.pontuacao_total} pts")

    st.markdown("---")

    # Main content area
    if user.role == "professor":
        render_professor_dashboard(user)
    else:
        render_student_dashboard(user)


def render_student_dashboard(user):
    """Render student dashboard."""
    # Fetch user stats
    try:
        stats = api.get(f"/gamificacao/stats/{user.id}")
        leaderboard = api.get("/gamificacao/leaderboard", {"limit": 5})
    except Exception:
        stats = {}
        leaderboard = []
        show_error("Erro ao carregar dados")

    # Metrics row
    st.subheader("Sua Pontuacao")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_stat_card(
            title="Pontos",
            value=str(stats.get("pontos_totais", user.pontuacao_total)),
            icon="P",
            color="primary"
        )

    with col2:
        render_stat_card(
            title="Nivel",
            value=str(stats.get("nivel_atual", {}).get("nivel_atual", user.nivel)),
            icon="N",
            color="success"
        )

    with col3:
        render_stat_card(
            title="Desafios",
            value=str(stats.get("desafios_completados", 0)),
            icon="D",
            color="purple"
        )

    with col4:
        render_stat_card(
            title="Ranking",
            value=f"#{stats.get('ranking_posicao', '-')}",
            icon="R",
            color="warning"
        )

    st.markdown("---")

    # Two column layout
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Recent challenges
        st.subheader("Desafios Recentes")

        try:
            desafios = api.get("/desafios", {"limit": 3})
            if desafios and not isinstance(desafios, dict):
                for d in desafios[:3]:
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"""
                            <div class="card">
                                <h4 style="margin: 0; color: #ffffff;">{d.get('titulo', 'Desafio')}</h4>
                                <p style="color: #8b98a5; margin-top: 0.5rem; font-size: 0.875rem;">
                                    {d.get('descricao', '')[:100]}...
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.metric("Pontos", d.get("pontos_recompensa", 0))
            else:
                render_empty_state("Nenhum desafio disponivel", "D")
        except Exception:
            render_empty_state("Erro ao carregar desafios", "X")

    with col_right:
        # Leaderboard
        st.subheader("Top 5 Ranking")

        if leaderboard and not isinstance(leaderboard, dict):
            for entry in leaderboard[:5]:
                render_leaderboard_item(
                    rank=entry.get("posicao", 0),
                    name=entry.get("aluno_nome", "Aluno"),
                    points=entry.get("pontos", 0),
                    level=entry.get("nivel", 1),
                    medals=entry.get("medalhas", 0),
                    is_current_user=str(entry.get("aluno_id")) == str(user.id)
                )
        else:
            render_empty_state("Ranking vazio", "R")

    st.markdown("---")

    # Bottom section - Medals
    st.subheader("Suas Conquistas")

    try:
        conquistas = api.get("/gamificacao/conquistas")
        if conquistas and not isinstance(conquistas, dict):
            cols = st.columns(min(len(conquistas), 4))
            for i, c in enumerate(conquistas[:4]):
                with cols[i]:
                    medalha = c.get("medalha", {})
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #1a1f2e, #16202a);
                         border-radius: 12px; border: 1px solid #2f3336;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                            {medalha.get('icone', 'M')}
                        </div>
                        <div style="font-weight: 600; color: #ffffff;">{medalha.get('nome', 'Medalha')}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            render_empty_state("Nenhuma conquista ainda", "M")
    except Exception:
        pass


def render_professor_dashboard(user):
    """Render professor dashboard."""
    # Fetch professor's data
    try:
        disciplinas = api.get(f"/disciplinas?professor_id={user.id}")
        turmas = api.get(f"/turmas?professor_id={user.id}")
        desafios = api.get("/desafios", {"limit": 5})
    except Exception:
        disciplinas = []
        turmas = []
        desafios = []
        show_error("Erro ao carregar dados")

    # Metrics row
    st.subheader("Visao Geral")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_stat_card(
            title="Disciplinas",
            value=str(len(disciplinas) if isinstance(disciplinas, list) else 0),
            icon="L",
            color="primary"
        )

    with col2:
        render_stat_card(
            title="Turmas",
            value=str(len(turmas) if isinstance(turmas, list) else 0),
            icon="T",
            color="success"
        )

    with col3:
        render_stat_card(
            title="Desafios Ativos",
            value=str(len([d for d in (desafios if isinstance(desafios, list) else []) if d.get('ativo')])),
            icon="D",
            color="purple"
        )

    with col4:
        render_stat_card(
            title="Submissoes Pendentes",
            value="0",
            icon="S",
            color="warning"
        )

    st.markdown("---")

    # Quick actions
    st.subheader("Acoes Rapidas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Criar Desafio", use_container_width=True):
            SessionManager.set_page("Criar Desafio")
            st.rerun()

    with col2:
        if st.button("Nova Mini Prova", use_container_width=True):
            SessionManager.set_page("Criar Prova")
            st.rerun()

    with col3:
        if st.button("Ver Rankings", use_container_width=True):
            SessionManager.set_page("Rankings")
            st.rerun()

    st.markdown("---")

    # Recent activity
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Turmas")

        if turmas and isinstance(turmas, list):
            for t in turmas[:3]:
                st.markdown(f"""
                <div class="card">
                    <h4 style="margin: 0; color: #ffffff;">{t.get('nome', 'Turma')}</h4>
                    <p style="color: #8b98a5; margin-top: 0.25rem; font-size: 0.875rem;">
                        Codigo: {t.get('codigo_convite', 'N/A')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            render_empty_state("Nenhuma turma criada", "T")

    with col_right:
        st.subheader("Atividade Recente")
        render_empty_state("Sem atividade recente", "-")


def main():
    """Main function for dashboard."""
    render_dashboard()


if __name__ == "__main__":
    main()
