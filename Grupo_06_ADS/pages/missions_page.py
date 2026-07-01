"""
Missoes (Missions) Page.
"""
import streamlit as st
from .session import SessionManager, api
from .styles import apply_dark_theme, COLORS
from .components import (
    render_empty_state, render_progress_bar,
    render_badge, show_error, show_success
)


def render_missions_page():
    """Render missions page."""
    apply_dark_theme()
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        st.warning("Por favor, faca login")
        return

    user = SessionManager.get_user()
    st.title("Missoes")

    if user.role == "professor":
        render_professor_missions(user)
    else:
        render_student_missions(user)


def render_student_missions(user):
    """Render student's missions view."""
    tab1, tab2 = st.tabs(["Missoes Ativas", "Completadas"])

    with tab1:
        render_active_missions(user)

    with tab2:
        render_completed_missions(user)


def render_active_missions(user):
    """Render active missions for student."""
    try:
        missoes = api.get("/missoes/available")

        if missoes and isinstance(missoes, list):
            active = [m for m in missoes if m.get("status") in ["em_progresso", "nao_iniciada"]]

            if not active:
                render_empty_state("Nenhuma missao disponivel", "G")
                return

            for missao in active:
                render_mission_card(missao, user)

        else:
            render_empty_state("Nenhuma missao disponivel", "G")

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def render_completed_missions(user):
    """Render completed missions for student."""
    try:
        missoes = api.get("/missoes/available")

        if missoes and isinstance(missoes, list):
            completed = [m for m in missoes if m.get("status") == "completa"]

            if completed:
                for missao in completed:
                    st.markdown(f"""
                    <div class="card" style="border-left: 4px solid #10B981;">
                        <h4 style="margin: 0; color: #ffffff;">{missao.get('titulo')}</h4>
                        <p style="color: #8b98a5; margin-top: 0.5rem;">{missao.get('pontos_obtidos', 0)} pontos conquistados</p>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                render_empty_state("Nenhuma missao completada ainda", "-")

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def render_mission_card(missao: dict, user):
    """Render a mission card."""
    status = missao.get("status", "nao_iniciada")
    progress = missao.get("progresso_atual", 0)
    etapas = missao.get("etapas", [])
    etapas_completas = missao.get("etapas_completas", 0)

    status_color = {
        "nao_iniciada": "#F59E0B",
        "em_progresso": "#3B82F6",
        "completa": "#10B981"
    }.get(status, "#8b98a5")

    with st.expander(f"**{missao.get('titulo')}** - {etapas_completas}/{len(etapas)} etapas"):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"""
            <div>
                <span class="badge" style="background: {status_color}22; color: {status_color};
                      border-color: {status_color}44;">{status.replace('_', ' ').title()}</span>
            </div>
            """, unsafe_allow_html=True)

            st.write(missao.get("descricao"))

            st.markdown("**Etapas:**")
            for i, etapa in enumerate(etapas):
                etapa_status = etapa.get("status") or (
                    "completa" if i < etapas_completas else (
                        "em_progresso" if i == etapas_completas else "pendente"
                    )
                )

                etapa_color = "#10B981" if etapa_status == "completa" else (
                    "#3B82F6" if etapa_status == "em_progresso" else "#2f3336"
                )

                checkmark = "-" if etapa_status == "completa" else (
                    "=" if etapa_status == "em_progresso" else "O"
                )

                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.5rem 0;">
                    <div style="width: 24px; height: 24px; border-radius: 50%;
                         background: {etapa_color}; display: flex; align-items: center;
                         justify-content: center; color: white; font-size: 0.75rem;">
                        {checkmark}
                    </div>
                    <span style="color: #e7e9ea;">{etapa.get('titulo')}</span>
                    <span style="color: #8b98a5; font-size: 0.75rem;">({etapa.get('pontos')} pts)</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.metric("Recompensa", f"{missao.get('pontos_recompensa', 0)} pts")
            st.metric("Dificuldade", missao.get("nivel_dificuldade", 1))

            render_progress_bar(etapas_completas, len(etapas), "Progresso")

            if st.button("Continuar", key=f"cont_{missao.get('id')}", type="primary"):
                start_mission_step(missao, etapas_completas, user)


def start_mission_step(missao: dict, step_index: int, user):
    """Start working on a mission step."""
    etapas = missao.get("etapas", [])
    if step_index < len(etapas):
        etapa = etapas[step_index]

        try:
            result = api.post(f"/missoes/{missao.get('id')}/etapas/{etapa.get('id')}/start")

            if "error" not in result:
                st.session_state.current_etapa = etapa
                st.session_state.current_missao = missao
                show_success("Etapa iniciada!")
            else:
                show_error(result.get("message", "Erro ao iniciar etapa"))

        except Exception as e:
            show_error(f"Erro: {str(e)}")


def render_professor_missions(user):
    """Render professor's missions view."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Missoes Criadas")

    with col2:
        if st.button("Nova Missao", type="primary"):
            st.session_state.show_create_mission = True

    st.markdown("---")

    try:
        missoes = api.get(f"/missoes?professor_id={user.id}")

        if missoes and isinstance(missoes, list):
            for missao in missoes:
                with st.expander(f"**{missao.get('titulo')}**"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Descricao:** {missao.get('descricao')}")
                        st.write(f"**Etapas:** {len(missao.get('etapas', []))}")

                    with col2:
                        st.metric("Pontos", missao.get("pontos_recompensa", 0))

                        if st.button("Editar", key=f"edit_m_{missao.get('id')}"):
                            st.session_state.edit_mission = missao

                        if st.button("Ver Progresso", key=f"prog_m_{missao.get('id')}"):
                            st.session_state.mission_progress = missao
        else:
            render_empty_state("Nenhuma missao criada", "G", "Criar Missao",
                             lambda: setattr(st.session_state, 'show_create_mission', True))

    except Exception as e:
        show_error(f"Erro: {str(e)}")


def main():
    """Main function."""
    render_missions_page()


if __name__ == "__main__":
    main()
