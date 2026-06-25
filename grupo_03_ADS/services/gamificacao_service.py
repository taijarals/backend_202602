import logging
from datetime import datetime, timedelta

from repositories.gamificacao_repository import (
    GamificacaoRepository
)


logger = logging.getLogger(__name__)


class GamificacaoService:

    def __init__(self):
        self.repo = GamificacaoRepository()

    # ==================================================
    # ALUNOS
    # ==================================================

    def cadastrar_aluno(
        self,
        nome: str,
        email: str
    ):
        logger.info(
            f"Iniciando cadastro de aluno: nome={nome}, email={email}"
        )

        aluno = self.repo.cadastrar_aluno(
            nome,
            email
        )

        logger.info(
            f"Aluno cadastrado com sucesso: id={aluno['id']}, nome={aluno['nome']}, email={aluno['email']}"
        )

        return aluno

    def listar_alunos(self):
        logger.info(
            "Listando alunos cadastrados."
        )

        alunos = self.repo.listar_alunos()

        logger.info(
            f"Total de alunos retornados: {len(alunos)}"
        )

        return [
            {
                "id": aluno["id"],
                "nome": aluno["nome"],
                "email": aluno["email"],
                "pontos": int(aluno["pontos"]),
                "nivel": aluno["nivel"],
                "titulo": aluno["titulo"],
                "streak": aluno["streak"]
            }
            for aluno in alunos
        ]

    # ==================================================
    # PROFESSORES
    # ==================================================

    def cadastrar_professor(
        self,
        nome: str,
        email: str
    ):
        logger.info(
            f"Cadastrando professor: nome={nome}, email={email}"
        )

        professor = self.repo.cadastrar_professor(
            nome,
            email
        )

        logger.info(
            f"Professor cadastrado: id={professor['id']}"
        )

        return professor

    def listar_professores(self):
        logger.info(
            "Listando professores."
        )

        return self.repo.listar_professores()

    # ==================================================
    # DISCIPLINAS
    # ==================================================

    def cadastrar_disciplina(
        self,
        nome: str,
        descricao: str = None
    ):
        logger.info(
            f"Cadastrando disciplina: nome={nome}"
        )

        disciplina = self.repo.cadastrar_disciplina(
            nome,
            descricao
        )

        logger.info(
            f"Disciplina cadastrada: id={disciplina['id']}"
        )

        return disciplina

    def listar_disciplinas(self):
        logger.info(
            "Listando disciplinas."
        )

        return self.repo.listar_disciplinas()

    # ==================================================
    # TURMAS
    # ==================================================

    def cadastrar_turma(
        self,
        nome: str,
        professor_id: int,
        disciplina_id: int
    ):
        professor = self.repo.obter_professor(
            professor_id
        )

        if not professor:
            raise ValueError(
                f"Professor {professor_id} não encontrado."
            )

        disciplina = self.repo.obter_disciplina(
            disciplina_id
        )

        if not disciplina:
            raise ValueError(
                f"Disciplina {disciplina_id} não encontrada."
            )

        logger.info(
            f"Cadastrando turma: nome={nome}, professor_id={professor_id}, disciplina_id={disciplina_id}"
        )

        turma = self.repo.cadastrar_turma(
            nome,
            professor_id,
            disciplina_id
        )

        logger.info(
            f"Turma cadastrada: id={turma['id']}"
        )

        return turma

    def listar_turmas(self):
        logger.info(
            "Listando turmas."
        )

        turmas = self.repo.listar_turmas()

        return [
            {
                "id": turma["id"],
                "nome": turma["nome"],
                "professor_id": turma["professor_id"],
                "professor": turma["professor"],
                "disciplina_id": turma["disciplina_id"],
                "disciplina": turma["disciplina"],
                "total_alunos": int(turma["total_alunos"])
            }
            for turma in turmas
        ]

    def vincular_aluno_turma(
        self,
        turma_id: int,
        aluno_id: int
    ):
        turma = self.repo.obter_turma(
            turma_id
        )

        if not turma:
            raise ValueError(
                f"Turma {turma_id} não encontrada."
            )

        aluno = self.repo.obter_aluno(
            aluno_id
        )

        if not aluno:
            raise ValueError(
                f"Aluno {aluno_id} não encontrado."
            )

        logger.info(
            f"Vinculando aluno à turma: aluno_id={aluno_id}, turma_id={turma_id}"
        )

        vinculo = self.repo.vincular_aluno_turma(
            turma_id,
            aluno_id
        )

        if not vinculo:
            return {
                "mensagem": "Aluno já estava vinculado a esta turma.",
                "turma_id": turma_id,
                "aluno_id": aluno_id
            }

        return {
            "mensagem": "Aluno vinculado à turma com sucesso.",
            "turma_id": turma_id,
            "aluno_id": aluno_id
        }

    def listar_alunos_da_turma(
        self,
        turma_id: int
    ):
        turma = self.repo.obter_turma(
            turma_id
        )

        if not turma:
            raise ValueError(
                f"Turma {turma_id} não encontrada."
            )

        return self.repo.listar_alunos_da_turma(
            turma_id
        )

    # ==================================================
    # DASHBOARD DO ALUNO
    # ==================================================

    def buscar_dashboard_aluno(
        self,
        aluno_id: int
    ):
        logger.info(
            f"Buscando dashboard do aluno id={aluno_id}"
        )

        aluno = self.repo.obter_aluno(aluno_id)

        if not aluno:
            logger.warning(
                f"Dashboard solicitado para aluno inexistente: id={aluno_id}"
            )

            raise ValueError(
                f"Aluno {aluno_id} não encontrado."
            )

        self.repo.inicializar_progresso(aluno_id)

        progresso = self.repo.obter_progresso(aluno_id)

        medalhas = self.repo.obter_medalhas_aluno(aluno_id)

        logger.info(
            f"Dashboard carregado: aluno_id={aluno_id}, pontos={progresso['pontos_totais']}, nivel={progresso['nivel_atual']}, medalhas={len(medalhas)}"
        )

        return {
            "id": aluno["id"],
            "nome": aluno["nome"],
            "email": aluno["email"],
            "pontos": progresso["pontos_totais"],
            "nivel": progresso["nivel_atual"],
            "titulo": progresso["titulo"],
            "streak": progresso["streak_atual"],
            "ultima_atividade": progresso["ultima_atividade"],
            "medalhas": medalhas
        }

    # ==================================================
    # PONTUAÇÃO
    # ==================================================

    def processar_pontuacao(
        self,
        aluno_id: int,
        atividade: str,
        pontos_base: int
    ):

        logger.info(
            f"Iniciando pontuação: aluno_id={aluno_id}, atividade='{atividade}', pontos_base={pontos_base}"
        )

        aluno = self.repo.obter_aluno(aluno_id)

        if not aluno:
            logger.warning(
                f"Tentativa de pontuar aluno inexistente: id={aluno_id}"
            )

            raise ValueError(
                f"Aluno {aluno_id} não encontrado."
            )

        self.repo.inicializar_progresso(aluno_id)

        progresso = self.repo.obter_progresso(aluno_id)

        pontos_finais = pontos_base

        streak = progresso["streak_atual"]

        ultima_ativ = progresso["ultima_atividade"]

        hoje = datetime.now().date()

        if ultima_ativ:

            diff = hoje - ultima_ativ.date()

            if diff == timedelta(days=1):
                streak += 1

            elif diff > timedelta(days=1):
                streak = 1

        else:
            streak = 1

        bonus_streak = min(
            0.5,
            (streak // 5) * 0.1
        )

        pontos_bonus = int(
            pontos_base * bonus_streak
        )

        pontos_finais += pontos_bonus

        self.repo.salvar_historico(
            aluno_id,
            atividade,
            pontos_finais
        )

        total_novo = (
            progresso["pontos_totais"]
            + pontos_finais
        )

        niveis = self.repo.obter_niveis()

        nivel_calculado = 1

        for nv in niveis:

            if total_novo >= nv["pontos_minimos"]:
                nivel_calculado = nv["nivel"]

        subiu = (
            nivel_calculado
            > progresso["nivel_atual"]
        )

        medalhas = []

        if progresso["pontos_totais"] == 0:

            self.repo.atribuir_medalha(
                aluno_id,
                "FIRST_BLOOD"
            )

            medalhas.append(
                "Primeiro Passo"
            )

        if streak >= 5:

            self.repo.atribuir_medalha(
                aluno_id,
                "STREAK_5"
            )

            medalhas.append(
                "Inabalável (Streak 5)"
            )

        self.repo.atualizar_progresso(
            aluno_id,
            total_novo,
            nivel_calculado,
            streak
        )

        logger.info(
            f"Aluno {aluno_id} recebeu {pontos_finais} pontos."
        )

        if subiu:

            logger.info(
                f"Aluno {aluno_id} subiu para o nível {nivel_calculado}."
            )

        return {
            "sucesso": True,
            "mensagem": "Pontos computados!",
            "pontos_finais": pontos_finais,
            "nivel_atualizado": nivel_calculado,
            "subiu_de_nivel": subiu,
            "medalhas_desbloqueadas": medalhas
        }

    # ==================================================
    # RANKING
    # ==================================================

    def buscar_ranking(self, tipo: str):

        logger.info(
            f"Buscando ranking: tipo={tipo}"
        )

        dados = self.repo.obter_ranking(
            geral=(tipo == "geral")
        )

        return [
            {
                "posicao": i + 1,
                "aluno_id": d["id"],
                "nome": d["nome"],
                "pontos": int(d["pontos"]),
                "nivel": d["nivel"]
            }
            for i, d in enumerate(dados)
        ]

    # ==================================================
    # ESTATÍSTICAS
    # ==================================================

    def buscar_estatisticas_admin(self):

        logger.info(
            "Buscando estatísticas administrativas."
        )

        estatisticas = self.repo.obter_estatisticas_admin()

        aluno_destaque = self.repo.obter_aluno_maior_pontuacao()

        if aluno_destaque:

            destaque = {
                "id": aluno_destaque["id"],
                "nome": aluno_destaque["nome"],
                "pontos": int(aluno_destaque["pontos"])
            }

        else:

            destaque = None

        return {
            "total_alunos": int(estatisticas["total_alunos"]),
            "total_professores": int(estatisticas["total_professores"]),
            "total_disciplinas": int(estatisticas["total_disciplinas"]),
            "total_turmas": int(estatisticas["total_turmas"]),
            "total_pontos": int(estatisticas["total_pontos"]),
            "quantidade_medalhas": int(estatisticas["quantidade_medalhas"]),
            "maior_pontuacao": int(estatisticas["maior_pontuacao"]),
            "aluno_destaque": destaque
        }