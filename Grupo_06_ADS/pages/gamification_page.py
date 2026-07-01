"""
Gamification and Rankings Page.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from .session import SessionManager, api
from .styles import apply_dark_theme, COLORS
from .components import (
    render_leaderboard_item, render_medal,
    render_stat_card, render_progress_bar,
    render_empty_state, show_error
)


def render_gamification_page():
    """Render the gamification and rankings page."""
    apply_dark_theme()
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        st.warning("Por favor, faca login")
        return

    user = SessionManager.get_user()

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Rankings", "Medalhas", "Niveis", "Estilos"])

    with tab1:
        render_rankings_tab(user)

    with tab2:
        render_medals_tab(user)

    with tab3:
        render_levels_tab(user)

    with tab4:
        render_stats_tab(user)


def render_rankings_tab(user):
    """Render rankings tab."""
    st.subheader("Rankings")

    # Filter by scope
    col1, col2 = st.columns([3, 1])

    with col1:
        scope = st.selectbox(
            "Escopo",
            ["Global", "Minha Turma"],
            key="ranking_scope"
        )

    with col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Atualizar"):
            st.rerun()

    # Fetch leaderboard
    try:
        params = {"limit": 50}
        if scope == "Minha Turma":
            turmas = api.get("/turmas/my")
            if turmas and isinstance(turmas, list) and len(turmas) > 0:
                params["turma_id"] = turmas[0].get("id")

        leaderboard = api.get("/gamificacao/leaderboard", params)

        if leaderboard and not isinstance(leaderboard, dict):
            # Top 3 podium
            st.markdown("### Top 3")
            col1, col2, col3 = st.columns(3)

            for i, entry in enumerate(leaderboard[:3]):
                col = [col1, col2, col3][i]
                with col:
                    rank = entry.get("posicao", i + 1)
                    medal_emoji = ["1", "2", "3"][i]

                    st.markdown(f"""
                    <div style="text-align: center; padding: 1.5rem;
                         background: linear-gradient(135deg, #1a1f2e, #16202a);
                         border-radius: 16px; border: 2px solid {['#FFD700', '#C0C0C0', '#CD7F32'][i]};">
                        <div style="font-size: 2.5rem; font-weight: 700;
                             color: {['#FFD700', '#C0C0C0', '#CD7F32'][i]};">#{rank}</div>
                        <div style="font-size: 1.2rem; color: #ffffff; margin-top: 0.5rem;">
                            {entry.get("aluno_nome", "Aluno")}
                        </div>
                        <div style="color: #3B82F6; font-weight: 600; margin-top: 0.25rem;">
                            {entry.get("pontos", 0):,} pts
                        </div>
                        <div style="color: #8b98a5; font-size: 0.875rem;">
                            Nivel {entry.get("nivel", 1)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            # Full leaderboard
            st.markdown("### Ranking Completo")

            for entry in leaderboard[3:]:
                render_leaderboard_item(
                    rank=entry.get("posicao", 0),
                    name=entry.get("aluno_nome", "Aluno"),
                    points=entry.get("pontos", 0),
                    level=entry.get("nivel", 1),
                    medals=entry.get("medalhas", 0),
                    is_current_user=str(entry.get("aluno_id")) == str(user.id)
                )
        else:
            render_empty_state("Nenhum ranking disponivel", "R")

    except Exception as e:
        show_error(f"Erro ao carregar ranking: {str(e)}")


def render_medals_tab(user):
    """Render medals tab."""
    st.subheader("Suas Medalhas")

    col1, col2 = st.columns([3, 1])

    with col1:
        # User's medals
        try:
            conquistas = api.get("/gamificacao/conquistas")

            if conquistas and not isinstance(conquistas, dict):
                cols = st.columns(min(len(conquistas), 3))
                for i, c in enumerate(conquistas):
                    with cols[i % 3]:
                        medalha = c.get("medalha", {})
                        render_medal(
                            name=medalha.get("nome", "Medalha"),
                            description=medalha.get("descricao", ""),
                            icon=medalha.get("icone", "medal"),
                            color=medalha.get("cor", "#FFD700"),
                            earned=True
                        )
            else:
                render_empty_state("Nenhuma medalha conquistada ainda", "M")

        except Exception as e:
            show_error(f"Erro: {str(e)}")

    with col2:
        # All available medals
        st.markdown("**Medalhas Disponiveis**")
        try:
            medalhas = api.get("/gamificacao/medalhas")
            if medalhas and isinstance(medalhas, list):
                for m in medalhas[:5]:
                    st.markdown(f"""
                    <div style="padding: 0.5rem; border-left: 3px solid {m.get('cor', '#FFD700')};
                         margin-bottom: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 4px;">
                        <small style="color: #ffffff;">{m.get('nome')}</small><br>
                        <small style="color: #8b98a5;">{m.get('descricao', '')[:50]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception:
            pass


def render_levels_tab(user):
    """Render levels tab."""
    st.subheader("Sistema de Niveis")

    try:
        levels = api.get("/gamificacao/levels")
        stats = api.get(f"/gamificacao/stats/{user.id}")

        if levels and isinstance(levels, list):
            # Current level progress
            nivel_atual = stats.get("nivel_atual", {})
            pontos_atuais = nivel_atual.get("pontos_atuais", user.pontuacao_total)
            nivel_num = nivel_atual.get("nivel_atual", user.nivel)

            # Find current and next level
            current_level = next((l for l in levels if l.get("nivel") == nivel_num), levels[0])
            next_level = next((l for l in levels if l.get("nivel") == nivel_num + 1), None)

            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;
                 background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
                 border-radius: 16px; border: 1px solid #3B82F6; margin-bottom: 2rem;">
                <div style="font-size: 1rem; color: #8b98a5;">Nivel Atual</div>
                <div style="font-size: 4rem; font-weight: 700; color: #3B82F6;">{nivel_num}</div>
                <div style="font-size: 1.5rem; color: #ffffff; margin-top: 0.5rem;">
                    {current_level.get("titulo", current_level.get("nome", ""))}
                </div>
                <div style="color: #8b98a5; margin-top: 1rem;">
                    {pontos_atuais:,} pontos
                </div>
            </div>
            """, unsafe_allow_html=True)

            if next_level:
                progress = (pontos_atuais / next_level.get("pontos_necessarios", 100)) * 100
                render_progress_bar(
                    pontos_atuais,
                    next_level.get("pontos_necessarios", 100),
                    f"Proximo: {next_level.get('titulo', next_level.get('nome'))}"
                )

            st.markdown("---")

            # Level chart
            st.markdown("### Todos os Niveis")

            fig = go.Figure()

            level_names = [l.get("nome", f"Nivel {l.get('nivel')}") for l in levels]
            level_points = [l.get("pontos_necessarios", 0) for l in levels]

            fig.add_trace(go.Bar(
                x=level_names,
                y=level_points,
                marker_color=['#3B82F6' if l.get("nivel") <= nivel_num else '#2f3336' for l in levels],
                text=[f"{p:,} pts" for p in level_points],
                textposition='outside',
            ))

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e7e9ea'),
                xaxis=dict(gridcolor='#2f3336'),
                yaxis=dict(gridcolor='#2f3336'),
                margin=dict(t=50, b=50, l=50, r=50),
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        show_error(f"Erro ao carregar niveis: {str(e)}")


def render_stats_tab(user):
    """Render user stats tab."""
    st.subheader("Estatisticas")

    try:
        stats = api.get(f"/gamificacao/stats/{user.id}")

        col1, col2 = st.columns(2)

        with col1:
            # Donut chart for points breakdown
            labels = ['Desafios', 'Provas', 'Missoes', 'Medalhas']
            values = [
                stats.get('desafios_completados', 0) * 100,
                stats.get('provas_completadas', 0) * 50,
                stats.get('missoes_completadas', 0) * 200,
                stats.get('medalhas', 0) * 50,
            ]
            values = [max(v, 0) for v in values]

            if sum(values) > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=.4,
                    marker_colors=['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B']
                )])

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e7e9ea'),
                    showlegend=True,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.2),
                    height=300
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Complete atividades para ver a distribuicao de pontos")

        with col2:
            # Stats summary
            st.metric("Total de Pontos", stats.get("pontos_totais", 0))
            st.metric("Desafios Completados", stats.get("desafios_completados", 0))
            st.metric("Provas Realizadas", stats.get("provas_completadas", 0))
            st.metric("Missoes Completadas", stats.get("missoes_completadas", 0))
            st.metric("Medalhas", stats.get("medalhas", 0))

    except Exception as e:
        show_error(f"Erro ao carregar estatisticas: {str(e)}")


def main():
    """Main function."""
    render_gamification_page()


if __name__ == "__main__":
    main()
