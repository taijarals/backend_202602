"""
Mini Provas (Quick Tests) Page.
"""
import streamlit as st
import time
from datetime import datetime
from .session import SessionManager, api
from .styles import apply_dark_theme
from .components import render_empty_state, render_badge, show_error, show_success


def render_miniprovas_page():
    """Render mini provas page."""
    apply_dark_theme()
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        st.warning("Por favor, faca login")
        return

    user = SessionManager.get_user()

    st.title("Mini Provas")

    if user.role == "professor":
        render_professor_view(user)
    else:
        render_student_view(user)


def render_professor_view(user):
    """Render professor's view of mini provas."""
    if st.button("Nova Mini Prova", type="primary"):
        st.session_state.show_create_prova = True

    st.markdown("---")

    # List existing mini provas
    try:
        provas = api.get("/mini-provas")

        if provas and isinstance(provas, list):
            for prova in provas:
                with st.expander(f"**{prova.get('titulo')}** ({prova.get('duracao_minutos')} min)"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Descricao:** {prova.get('descricao', 'N/A')}")
                        st.write(f"**Tentativas Permitidas:** {prova.get('tentativas_permitidas')}")
                        st.write(f"**Pontos Maximos:** {prova.get('pontos_maximos')}")

                        status = "Ativa" if prova.get("ativa") else "Inativa"
                        render_badge(status, "success" if prova.get("ativa") else "error")

                    with col2:
                        if st.button("Ver Detalhes", key=f"view_{prova.get('id')}"):
                            st.session_state.selected_prova = prova
                        if st.button("Editar", key=f"edit_{prova.get('id')}"):
                            st.session_state.edit_prova = prova
        else:
            render_empty_state("Nenhuma mini prova criada", "P")
    except Exception as e:
        show_error(f"Erro ao carregar provas: {str(e)}")


def render_student_view(user):
    """Render student's view of mini provas."""
    tab1, tab2 = st.tabs(["Disponiveis", "Realizadas"])

    with tab1:
        render_available_provas(user)

    with tab2:
        render_completed_provas(user)


def render_available_provas(user):
    """Render available mini provas for student."""
    try:
        provas = api.get("/mini-provas")

        if provas and isinstance(provas, list):
            active_provas = [p for p in provas if p.get("ativa")]

            for prova in active_provas:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.markdown(f"""
                        <div class="card">
                            <h4 style="margin: 0; color: #ffffff;">{prova.get('titulo')}</h4>
                            <p style="color: #8b98a5; margin-top: 0.5rem;">{prova.get('descricao', '')[:100]}...</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.write(f"**Duracao:** {prova.get('duracao_minutos')} minutos")
                        st.write(f"**Tentativas:** {prova.get('tentativas_permitidas')}")
                        st.write(f"**Pontos:** {prova.get('pontos_maximos')}")

                    with col3:
                        if st.button("Iniciar", key=f"start_{prova.get('id')}", type="primary"):
                            start_prova(prova, user)

                    st.markdown("---")
        else:
            render_empty_state("Nenhuma mini prova disponivel", "P")

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def start_prova(prova: dict, user):
    """Start a mini prova."""
    st.session_state.current_prova = prova
    st.session_state.prova_start_time = time.time()
    st.session_state.current_answers = {}

    try:
        response = api.post(f"/mini-provas/{prova.get('id')}/start")
        if "error" not in response:
            st.session_state.tentativa_id = response.get("id")
            show_success("Prova iniciada!")
        else:
            show_error(response.get("message", "Erro ao iniciar prova"))
    except Exception as e:
        show_error(f"Erro: {str(e)}")


def render_completed_provas(user):
    """Render student's completed provas."""
    try:
        tentativas = api.get("/mini-provas/my/tentativas")

        if tentativas and isinstance(tentativas, list):
            completed = [t for t in tentativas if t.get("status") == "finalizada"]

            for tentativa in completed:
                with st.container():
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        st.markdown(f"""
                        <div class="card">
                            <h4 style="margin: 0; color: #ffffff;">{tentativa.get('mini_prova_titulo', 'Prova')}</h4>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.metric("Pontos", tentativa.get("pontos_obtidos", 0))
                        aprovada = tentativa.get("aprovada")
                        if aprovada:
                            render_badge("Aprovado", "success")
                        else:
                            render_badge("Nao Aprovado", "warning")

        else:
            render_empty_state("Nenhuma prova realizada", "-")

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def render_prova_interface(prova: dict, questoes: list):
    """Render the active prova interface with timer."""
    st.title(prova.get("titulo"))

    # Timer
    start_time = st.session_state.get("prova_start_time", time.time())
    duration = prova.get("duracao_minutos", 30) * 60
    elapsed = time.time() - start_time
    remaining = max(0, duration - elapsed)

    # Display timer
    timer_placeholder = st.empty()
    mins, secs = divmod(int(remaining), 60)
    timer_placeholder.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
         border-radius: 12px; border: 1px solid #3B82F6; margin-bottom: 2rem;">
        <div style="font-size: 0.875rem; color: #8b98a5;">Tempo Restante</div>
        <div style="font-size: 3rem; font-weight: 700; color: {'#EF4444' if remaining < 300 else '#3B82F6'};">{mins:02d}:{secs:02d}</div>
    </div>
    """, unsafe_allow_html=True)

    # Questions
    answers = st.session_state.get("current_answers", {})

    for i, questao in enumerate(questoes):
        st.markdown(f"**Questao {i + 1}** ({questao.get('pontos')} pts)")
        st.write(questao.get("enunciado"))

        q_type = questao.get("tipo")
        q_id = questao.get("id")

        if q_type == "multipla_escolha":
            opcoes = questao.get("opcoes", {})
            choices = list(opcoes.keys()) if isinstance(opcoes, dict) else opcoes
            answer = st.radio(
                "Selecione uma opcao",
                choices,
                key=f"q_{q_id}"
            )
            answers[q_id] = answer

        elif q_type == "verdadeiro_falso":
            answer = st.radio(
                "Selecione",
                ["Verdadeiro", "Falso"],
                key=f"q_{q_id}"
            )
            answers[q_id] = answer

        elif q_type == "resposta_curta":
            answer = st.text_input(
                "Sua resposta",
                key=f"q_{q_id}"
            )
            answers[q_id] = answer

        elif q_type == "codigo":
            answer = st.text_area(
                "Seu codigo",
                height=150,
                key=f"q_{q_id}"
            )
            answers[q_id] = answer

        st.markdown("---")

    st.session_state.current_answers = answers

    # Submit button
    if st.button("Enviar Prova", type="primary"):
        submit_prova(prova, answers)


def submit_prova(prova: dict, answers: dict):
    """Submit completed prova."""
    tentativa_id = st.session_state.get("tentativa_id")

    try:
        # Submit each answer
        for q_id, answer in answers.items():
            api.post(f"/mini-provas/tentativas/{tentativa_id}/answer", {
                "questao_id": q_id,
                "resposta": answer
            })

        # Finish attempt
        result = api.post(f"/mini-provas/tentativas/{tentativa_id}/finish")

        if "error" not in result:
            show_success(f"Prova finalizada! Pontos: {result.get('pontos_obtidos', 0)}")
            # Clean up session
            del st.session_state.current_prova
            del st.session_state.prova_start_time
            del st.session_state.current_answers
            if "tentativa_id" in st.session_state:
                del st.session_state.tentativa_id
            st.rerun()
        else:
            show_error(result.get("message", "Erro ao finalizar prova"))

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def main():
    """Main function."""
    render_miniprovas_page()


if __name__ == "__main__":
    main()
