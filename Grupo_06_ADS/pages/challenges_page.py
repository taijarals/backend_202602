"""
Desafios (Challenges) Page.
"""
import streamlit as st
from typing import Optional
from .session import SessionManager, api
from .styles import apply_dark_theme, DIFFICULTY_COLORS
from .components import (
    render_desafio_card, render_empty_state,
    render_badge, render_progress_bar,
    show_error, show_success
)


def render_challenges_page():
    """Render the challenges page."""
    apply_dark_theme()
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        st.warning("Por favor, faca login")
        return

    user = SessionManager.get_user()

    st.title("Desafios")
    st.markdown("###")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        turma_filter = st.selectbox(
            "Turma",
            ["Todas"] + _get_user_turmas(user),
            key="challenge_turma_filter"
        )

    with col2:
        difficulty_filter = st.selectbox(
            "Dificuldade",
            ["Todas", "facil", "media", "dificil", "expert"],
            format_func=lambda x: x.capitalize() if x != "Todas" else x,
            key="challenge_diff_filter"
        )

    with col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Atualizar"):
            st.rerun()

    st.markdown("---")

    # Action buttons for professors
    if user.role == "professor":
        if st.button("Criar Novo Desafio", type="primary"):
            SessionManager.set_page("Criar Desafio")
            st.rerun()
        st.markdown("---")

    # Fetch desafios
    try:
        params = {}
        if turma_filter != "Todas":
            params["turma_id"] = turma_filter

        desafios = api.get("/desafios", params)

        if not desafios or isinstance(desafios, dict):
            render_empty_state(
                "Nenhum desafio disponivel",
                "-",
                "Criar Desafio" if user.role == "professor" else None,
                lambda: SessionManager.set_page("Criar Desafio")
            )
            return

        # Apply difficulty filter
        if difficulty_filter != "Todas":
            desafios = [d for d in desafios if d.get("dificuldade") == difficulty_filter]

        # Render challenge cards
        for desafio in desafios:
            render_desafio_item(desafio, user)

    except Exception as e:
        show_error(f"Erro ao carregar desafios: {str(e)}")


def render_desafio_item(desafio: dict, user):
    """Render a single desafio item."""
    with st.expander(f"**{desafio.get('titulo', 'Desafio')}** - {desafio.get('pontos_recompensa', 0)} pts"):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**Descricao:**")
            st.write(desafio.get("descricao", ""))

            st.markdown(f"**Tipo:** {desafio.get('tipo', 'N/A')}")

            difficulty = desafio.get("dificuldade", "media")
            diff_color = DIFFICULTY_COLORS.get(difficulty, "#F59E0B")
            st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <span>Dificuldade:</span>
                <span class="badge" style="background: {diff_color}22; color: {diff_color}; border-color: {diff_color}44;">
                    {difficulty}
                </span>
            </div>
            """, unsafe_allow_html=True)

            prazo = desafio.get("prazo")
            if prazo:
                st.markdown(f"**Prazo:** {prazo}")

        with col2:
            st.metric("Pontos", desafio.get("pontos_recompensa", 0))

            # Check submission status
            if user.role == "student":
                if st.button("Enviar Submissao", key=f"sub_{desafio.get('id')}"):
                    _show_submission_dialog(desafio)

            elif user.role == "professor":
                if st.button("Ver Submissoes", key=f"view_{desafio.get('id')}"):
                    _show_submissions_list(desafio)


def _get_user_turmas(user) -> list:
    """Get user's turmas for filter."""
    try:
        if user.role == "student":
            turmas = api.get("/turmas/my")
        else:
            turmas = api.get(f"/turmas?professor_id={user.id}")

        if isinstance(turmas, list):
            return [t.get("id") for t in turmas]
    except Exception:
        pass
    return []


def _show_submission_dialog(desafio: dict):
    """Show submission dialog for students."""
    st.session_state.selected_desafio = desafio
    st.session_state.show_submission = True


def _show_submissions_list(desafio: dict):
    """Show submissions list for professors."""
    st.session_state.selected_desafio = desafio
    st.session_state.show_submissions = True


def render_create_desafio_page():
    """Render create desafio form for professors."""
    apply_dark_theme()
    SessionManager.init_session()

    user = SessionManager.get_user()
    if user.role != "professor":
        st.error("Acesso negado")
        return

    st.title("Criar Novo Desafio")

    with st.form("create_desafio"):
        titulo = st.text_input("Titulo", placeholder="Nome do desafio")
        descricao = st.text_area("Descricao", placeholder="Descreva o desafio em detalhes", height=150)

        col1, col2 = st.columns(2)

        with col1:
            pontos = st.number_input("Pontos de Recompensa", min_value=10, max_value=1000, value=100)
            tipo = st.selectbox("Tipo", ["codigo", "quiz", "projeto", "pesquisa", "outro"])

        with col2:
            dificuldade = st.selectbox("Dificuldade", ["facil", "media", "dificil", "expert"])
            prazo = st.date_input("Prazo (opcional)", value=None)

        turma = st.selectbox("Turma", _get_user_turmas(user))
        disciplina = st.selectbox("Disciplina", _get_disciplinas(user))

        submit = st.form_submit_button("Criar Desafio", type="primary")

        if submit:
            if not titulo or not descricao:
                show_error("Preencha todos os campos obrigatorios")
            else:
                try:
                    data = {
                        "titulo": titulo,
                        "descricao": descricao,
                        "pontos_recompensa": pontos,
                        "tipo": tipo,
                        "dificuldade": dificuldade,
                        "professor_id": str(user.id),
                    }

                    if turma:
                        data["turma_id"] = turma
                    if disciplina:
                        data["disciplina_id"] = disciplina
                    if prazo:
                        data["prazo"] = str(prazo)

                    response = api.post("/desafios", data)

                    if "error" in response:
                        show_error(response.get("message", "Erro ao criar desafio"))
                    else:
                        show_success("Desafio criado com sucesso!")
                        SessionManager.set_page("Desafios")
                        st.rerun()
                except Exception as e:
                    show_error(f"Erro: {str(e)}")


def _get_disciplinas(user) -> list:
    """Get professor's disciplinas."""
    try:
        disciplinas = api.get(f"/disciplinas?professor_id={user.id}")
        if isinstance(disciplinas, list):
            return [d.get("id") for d in disciplinas]
    except Exception:
        pass
    return []


def main():
    """Main function."""
    render_challenges_page()


if __name__ == "__main__":
    main()
