import streamlit as st
import requests
import pandas as pd

URL = "http://localhost:8000/api"

HEADERS = {
    "X-API-Token": "chave-secreta-123"
}

st.set_page_config(
    page_title="Gamificação",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Módulo de Gamificação")


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def mostrar_erro(resposta):
    try:
        erro = resposta.json()

        if "detail" in erro:
            st.error(erro["detail"])

        elif "mensagem" in erro:
            st.error(erro["mensagem"])

        elif "erro" in erro:
            st.error(erro["erro"])

        else:
            st.error(resposta.text)

    except Exception:
        st.error(resposta.text)


def get_api(endpoint):
    return requests.get(
        f"{URL}{endpoint}",
        headers=HEADERS
    )


def post_api(endpoint, dados):
    return requests.post(
        f"{URL}{endpoint}",
        json=dados,
        headers=HEADERS
    )


# ==================================================
# SESSION STATE
# ==================================================

if "aluno_id_selecionado" not in st.session_state:
    st.session_state["aluno_id_selecionado"] = 1

if "input_pontuar_aluno" not in st.session_state:
    st.session_state["input_pontuar_aluno"] = 1

if "input_dashboard_aluno" not in st.session_state:
    st.session_state["input_dashboard_aluno"] = 1

if "questoes_prova_carregadas" not in st.session_state:
    st.session_state["questoes_prova_carregadas"] = []

if "prova_id_carregada" not in st.session_state:
    st.session_state["prova_id_carregada"] = None


# ==================================================
# ABAS PRINCIPAIS
# ==================================================

aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs(
    [
        "Cadastrar Aluno",
        "Registrar Atividade",
        "Dashboard do Aluno",
        "Alunos",
        "Gestão Acadêmica",
        "Mini-Provas",
        "Ranking",
        "Estatísticas"
    ]
)


# ==================================================
# ABA 1 - CADASTRO DE ALUNOS
# ==================================================

with aba1:

    st.subheader("Cadastro de Alunos")

    with st.form("cadastro_aluno"):

        nome = st.text_input("Nome")

        email = st.text_input("Email")

        cadastrar = st.form_submit_button(
            "Cadastrar"
        )

        if cadastrar:

            if not nome or not email:

                st.warning(
                    "Preencha nome e email."
                )

            else:

                try:

                    resposta = post_api(
                        "/alunos",
                        {
                            "nome": nome,
                            "email": email
                        }
                    )

                    if resposta.status_code == 200:

                        aluno = resposta.json()

                        st.session_state["aluno_id_selecionado"] = aluno["id"]
                        st.session_state["input_pontuar_aluno"] = aluno["id"]
                        st.session_state["input_dashboard_aluno"] = aluno["id"]

                        st.success(
                            f"Aluno cadastrado com sucesso! ID: {aluno['id']}"
                        )

                        st.info(
                            "O ID foi preenchido automaticamente nas abas de atividade e dashboard."
                        )

                    else:

                        mostrar_erro(resposta)

                except Exception as e:

                    st.error(
                        f"Erro ao cadastrar aluno: {e}"
                    )


# ==================================================
# ABA 2 - REGISTRAR ATIVIDADE
# ==================================================

with aba2:

    st.subheader("Registrar Atividade")

    st.info(
        f"Aluno selecionado: ID {st.session_state['input_pontuar_aluno']}"
    )

    with st.form("pontuar"):

        aluno = st.number_input(
            "ID do Aluno",
            min_value=1,
            step=1,
            key="input_pontuar_aluno"
        )

        atividade = st.text_input(
            "Atividade"
        )

        pontos = st.number_input(
            "Pontos",
            min_value=10,
            step=10
        )

        pontuar = st.form_submit_button(
            "Pontuar"
        )

        if pontuar:

            if not atividade:

                st.warning(
                    "Informe a atividade."
                )

            else:

                try:

                    resposta = post_api(
                        "/pontuar",
                        {
                            "aluno_id": aluno,
                            "atividade": atividade,
                            "pontos_ganhos": pontos
                        }
                    )

                    if resposta.status_code == 200:

                        dados = resposta.json()

                        st.session_state["aluno_id_selecionado"] = aluno

                        st.success(
                            dados["mensagem"]
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.metric(
                                "Pontos Computados",
                                dados["pontos_finais"]
                            )

                        with col2:

                            st.metric(
                                "Nível Atual",
                                dados["nivel_atualizado"]
                            )

                        if dados["subiu_de_nivel"]:

                            st.balloons()

                            st.success(
                                "🎉 O aluno subiu de nível!"
                            )

                        if dados["medalhas_desbloqueadas"]:

                            st.info(
                                "🏅 Medalhas conquistadas:"
                            )

                            for medalha in dados["medalhas_desbloqueadas"]:

                                st.write(
                                    f"• {medalha}"
                                )

                    else:

                        mostrar_erro(resposta)

                except Exception as e:

                    st.error(
                        f"Erro ao pontuar: {e}"
                    )


# ==================================================
# ABA 3 - DASHBOARD DO ALUNO
# ==================================================

with aba3:

    st.subheader("Dashboard do Aluno")

    aluno_dashboard = st.number_input(
        "ID do Aluno para consultar",
        min_value=1,
        step=1,
        key="input_dashboard_aluno"
    )

    buscar_dashboard = st.button(
        "Buscar Dashboard"
    )

    if buscar_dashboard:

        try:

            resposta = get_api(
                f"/aluno/{aluno_dashboard}"
            )

            if resposta.status_code == 200:

                dados = resposta.json()

                st.success(
                    f"Dashboard carregado para {dados['nome']}"
                )

                st.write(
                    f"**Email:** {dados['email']}"
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Pontos Totais",
                        dados["pontos"]
                    )

                with col2:

                    st.metric(
                        "Nível",
                        dados["nivel"]
                    )

                with col3:

                    st.metric(
                        "Título",
                        dados["titulo"]
                    )

                with col4:

                    st.metric(
                        "Streak",
                        dados["streak"]
                    )

                if dados["ultima_atividade"]:

                    st.info(
                        f"Última atividade: {dados['ultima_atividade']}"
                    )

                else:

                    st.warning(
                        "Este aluno ainda não realizou nenhuma atividade."
                    )

                st.divider()

                st.subheader("🏅 Medalhas Conquistadas")

                medalhas = dados["medalhas"]

                if len(medalhas) == 0:

                    st.warning(
                        "Este aluno ainda não conquistou medalhas."
                    )

                else:

                    df_medalhas = pd.DataFrame(medalhas)

                    st.dataframe(
                        df_medalhas,
                        use_container_width=True
                    )

            else:

                mostrar_erro(resposta)

        except Exception as e:

            st.error(
                f"Erro ao buscar dashboard: {e}"
            )


# ==================================================
# ABA 4 - LISTAGEM DE ALUNOS
# ==================================================

with aba4:

    st.subheader("Alunos Cadastrados")

    atualizar = st.button(
        "Atualizar Lista de Alunos"
    )

    if atualizar:

        try:

            resposta = get_api(
                "/alunos"
            )

            if resposta.status_code == 200:

                alunos = resposta.json()

                if len(alunos) == 0:

                    st.warning(
                        "Nenhum aluno cadastrado ainda."
                    )

                else:

                    df_alunos = pd.DataFrame(alunos)

                    st.dataframe(
                        df_alunos,
                        use_container_width=True
                    )

            else:

                mostrar_erro(resposta)

        except Exception as e:

            st.error(
                f"Erro ao listar alunos: {e}"
            )


# ==================================================
# ABA 5 - GESTÃO ACADÊMICA
# ==================================================

with aba5:

    st.subheader("Gestão Acadêmica")

    st.write(
        "Nesta área ficam as entidades globais obrigatórias: Professor, Disciplina, Turma e vínculo entre aluno e turma."
    )

    subaba1, subaba2, subaba3, subaba4 = st.tabs(
        [
            "Professores",
            "Disciplinas",
            "Turmas",
            "Alunos por Turma"
        ]
    )

    # ==============================================
    # PROFESSORES
    # ==============================================

    with subaba1:

        st.markdown("### Cadastro de Professores")

        with st.form("form_cadastro_professor"):

            nome_professor = st.text_input(
                "Nome do Professor"
            )

            email_professor = st.text_input(
                "Email do Professor"
            )

            cadastrar_professor = st.form_submit_button(
                "Cadastrar Professor"
            )

            if cadastrar_professor:

                if not nome_professor or not email_professor:

                    st.warning(
                        "Preencha nome e email do professor."
                    )

                else:

                    try:

                        resposta = post_api(
                            "/professores",
                            {
                                "nome": nome_professor,
                                "email": email_professor
                            }
                        )

                        if resposta.status_code == 200:

                            professor = resposta.json()

                            st.success(
                                f"Professor cadastrado com sucesso! ID: {professor['id']}"
                            )

                        else:

                            mostrar_erro(resposta)

                    except Exception as e:

                        st.error(
                            f"Erro ao cadastrar professor: {e}"
                        )

        st.divider()

        st.markdown("### Professores Cadastrados")

        if st.button("Listar Professores"):

            try:

                resposta = get_api(
                    "/professores"
                )

                if resposta.status_code == 200:

                    professores = resposta.json()

                    if len(professores) == 0:

                        st.warning(
                            "Nenhum professor cadastrado."
                        )

                    else:

                        st.dataframe(
                            pd.DataFrame(professores),
                            use_container_width=True
                        )

                else:

                    mostrar_erro(resposta)

            except Exception as e:

                st.error(
                    f"Erro ao listar professores: {e}"
                )

    # ==============================================
    # DISCIPLINAS
    # ==============================================

    with subaba2:

        st.markdown("### Cadastro de Disciplinas")

        with st.form("form_cadastro_disciplina"):

            nome_disciplina = st.text_input(
                "Nome da Disciplina"
            )

            descricao_disciplina = st.text_area(
                "Descrição da Disciplina"
            )

            cadastrar_disciplina = st.form_submit_button(
                "Cadastrar Disciplina"
            )

            if cadastrar_disciplina:

                if not nome_disciplina:

                    st.warning(
                        "Preencha o nome da disciplina."
                    )

                else:

                    try:

                        resposta = post_api(
                            "/disciplinas",
                            {
                                "nome": nome_disciplina,
                                "descricao": descricao_disciplina
                            }
                        )

                        if resposta.status_code == 200:

                            disciplina = resposta.json()

                            st.success(
                                f"Disciplina cadastrada com sucesso! ID: {disciplina['id']}"
                            )

                        else:

                            mostrar_erro(resposta)

                    except Exception as e:

                        st.error(
                            f"Erro ao cadastrar disciplina: {e}"
                        )

        st.divider()

        st.markdown("### Disciplinas Cadastradas")

        if st.button("Listar Disciplinas"):

            try:

                resposta = get_api(
                    "/disciplinas"
                )

                if resposta.status_code == 200:

                    disciplinas = resposta.json()

                    if len(disciplinas) == 0:

                        st.warning(
                            "Nenhuma disciplina cadastrada."
                        )

                    else:

                        st.dataframe(
                            pd.DataFrame(disciplinas),
                            use_container_width=True
                        )

                else:

                    mostrar_erro(resposta)

            except Exception as e:

                st.error(
                    f"Erro ao listar disciplinas: {e}"
                )

    # ==============================================
    # TURMAS
    # ==============================================

    with subaba3:

        st.markdown("### Cadastro de Turmas")

        st.info(
            "Antes de cadastrar uma turma, cadastre pelo menos um professor e uma disciplina."
        )

        with st.form("form_cadastro_turma"):

            nome_turma = st.text_input(
                "Nome da Turma"
            )

            professor_id = st.number_input(
                "ID do Professor",
                min_value=1,
                step=1
            )

            disciplina_id = st.number_input(
                "ID da Disciplina",
                min_value=1,
                step=1
            )

            cadastrar_turma = st.form_submit_button(
                "Cadastrar Turma"
            )

            if cadastrar_turma:

                if not nome_turma:

                    st.warning(
                        "Preencha o nome da turma."
                    )

                else:

                    try:

                        resposta = post_api(
                            "/turmas",
                            {
                                "nome": nome_turma,
                                "professor_id": professor_id,
                                "disciplina_id": disciplina_id
                            }
                        )

                        if resposta.status_code == 200:

                            turma = resposta.json()

                            st.success(
                                f"Turma cadastrada com sucesso! ID: {turma['id']}"
                            )

                        else:

                            mostrar_erro(resposta)

                    except Exception as e:

                        st.error(
                            f"Erro ao cadastrar turma: {e}"
                        )

        st.divider()

        st.markdown("### Turmas Cadastradas")

        if st.button("Listar Turmas"):

            try:

                resposta = get_api(
                    "/turmas"
                )

                if resposta.status_code == 200:

                    turmas = resposta.json()

                    if len(turmas) == 0:

                        st.warning(
                            "Nenhuma turma cadastrada."
                        )

                    else:

                        st.dataframe(
                            pd.DataFrame(turmas),
                            use_container_width=True
                        )

                else:

                    mostrar_erro(resposta)

            except Exception as e:

                st.error(
                    f"Erro ao listar turmas: {e}"
                )

    # ==============================================
    # ALUNOS POR TURMA
    # ==============================================

    with subaba4:

        st.markdown("### Vincular Aluno à Turma")

        with st.form("form_vincular_aluno_turma"):

            turma_id_vinculo = st.number_input(
                "ID da Turma",
                min_value=1,
                step=1
            )

            aluno_id_vinculo = st.number_input(
                "ID do Aluno",
                min_value=1,
                step=1
            )

            vincular = st.form_submit_button(
                "Vincular Aluno"
            )

            if vincular:

                try:

                    resposta = post_api(
                        "/turmas/alunos",
                        {
                            "turma_id": turma_id_vinculo,
                            "aluno_id": aluno_id_vinculo
                        }
                    )

                    if resposta.status_code == 200:

                        dados = resposta.json()

                        st.success(
                            dados["mensagem"]
                        )

                    else:

                        mostrar_erro(resposta)

                except Exception as e:

                    st.error(
                        f"Erro ao vincular aluno à turma: {e}"
                    )

        st.divider()

        st.markdown("### Consultar Alunos de uma Turma")

        turma_id_consulta = st.number_input(
            "ID da Turma para consultar",
            min_value=1,
            step=1,
            key="turma_id_consulta"
        )

        if st.button("Listar Alunos da Turma"):

            try:

                resposta = get_api(
                    f"/turmas/{turma_id_consulta}/alunos"
                )

                if resposta.status_code == 200:

                    alunos_turma = resposta.json()

                    if len(alunos_turma) == 0:

                        st.warning(
                            "Nenhum aluno vinculado a esta turma."
                        )

                    else:

                        st.dataframe(
                            pd.DataFrame(alunos_turma),
                            use_container_width=True
                        )

                else:

                    mostrar_erro(resposta)

            except Exception as e:

                st.error(
                    f"Erro ao listar alunos da turma: {e}"
                )


# ==================================================
# ABA 6 - MINI-PROVAS GAMIFICADAS
# ==================================================

with aba6:

    st.subheader("Mini-Provas Gamificadas")

    st.write(
        "Nesta área é possível criar provas, cadastrar questões, responder provas e transformar acertos em pontos de gamificação."
    )

    prova_aba1, prova_aba2, prova_aba3, prova_aba4, prova_aba5 = st.tabs(
        [
            "Criar Prova",
            "Cadastrar Questões",
            "Responder Prova",
            "Tentativas",
            "Estatísticas"
        ]
    )

    # ==============================================
    # CRIAR PROVA
    # ==============================================

    with prova_aba1:

        st.markdown("### Criar Mini-Prova")

        st.info(
            "Antes de criar uma prova, cadastre professor e disciplina na aba Gestão Acadêmica."
        )

        with st.form("form_criar_prova"):

            titulo_prova = st.text_input(
                "Título da Prova"
            )

            descricao_prova = st.text_area(
                "Descrição da Prova"
            )

            professor_id_prova = st.number_input(
                "ID do Professor",
                min_value=1,
                step=1,
                key="professor_id_prova"
            )

            disciplina_id_prova = st.number_input(
                "ID da Disciplina",
                min_value=1,
                step=1,
                key="disciplina_id_prova"
            )

            duracao_minutos = st.number_input(
                "Duração em minutos",
                min_value=1,
                step=1,
                value=10
            )

            pontos_por_questao = st.number_input(
                "Pontos por Questão",
                min_value=1,
                step=1,
                value=10
            )

            ativa = st.checkbox(
                "Prova ativa",
                value=True
            )

            criar_prova = st.form_submit_button(
                "Criar Prova"
            )

            if criar_prova:

                if not titulo_prova:

                    st.warning(
                        "Informe o título da prova."
                    )

                else:

                    try:

                        resposta = post_api(
                            "/provas",
                            {
                                "titulo": titulo_prova,
                                "descricao": descricao_prova,
                                "professor_id": professor_id_prova,
                                "disciplina_id": disciplina_id_prova,
                                "duracao_minutos": duracao_minutos,
                                "pontos_por_questao": pontos_por_questao,
                                "ativa": ativa
                            }
                        )

                        if resposta.status_code == 200:

                            prova = resposta.json()

                            st.success(
                                f"Prova criada com sucesso! ID: {prova['id']}"
                            )

                        else:

                            mostrar_erro(resposta)

                    except Exception as e:

                        st.error(
                            f"Erro ao criar prova: {e}"
                        )

        st.divider()

        st.markdown("### Provas Cadastradas")

        if st.button("Listar Provas"):

            try:

                resposta = get_api(
                    "/provas"
                )

                if resposta.status_code == 200:

                    provas = resposta.json()

                    if len(provas) == 0:

                        st.warning(
                            "Nenhuma prova cadastrada."
                        )

                    else:

                        st.dataframe(
                            pd.DataFrame(provas),
                            use_container_width=True
                        )

                else:

                    mostrar_erro(resposta)

            except Exception as e:

                st.error(
                    f"Erro ao listar provas: {e}"
                )

    # ==============================================
    # CADASTRAR QUESTÕES
    # ==============================================

    with prova_aba2:

        st.markdown("### Cadastrar Questão na Prova")

        with st.form("form_cadastrar_questao"):

            prova_id_questao = st.number_input(
                "ID da Prova",
                min_value=1,
                step=1,
                key="prova_id_questao"
            )

            ordem_questao = st.number_input(
                "Ordem da Questão",
                min_value=1,
                step=1,
                value=1
            )

            enunciado = st.text_area(
                "Enunciado"
            )

            alternativa_a = st.text_input(
                "Alternativa A"
            )

            alternativa_b = st.text_input(
                "Alternativa B"
            )

            alternativa_c = st.text_input(
                "Alternativa C"
            )

            alternativa_d = st.text_input(
                "Alternativa D"
            )

            resposta_correta = st.selectbox(
                "Resposta Correta",
                [
                    "A",
                    "B",
                    "C",
                    "D"
                ]
            )

            cadastrar_questao = st.form_submit_button(
                "Cadastrar Questão"
            )

            if cadastrar_questao:

                if (
                    not enunciado
                    or not alternativa_a
                    or not alternativa_b
                    or not alternativa_c
                    or not alternativa_d
                ):

                    st.warning(
                        "Preencha o enunciado e todas as alternativas."
                    )

                else:

                    try:

                        resposta = post_api(
                            "/provas/questoes",
                            {
                                "prova_id": prova_id_questao,
                                "enunciado": enunciado,
                                "alternativa_a": alternativa_a,
                                "alternativa_b": alternativa_b,
                                "alternativa_c": alternativa_c,
                                "alternativa_d": alternativa_d,
                                "resposta_correta": resposta_correta,
                                "ordem": ordem_questao
                            }
                        )

                        if resposta.status_code == 200:

                            questao = resposta.json()

                            st.success(
                                f"Questão cadastrada com sucesso! ID: {questao['id']}"
                            )

                        else:

                            mostrar_erro(resposta)

                    except Exception as e:

                        st.error(
                            f"Erro ao cadastrar questão: {e}"
                        )

    # ==============================================
    # RESPONDER PROVA
    # ==============================================

    with prova_aba3:

        st.markdown("### Responder Mini-Prova")

        aluno_id_resposta = st.number_input(
            "ID do Aluno",
            min_value=1,
            step=1,
            key="aluno_id_responder_prova"
        )

        prova_id_resposta = st.number_input(
            "ID da Prova",
            min_value=1,
            step=1,
            key="prova_id_responder_prova"
        )

        carregar_questoes = st.button(
            "Carregar Questões"
        )

        if carregar_questoes:

            try:

                resposta = get_api(
                    f"/provas/{prova_id_resposta}/questoes"
                )

                if resposta.status_code == 200:

                    questoes = resposta.json()

                    if len(questoes) == 0:

                        st.warning(
                            "Esta prova ainda não possui questões cadastradas."
                        )

                    else:

                        st.session_state["questoes_prova_carregadas"] = questoes
                        st.session_state["prova_id_carregada"] = prova_id_resposta

                        st.success(
                            f"{len(questoes)} questão(ões) carregada(s)."
                        )

                else:

                    mostrar_erro(resposta)

            except Exception as e:

                st.error(
                    f"Erro ao carregar questões: {e}"
                )

        questoes_carregadas = st.session_state["questoes_prova_carregadas"]

        if len(questoes_carregadas) > 0:

            st.divider()

            st.markdown(
                f"### Questões da Prova ID {st.session_state['prova_id_carregada']}"
            )

            with st.form("form_responder_prova"):

                respostas_aluno = []

                for questao in questoes_carregadas:

                    st.markdown(
                        f"**Questão {questao['ordem']} - {questao['enunciado']}**"
                    )

                    opcao = st.radio(
                        "Escolha uma alternativa:",
                        [
                            "A",
                            "B",
                            "C",
                            "D"
                        ],
                        format_func=lambda x, q=questao: (
                            f"{x} - {q[f'alternativa_{x.lower()}']}"
                        ),
                        key=f"resposta_questao_{questao['id']}"
                    )

                    respostas_aluno.append(
                        {
                            "questao_id": questao["id"],
                            "resposta": opcao
                        }
                    )

                    st.divider()

                enviar_respostas = st.form_submit_button(
                    "Enviar Respostas"
                )

                if enviar_respostas:

                    try:

                        resposta = post_api(
                            "/provas/responder",
                            {
                                "aluno_id": aluno_id_resposta,
                                "prova_id": st.session_state["prova_id_carregada"],
                                "respostas": respostas_aluno
                            }
                        )

                        if resposta.status_code == 200:

                            resultado = resposta.json()

                            st.success(
                                resultado["mensagem"]
                            )

                            col1, col2, col3, col4 = st.columns(4)

                            with col1:

                                st.metric(
                                    "Total de Questões",
                                    resultado["total_questoes"]
                                )

                            with col2:

                                st.metric(
                                    "Acertos",
                                    resultado["acertos"]
                                )

                            with col3:

                                st.metric(
                                    "Percentual",
                                    f"{resultado['percentual']}%"
                                )

                            with col4:

                                st.metric(
                                    "Pontos Gamificados",
                                    resultado["pontos_gamificados"]
                                )

                            if resultado["resultado_gamificacao"]:

                                gamificacao = resultado["resultado_gamificacao"]

                                st.info(
                                    f"Nível atual: {gamificacao['nivel_atualizado']}"
                                )

                                if gamificacao["subiu_de_nivel"]:

                                    st.balloons()

                                    st.success(
                                        "🎉 O aluno subiu de nível com a mini-prova!"
                                    )

                                if gamificacao["medalhas_desbloqueadas"]:

                                    st.success(
                                        "🏅 Medalhas desbloqueadas:"
                                    )

                                    for medalha in gamificacao["medalhas_desbloqueadas"]:

                                        st.write(
                                            f"• {medalha}"
                                        )

                        else:

                            mostrar_erro(resposta)

                    except Exception as e:

                        st.error(
                            f"Erro ao responder prova: {e}"
                        )

    # ==============================================
    # TENTATIVAS
    # ==============================================

    with prova_aba4:

        st.markdown("### Histórico de Tentativas do Aluno")

        aluno_id_tentativas = st.number_input(
            "ID do Aluno para consultar tentativas",
            min_value=1,
            step=1,
            key="aluno_id_tentativas"
        )

        if st.button("Buscar Tentativas"):

            try:

                resposta = get_api(
                    f"/alunos/{aluno_id_tentativas}/tentativas"
                )

                if resposta.status_code == 200:

                    tentativas = resposta.json()

                    if len(tentativas) == 0:

                        st.warning(
                            "Este aluno ainda não respondeu nenhuma prova."
                        )

                    else:

                        st.dataframe(
                            pd.DataFrame(tentativas),
                            use_container_width=True
                        )

                else:

                    mostrar_erro(resposta)

            except Exception as e:

                st.error(
                    f"Erro ao buscar tentativas: {e}"
                )

    # ==============================================
    # ESTATÍSTICAS DAS PROVAS
    # ==============================================

    with prova_aba5:

        st.markdown("### Estatísticas das Mini-Provas")

        if st.button("Atualizar Estatísticas das Provas"):

            try:

                resposta = get_api(
                    "/provas/estatisticas"
                )

                if resposta.status_code == 200:

                    dados = resposta.json()

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "Total de Provas",
                            dados["total_provas"]
                        )

                    with col2:

                        st.metric(
                            "Total de Questões",
                            dados["total_questoes"]
                        )

                    with col3:

                        st.metric(
                            "Tentativas Realizadas",
                            dados["total_tentativas"]
                        )

                    with col4:

                        st.metric(
                            "Média de Aproveitamento",
                            f"{round(dados['media_percentual'], 2)}%"
                        )

                else:

                    mostrar_erro(resposta)

            except Exception as e:

                st.error(
                    f"Erro ao buscar estatísticas das provas: {e}"
                )


# ==================================================
# ABA 7 - RANKING
# ==================================================

with aba7:

    st.subheader("Ranking")

    tipo = st.radio(
        "Tipo de Ranking",
        [
            "geral",
            "semanal"
        ]
    )

    buscar = st.button(
        "Buscar Ranking"
    )

    if buscar:

        try:

            resposta = get_api(
                f"/ranking/{tipo}"
            )

            if resposta.status_code == 200:

                ranking = resposta.json()

                if len(ranking) == 0:

                    st.warning(
                        "Nenhum aluno pontuado ainda."
                    )

                else:

                    df = pd.DataFrame(
                        ranking
                    )

                    st.dataframe(
                        df,
                        use_container_width=True
                    )

            else:

                mostrar_erro(resposta)

        except Exception as e:

            st.error(
                f"Erro ao buscar ranking: {e}"
            )


# ==================================================
# ABA 8 - ESTATÍSTICAS ADMINISTRATIVAS
# ==================================================

with aba8:

    st.subheader("Estatísticas Administrativas")

    st.write(
        "Resumo geral do módulo de gamificação e das entidades acadêmicas."
    )

    atualizar_estatisticas = st.button(
        "Atualizar Estatísticas"
    )

    if atualizar_estatisticas:

        try:

            resposta = get_api(
                "/admin/estatisticas"
            )

            if resposta.status_code == 200:

                dados = resposta.json()

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Total de Alunos",
                        dados["total_alunos"]
                    )

                with col2:

                    st.metric(
                        "Total de Professores",
                        dados["total_professores"]
                    )

                with col3:

                    st.metric(
                        "Total de Disciplinas",
                        dados["total_disciplinas"]
                    )

                with col4:

                    st.metric(
                        "Total de Turmas",
                        dados["total_turmas"]
                    )

                col5, col6, col7 = st.columns(3)

                with col5:

                    st.metric(
                        "Total de Pontos",
                        dados["total_pontos"]
                    )

                with col6:

                    st.metric(
                        "Medalhas Conquistadas",
                        dados["quantidade_medalhas"]
                    )

                with col7:

                    st.metric(
                        "Maior Pontuação",
                        dados["maior_pontuacao"]
                    )

                st.divider()

                aluno_destaque = dados["aluno_destaque"]

                if aluno_destaque:

                    st.success(
                        f"🏆 Aluno destaque: {aluno_destaque['nome']} "
                        f"(ID {aluno_destaque['id']}) com "
                        f"{aluno_destaque['pontos']} pontos."
                    )

                else:

                    st.warning(
                        "Ainda não há aluno com pontuação registrada."
                    )

            else:

                mostrar_erro(resposta)

        except Exception as e:

            st.error(
                f"Erro ao buscar estatísticas: {e}"
            )