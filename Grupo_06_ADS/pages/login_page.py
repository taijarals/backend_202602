"""
Login and Registration Page.
"""
import streamlit as st
from .session import SessionManager, api
from .styles import apply_dark_theme
from .components import show_error, show_success


def render_login_page():
    """Render the login/registration page."""
    apply_dark_theme()
    SessionManager.init_session()

    st.title("EduGame Platform")
    st.markdown("---")

    # Create tabs for login and register
    tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])

    with tab1:
        render_login_form()

    with tab2:
        render_register_form()


def render_login_form():
    """Render login form."""
    st.subheader("Entrar na sua conta")

    email = st.text_input("Email", placeholder="seu@email.com", key="login_email")
    password = st.text_input("Senha", type="password", placeholder="******", key="login_password")

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("Entrar", use_container_width=True, type="primary"):
            if not email or not password:
                show_error("Preencha todos os campos")
            else:
                with st.spinner("Entrando..."):
                    try:
                        response = api.post("/auth/login", {
                            "email": email,
                            "password": password
                        })

                        if "error" in response:
                            show_error(response.get("message", "Erro ao entrar"))
                        elif "access_token" in response:
                            token = response["access_token"]
                            user = response.get("user", {})
                            SessionManager.login(user, token)
                            show_success("Bem-vindo!")
                            st.rerun()
                        else:
                            show_error("Erro ao entrar")
                    except Exception as e:
                        show_error(f"Erro de conexao: {str(e)}")

    with col2:
        st.markdown("""
        <div style="color: #8b98a5; font-size: 0.75rem; padding-top: 0.5rem;">
            Esqueceu a senha?<br>
            <a href="#" style="color: #3B82F6;">Recuperar acesso</a>
        </div>
        """, unsafe_allow_html=True)


def render_register_form():
    """Render registration form."""
    st.subheader("Criar nova conta")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome completo", placeholder="Seu nome", key="reg_nome")
        email = st.text_input("Email", placeholder="seu@email.com", key="reg_email")

    with col2:
        role = st.selectbox("Tipo de conta", ["student", "professor"],
                           format_func=lambda x: "Aluno" if x == "student" else "Professor",
                           key="reg_role")
        password = st.text_input("Senha", type="password", placeholder="Minimo 6 caracteres", key="reg_password")

    confirm_password = st.text_input("Confirmar senha", type="password", placeholder="******", key="reg_confirm")

    if st.button("Criar Conta", use_container_width=True, type="primary"):
        if not all([nome, email, password, confirm_password]):
            show_error("Preencha todos os campos")
        elif password != confirm_password:
            show_error("As senhas nao coincidem")
        elif len(password) < 6:
            show_error("A senha deve ter pelo menos 6 caracteres")
        else:
            with st.spinner("Criando conta..."):
                try:
                    response = api.post("/auth/register", {
                        "nome": nome,
                        "email": email,
                        "password": password,
                        "role": role
                    })

                    if "error" in response:
                        show_error(response.get("message", "Erro ao criar conta"))
                    elif "access_token" in response:
                        token = response["access_token"]
                        user = response.get("user", {})
                        SessionManager.login(user, token)
                        show_success("Conta criada com sucesso!")
                        st.rerun()
                    else:
                        show_error("Erro ao criar conta")
                except Exception as e:
                    show_error(f"Erro de conexao: {str(e)}")

    st.markdown("""
    <div style="margin-top: 1rem; color: #8b98a5; font-size: 0.75rem;">
        Ao criar uma conta, voce concorda com nossos
        <a href="#" style="color: #3B82F6;">Termos de Uso</a> e
        <a href="#" style="color: #3B82F6;">Politica de Privacidade</a>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main function for login page."""
    render_login_page()


if __name__ == "__main__":
    main()
