"""
Enquetes (Polls) Page.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from .session import SessionManager, api
from .styles import apply_dark_theme, COLORS
from .components import render_empty_state, render_badge, show_error, show_success


def render_polls_page():
    """Render polls page."""
    apply_dark_theme()
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        st.warning("Por favor, faca login")
        return

    user = SessionManager.get_user()
    st.title("Enquetes")

    if user.role == "professor":
        render_professor_polls(user)
    else:
        render_student_polls(user)


def render_student_polls(user):
    """Render student's polls view."""
    tab1, tab2 = st.tabs(["Ativas", "Finalizadas"])

    with tab1:
        render_active_polls(user)

    with tab2:
        render_closed_polls(user)


def render_active_polls(user):
    """Render active polls for voting."""
    try:
        enquetes = api.get("/enquetes/active")

        if enquetes and isinstance(enquetes, list):
            for enquete in enquetes:
                render_poll_voting_card(enquete, user)
        else:
            render_empty_state("Nenhuma enquete ativa", "P")

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def render_poll_voting_card(enquete: dict, user):
    """Render a poll card for voting."""
    with st.container():
        st.markdown(f"""
        <div class="card">
            <h4 style="margin: 0; color: #ffffff;">{enquete.get('titulo')}</h4>
            <p style="color: #8b98a5; margin-top: 0.5rem;">{enquete.get('descricao', '')}</p>
            {f'<small style="color: #F59E0B;">Encerra: {enquete.get("fim")}</small>' if enquete.get('fim') else ''}
        </div>
        """, unsafe_allow_html=True)

        # Check if already voted
        try:
            has_voted = False
            # Fetch user votes to check
            stats = api.get(f"/enquetes/{enquete.get('id')}/stats")

            if stats and not isinstance(stats, dict):
                has_voted = False  # Would need proper check
        except Exception:
            has_voted = False

        opcoes = enquete.get("opcoes", [])

        if not has_voted:
            st.markdown("**Selecione uma opcao:**")

            selected = None
            for opcao in opcoes:
                if st.button(
                    opcao.get("texto", ""),
                    key=f"opt_{enquete.get('id')}_{opcao.get('id')}"
                ):
                    selected = opcao.get("id")

            if selected:
                cast_vote(enquete.get("id"), selected, user.id)
        else:
            st.info("Voce ja votou nesta enquete")
            render_poll_results(enquete)

        st.markdown("---")


def render_poll_results(enquete: dict):
    """Render poll results visualization."""
    opcoes = enquete.get("opcoes", [])
    total_votos = enquete.get("total_votos", 0)

    if opcoes and total_votos > 0:
        labels = [o.get("texto", "") for o in opcoes]
        values = [o.get("votos", 0) for o in opcoes]

        fig = go.Figure(data=[go.Bar(
            x=values,
            y=labels,
            orientation='h',
            marker_color=['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'][:len(opcoes)],
            text=[f"{v} ({v/total_votos*100:.1f}%)" for v in values],
            textposition='outside',
        )])

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e7e9ea'),
            xaxis=dict(gridcolor='#2f3336', title='Votos'),
            yaxis=dict(gridcolor='#2f3336'),
            margin=dict(t=30, b=30, l=30, r=50),
            height=200
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write(f"**Total de votos:** {total_votos}")


def render_closed_polls(user):
    """Render closed/finished polls."""
    try:
        enquetes = api.get("/enquetes")

        if enquetes and isinstance(enquetes, list):
            closed = [e for e in enquetes if not e.get("ativa")]

            if closed:
                for enquete in closed:
                    with st.expander(f"**{enquete.get('titulo')}** - Finalizada"):
                        render_poll_results(enquete)
            else:
                render_empty_state("Nenhuma enquete finalizada", "-")
        else:
            render_empty_state("Nenhuma enquete finalizada", "-")

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def render_professor_polls(user):
    """Render professor's polls management view."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Suas Enquetes")
    with col2:
        if st.button("Nova Enquete", type="primary"):
            st.session_state.show_create_poll = True

    st.markdown("---")

    # Create poll form
    if st.session_state.get("show_create_poll"):
        render_create_poll_form(user)

    # List existing polls
    try:
        enquetes = api.get(f"/enquetes?professor_id={user.id}")

        if enquetes and isinstance(enquetes, list):
            for enquete in enquetes:
                render_professor_poll_card(enquete)
        else:
            render_empty_state("Nenhuma enquete criada", "P")

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def render_professor_poll_card(enquete: dict):
    """Render a poll card for professor."""
    status = "Ativa" if enquete.get("ativa") else "Finalizada"
    status_color = "success" if enquete.get("ativa") else "warning"

    with st.expander(f"**{enquete.get('titulo')}**"):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**Descricao:** {enquete.get('descricao', 'N/A')}")
            render_badge(status, status_color)

            # Show stats
            try:
                stats = api.get(f"/enquetes/{enquete.get('id')}/stats")
                if stats and not isinstance(stats, dict):
                    st.write(f"**Total de votos:** {stats.get('total_votos', 0)}")
                    st.write(f"**Participacao:** {stats.get('participacao_percentual', 0):.1f}%")
            except Exception:
                pass

        with col2:
            if enquete.get("ativa"):
                if st.button("Fechar Enquete", key=f"close_{enquete.get('id')}"):
                    close_poll(enquete.get("id"))

            if st.button("Ver Resultados", key=f"res_{enquete.get('id')}"):
                st.session_state.view_results = enquete

        st.markdown("---")

        # Show results inline
        render_poll_results(enquete)


def render_create_poll_form(user):
    """Render create poll form."""
    st.subheader("Nova Enquete")

    with st.form("create_poll"):
        titulo = st.text_input("Titulo", placeholder="Pergunta da enquete")
        descricao = st.text_area("Descricao", placeholder="Descricao adicional")

        col1, col2 = st.columns(2)

        with col1:
            turma = st.selectbox("Turma (opcional)", ["Nenhuma"] + _get_turmas(user))

        with col2:
            multipla = st.checkbox("Multipla escolha", value=False)
            anonima = st.checkbox("Anonima", value=False)

        st.markdown("**Opcoes** (uma por linha)")
        opcoes_text = st.text_area("", placeholder="Opcao 1\nOpcao 2\nOpcao 3", height=100)

        prazo = st.date_input("Prazo (opcional)", value=None)

        submit = st.form_submit_button("Criar Enquete", type="primary")

        if submit:
            if not titulo or not opcoes_text:
                show_error("Titulo e opcoes sao obrigatorios")
            else:
                opcoes_list = [o.strip() for o in opcoes_text.split('\n') if o.strip()]

                if len(opcoes_list) < 2:
                    show_error("Adicione pelo menos 2 opcoes")
                else:
                    try:
                        data = {
                            "titulo": titulo,
                            "descricao": descricao,
                            "professor_id": str(user.id),
                            "opcoes": opcoes_list,
                            "multipla_escolha": multipla,
                            "anonima": anonima
                        }

                        if turma != "Nenhuma":
                            data["turma_id"] = turma
                        if prazo:
                            data["fim"] = str(prazo)

                        result = api.post("/enquetes", data)

                        if "error" not in result:
                            show_success("Enquete criada!")
                            st.session_state.show_create_poll = False
                            st.rerun()
                        else:
                            show_error(result.get("message", "Erro ao criar enquete"))

                    except Exception as e:
                        show_error(f"Erro: {str(e)}")


def cast_vote(enquete_id: str, opcao_id: str, aluno_id: str):
    """Cast a vote in a poll."""
    try:
        result = api.post(f"/enquetes/{enquete_id}/vote", {
            "opcao_id": opcao_id
        })

        if "error" not in result:
            show_success("Voto registrado!")
            st.rerun()
        else:
            show_error(result.get("message", "Erro ao votar"))

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def close_poll(enquete_id: str):
    """Close a poll."""
    try:
        result = api.post(f"/enquetes/{enquete_id}/close")

        if "error" not in result:
            show_success("Enquete finalizada!")
            st.rerun()
        else:
            show_error(result.get("message", "Erro ao finalizar"))

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def _get_turmas(user) -> list:
    """Get user's turmas."""
    try:
        turmas = api.get(f"/turmas?professor_id={user.id}")
        if isinstance(turmas, list):
            return [t.get("id") for t in turmas]
    except Exception:
        pass
    return []


def main():
    """Main function."""
    render_polls_page()


if __name__ == "__main__":
    main()
