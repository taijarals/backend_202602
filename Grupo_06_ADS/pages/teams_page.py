"""
Equipes (Teams) Page.
"""
import streamlit as st
from .session import SessionManager, api
from .styles import apply_dark_theme, COLORS
from .components import render_empty_state, render_avatar, show_error, show_success


def render_teams_page():
    """Render teams page."""
    apply_dark_theme()
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        st.warning("Por favor, faca login")
        return

    user = SessionManager.get_user()
    st.title("Equipes")

    # Get user's teams
    try:
        my_teams = api.get("/equipes/my")

        if user.role == "professor":
            render_professor_teams_view(user)
        else:
            render_student_teams_view(user, my_teams)

    except Exception as e:
        show_error(f"Erro ao carregar equipes: {str(e)}")


def render_student_teams_view(user, my_teams):
    """Render student's teams view."""
    tab1, tab2 = st.tabs(["Minha Equipe", "Buscar Equipe"])

    with tab1:
        if my_teams and not isinstance(my_teams, dict):
            equipe = my_teams[0] if isinstance(my_teams, list) else my_teams
            render_team_details(equipe)
        else:
            render_empty_state("Voce ainda nao faz parte de uma equipe", "T")
            st.info("Entre em uma equipe ou aguarde o professor formar os times")

    with tab2:
        st.subheader("Equipes Disponiveis")

        turma_filter = st.selectbox("Selecione a Turma", _get_turmas(user))

        if turma_filter:
            try:
                equipes = api.get(f"/equipes/turma/{turma_filter}")

                if equipes and isinstance(equipes, list):
                    for equipe in equipes:
                        with st.expander(f"**{equipe.get('nome')}**"):
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.write(f"**Descricao:** {equipe.get('descricao', 'N/A')}")
                                st.write(f"**Membros:** {equipe.get('total_membros', 0)}/{equipe.get('max_membros', 5)}")

                            with col2:
                                if equipe.get("total_membros", 0) < equipe.get("max_membros", 5):
                                    if st.button("Entrar", key=f"join_{equipe.get('id')}"):
                                        join_team(equipe.get("id"), user.id)
                                else:
                                    st.write("Equipe cheia")

                else:
                    render_empty_state("Nenhuma equipe disponivel nesta turma", "T")

            except Exception as e:
                show_error(f"Erro: {str(e)}")


def render_professor_teams_view(user):
    """Render professor's teams management view."""
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Criar Equipe", type="primary", use_container_width=True):
            st.session_state.show_create_team = True

    with col2:
        if st.button("Formar Times Automaticamente", use_container_width=True):
            st.session_state.show_auto_form = True

    with col3:
        if st.button("Gerenciar Equipes", use_container_width=True):
            st.session_state.show_manage = True

    st.markdown("---")

    # List teams by turma
    turma_filter = st.selectbox("Filtrar por Turma", ["Todas"] + _get_professor_turmas(user))

    try:
        if turma_filter != "Todas":
            equipes = api.get(f"/equipes/turma/{turma_filter}")
        else:
            equipes = []
            for t in _get_professor_turmas(user):
                team_list = api.get(f"/equipes/turma/{t}")
                if team_list and isinstance(team_list, list):
                    equipes.extend(team_list)

        if equipes:
            for equipe in equipes:
                render_team_card_professor(equipe)
        else:
            render_empty_state("Nenhuma equipe criada", "T")

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def render_team_details(equipe: dict):
    """Render team details for students."""
    st.subheader(equipe.get("nome", "Minha Equipe"))

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1f2e, #16202a);
             border-radius: 16px; padding: 2rem; border: 1px solid {equipe.get('cor', '#3B82F6')};">
            <h3 style="margin: 0; color: #ffffff;">{equipe.get('nome')}</h3>
            <p style="color: #8b98a5; margin-top: 0.5rem;">{equipe.get('descricao', 'Nenhuma descricao')}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric("Pontuacao da Equipe", equipe.get("pontuacao", 0))

    st.markdown("### Membros")

    membros = equipe.get("membros", [])
    if membros:
        cols = st.columns(min(len(membros), 4))
        for i, membro in enumerate(membros):
            with cols[i % 4]:
                render_avatar(membro.get("aluno_nome", "Membro"))
                st.write(f"**{membro.get('aluno_nome', 'Membro')}**")
                render_badge(membro.get("papel", "membro").capitalize(),
                           "success" if membro.get("papel") == "lider" else "info")
                st.write(f"{membro.get('aluno_pontos', 0)} pts")
    else:
        st.info("Nenhum membro na equipe")


def render_team_card_professor(equipe: dict):
    """Render team card for professor view."""
    with st.expander(f"**{equipe.get('nome')}** - {equipe.get('total_membros', 0)} membros"):
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.write(f"**Descricao:** {equipe.get('descricao', 'N/A')}")

            membros = equipe.get("membros", [])
            st.write(f"**Membros:** {', '.join([m.get('aluno_nome', '') for m in membros])}")

        with col2:
            lider = next((m for m in membros if m.get("papel") == "lider"), None)
            if lider:
                st.write(f"**Lider:** {lider.get('aluno_nome', 'N/A')}")

            st.metric("Pontos", equipe.get("pontuacao", 0))

        with col3:
            if st.button("Adicionar Pontos", key=f"pts_{equipe.get('id')}"):
                st.session_state.add_points_team = equipe

            if st.button("Gerenciar", key=f"mgmt_{equipe.get('id')}"):
                st.session_state.manage_team = equipe

        st.markdown("---")


def join_team(equipe_id: str, aluno_id: str):
    """Join a team."""
    try:
        result = api.post(f"/equipes/{equipe_id}/members", {
            "aluno_id": aluno_id,
            "papel": "membro"
        })

        if "error" not in result:
            show_success("Voce entrou na equipe!")
            st.rerun()
        else:
            show_error(result.get("message", "Erro ao entrar na equipe"))
    except Exception as e:
        show_error(f"Erro: {str(e)}")


def _get_turmas(user) -> list:
    """Get user's turmas."""
    try:
        turmas = api.get("/turmas/my")
        if isinstance(turmas, list):
            return [t.get("id") for t in turmas]
    except Exception:
        pass
    return []


def _get_professor_turmas(user) -> list:
    """Get professor's turmas."""
    try:
        turmas = api.get(f"/turmas?professor_id={user.id}")
        if isinstance(turmas, list):
            return [t.get("id") for t in turmas]
    except Exception:
        pass
    return []


def main():
    """Main function."""
    render_teams_page()


if __name__ == "__main__":
    main()
