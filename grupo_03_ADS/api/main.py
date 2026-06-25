import logging

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse

from models.gamificacao_models import (
    RegistroPontuacao,
    CadastroAluno,
    CadastroProfessor,
    CadastroDisciplina,
    CadastroTurma,
    VincularAlunoTurma
)

from models.provas_models import (
    CadastroProva,
    CadastroQuestaoProva,
    EnviarRespostasProva
)

from services.gamificacao_service import (
    GamificacaoService
)

from services.provas_service import (
    ProvasService
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Plataforma Educacional - Gamificação"
)

service = GamificacaoService()
provas_service = ProvasService()


@app.exception_handler(Exception)
async def tratar_erro_global(
    request: Request,
    exc: Exception
):
    logger.exception(
        f"Erro interno não tratado na rota {request.url.path}: {exc}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "erro": "Erro interno",
            "mensagem": "Ocorreu um erro inesperado no servidor."
        }
    )


def validar_token(
    x_api_token: str = Header(...)
):
    if x_api_token != "chave-secreta-123":

        logger.warning(
            "Tentativa de acesso com token inválido."
        )

        raise HTTPException(
            status_code=401,
            detail="Token Inválido"
        )


# ==================================================
# ALUNOS
# ==================================================

@app.post("/api/alunos")
def cadastrar_aluno(
    dados: CadastroAluno,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return service.cadastrar_aluno(
            dados.nome,
            str(dados.email)
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Não foi possível cadastrar o aluno. Verifique se o email já está cadastrado."
        )


@app.get("/api/alunos")
def listar_alunos(
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    return service.listar_alunos()


# ==================================================
# PROFESSORES
# ==================================================

@app.post("/api/professores")
def cadastrar_professor(
    dados: CadastroProfessor,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return service.cadastrar_professor(
            dados.nome,
            str(dados.email)
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Não foi possível cadastrar o professor. Verifique se o email já está cadastrado."
        )


@app.get("/api/professores")
def listar_professores(
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    return service.listar_professores()


# ==================================================
# DISCIPLINAS
# ==================================================

@app.post("/api/disciplinas")
def cadastrar_disciplina(
    dados: CadastroDisciplina,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    return service.cadastrar_disciplina(
        dados.nome,
        dados.descricao
    )


@app.get("/api/disciplinas")
def listar_disciplinas(
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    return service.listar_disciplinas()


# ==================================================
# TURMAS
# ==================================================

@app.post("/api/turmas")
def cadastrar_turma(
    dados: CadastroTurma,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return service.cadastrar_turma(
            dados.nome,
            dados.professor_id,
            dados.disciplina_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get("/api/turmas")
def listar_turmas(
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    return service.listar_turmas()


@app.post("/api/turmas/alunos")
def vincular_aluno_turma(
    dados: VincularAlunoTurma,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return service.vincular_aluno_turma(
            dados.turma_id,
            dados.aluno_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get("/api/turmas/{turma_id}/alunos")
def listar_alunos_da_turma(
    turma_id: int,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return service.listar_alunos_da_turma(
            turma_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ==================================================
# MINI-PROVAS GAMIFICADAS
# ==================================================

@app.post("/api/provas")
def cadastrar_prova(
    dados: CadastroProva,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return provas_service.cadastrar_prova(
            dados.titulo,
            dados.descricao,
            dados.professor_id,
            dados.disciplina_id,
            dados.duracao_minutos,
            dados.pontos_por_questao,
            dados.ativa
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get("/api/provas")
def listar_provas(
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    return provas_service.listar_provas()


@app.post("/api/provas/questoes")
def cadastrar_questao_prova(
    dados: CadastroQuestaoProva,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return provas_service.cadastrar_questao(
            dados.prova_id,
            dados.enunciado,
            dados.alternativa_a,
            dados.alternativa_b,
            dados.alternativa_c,
            dados.alternativa_d,
            dados.resposta_correta,
            dados.ordem
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get("/api/provas/{prova_id}/questoes")
def listar_questoes_prova(
    prova_id: int,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return provas_service.listar_questoes_para_aluno(
            prova_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.post("/api/provas/responder")
def responder_prova(
    dados: EnviarRespostasProva,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return provas_service.responder_prova(
            dados.aluno_id,
            dados.prova_id,
            dados.respostas
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get("/api/alunos/{aluno_id}/tentativas")
def listar_tentativas_aluno(
    aluno_id: int,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return provas_service.listar_tentativas_aluno(
            aluno_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get("/api/provas/estatisticas")
def estatisticas_provas(
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    return provas_service.obter_estatisticas_provas()


# ==================================================
# DASHBOARD DO ALUNO
# ==================================================

@app.get("/api/aluno/{aluno_id}")
def dashboard_aluno(
    aluno_id: int,
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    try:

        return service.buscar_dashboard_aluno(
            aluno_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ==================================================
# PONTUAÇÃO
# ==================================================

@app.post("/api/pontuar")
def pontuar(
    dados: RegistroPontuacao,
    x_api_token: str = Header(...)
):

    validar_token(x_api_token)

    try:

        return service.processar_pontuacao(
            dados.aluno_id,
            dados.atividade,
            dados.pontos_ganhos
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ==================================================
# RANKING
# ==================================================

@app.get("/api/ranking/{tipo}")
def ranking(
    tipo: str,
    x_api_token: str = Header(...)
):

    validar_token(x_api_token)

    if tipo not in [
        "geral",
        "semanal"
    ]:

        raise HTTPException(
            status_code=400,
            detail="Tipo de ranking inválido. Use 'geral' ou 'semanal'."
        )

    return service.buscar_ranking(tipo)


# ==================================================
# ESTATÍSTICAS
# ==================================================

@app.get("/api/admin/estatisticas")
def estatisticas_admin(
    x_api_token: str = Header(...)
):
    validar_token(x_api_token)

    return service.buscar_estatisticas_admin()