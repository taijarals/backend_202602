import logging

from repositories.provas_repository import ProvasRepository
from repositories.gamificacao_repository import GamificacaoRepository
from services.gamificacao_service import GamificacaoService


logger = logging.getLogger(__name__)


class ProvasService:

    def __init__(self):
        self.repo = ProvasRepository()
        self.gamificacao_repo = GamificacaoRepository()
        self.gamificacao_service = GamificacaoService()

    def cadastrar_prova(
        self,
        titulo: str,
        descricao: str,
        professor_id: int,
        disciplina_id: int,
        duracao_minutos: int,
        pontos_por_questao: int,
        ativa: bool
    ):
        professor = self.gamificacao_repo.obter_professor(
            professor_id
        )

        if not professor:
            raise ValueError(
                f"Professor {professor_id} não encontrado."
            )

        disciplina = self.gamificacao_repo.obter_disciplina(
            disciplina_id
        )

        if not disciplina:
            raise ValueError(
                f"Disciplina {disciplina_id} não encontrada."
            )

        logger.info(
            f"Cadastrando prova: titulo={titulo}, professor_id={professor_id}, disciplina_id={disciplina_id}"
        )

        return self.repo.cadastrar_prova(
            titulo,
            descricao,
            professor_id,
            disciplina_id,
            duracao_minutos,
            pontos_por_questao,
            ativa
        )

    def listar_provas(self):
        provas = self.repo.listar_provas()

        return [
            {
                "id": prova["id"],
                "titulo": prova["titulo"],
                "descricao": prova["descricao"],
                "professor_id": prova["professor_id"],
                "professor": prova["professor"],
                "disciplina_id": prova["disciplina_id"],
                "disciplina": prova["disciplina"],
                "duracao_minutos": prova["duracao_minutos"],
                "pontos_por_questao": prova["pontos_por_questao"],
                "ativa": prova["ativa"],
                "data_criacao": prova["data_criacao"],
                "total_questoes": int(prova["total_questoes"])
            }
            for prova in provas
        ]

    def cadastrar_questao(
        self,
        prova_id: int,
        enunciado: str,
        alternativa_a: str,
        alternativa_b: str,
        alternativa_c: str,
        alternativa_d: str,
        resposta_correta: str,
        ordem: int
    ):
        prova = self.repo.obter_prova(
            prova_id
        )

        if not prova:
            raise ValueError(
                f"Prova {prova_id} não encontrada."
            )

        resposta_correta = resposta_correta.upper()

        if resposta_correta not in [
            "A",
            "B",
            "C",
            "D"
        ]:
            raise ValueError(
                "A resposta correta deve ser A, B, C ou D."
            )

        logger.info(
            f"Cadastrando questão na prova_id={prova_id}, resposta_correta={resposta_correta}"
        )

        return self.repo.cadastrar_questao(
            prova_id,
            enunciado,
            alternativa_a,
            alternativa_b,
            alternativa_c,
            alternativa_d,
            resposta_correta,
            ordem
        )

    def listar_questoes_para_aluno(
        self,
        prova_id: int
    ):
        prova = self.repo.obter_prova(
            prova_id
        )

        if not prova:
            raise ValueError(
                f"Prova {prova_id} não encontrada."
            )

        questoes = self.repo.listar_questoes_para_aluno(
            prova_id
        )

        return questoes

    def responder_prova(
        self,
        aluno_id: int,
        prova_id: int,
        respostas: list
    ):
        aluno = self.gamificacao_repo.obter_aluno(
            aluno_id
        )

        if not aluno:
            raise ValueError(
                f"Aluno {aluno_id} não encontrado."
            )

        prova = self.repo.obter_prova(
            prova_id
        )

        if not prova:
            raise ValueError(
                f"Prova {prova_id} não encontrada."
            )

        if not prova["ativa"]:
            raise ValueError(
                "Esta prova está inativa."
            )

        questoes = self.repo.listar_questoes_com_resposta(
            prova_id
        )

        if len(questoes) == 0:
            raise ValueError(
                "Esta prova ainda não possui questões cadastradas."
            )

        mapa_respostas = {}

        for resposta in respostas:
            mapa_respostas[resposta.questao_id] = resposta.resposta.upper()

        total_questoes = len(questoes)

        acertos = 0

        detalhes_respostas = []

        for questao in questoes:

            resposta_aluno = mapa_respostas.get(
                questao["id"],
                ""
            )

            correta = (
                resposta_aluno == questao["resposta_correta"]
            )

            if correta:
                acertos += 1

            detalhes_respostas.append(
                {
                    "questao_id": questao["id"],
                    "resposta_aluno": resposta_aluno,
                    "resposta_correta": questao["resposta_correta"],
                    "correta": correta
                }
            )

        pontos_base = (
            acertos * prova["pontos_por_questao"]
        )

        percentual = round(
            (acertos / total_questoes) * 100,
            2
        )

        resultado_gamificacao = None

        pontos_gamificados = 0

        if pontos_base > 0:

            resultado_gamificacao = (
                self.gamificacao_service.processar_pontuacao(
                    aluno_id,
                    f"Mini-Prova: {prova['titulo']}",
                    pontos_base
                )
            )

            pontos_gamificados = resultado_gamificacao[
                "pontos_finais"
            ]

        tentativa = self.repo.registrar_tentativa(
            prova_id,
            aluno_id,
            total_questoes,
            acertos,
            pontos_base,
            pontos_gamificados,
            percentual
        )

        for detalhe in detalhes_respostas:

            self.repo.registrar_resposta_tentativa(
                tentativa["id"],
                detalhe["questao_id"],
                detalhe["resposta_aluno"],
                detalhe["correta"]
            )

        logger.info(
            f"Prova respondida: aluno_id={aluno_id}, prova_id={prova_id}, acertos={acertos}, pontos_base={pontos_base}, pontos_gamificados={pontos_gamificados}"
        )

        return {
            "sucesso": True,
            "mensagem": "Mini-prova corrigida com sucesso!",
            "tentativa_id": tentativa["id"],
            "aluno_id": aluno_id,
            "prova_id": prova_id,
            "prova": prova["titulo"],
            "total_questoes": total_questoes,
            "acertos": acertos,
            "percentual": percentual,
            "pontos_base": pontos_base,
            "pontos_gamificados": pontos_gamificados,
            "resultado_gamificacao": resultado_gamificacao
        }

    def listar_tentativas_aluno(
        self,
        aluno_id: int
    ):
        aluno = self.gamificacao_repo.obter_aluno(
            aluno_id
        )

        if not aluno:
            raise ValueError(
                f"Aluno {aluno_id} não encontrado."
            )

        tentativas = self.repo.listar_tentativas_aluno(
            aluno_id
        )

        return [
            {
                "id": tentativa["id"],
                "prova_id": tentativa["prova_id"],
                "prova": tentativa["prova"],
                "aluno_id": tentativa["aluno_id"],
                "aluno": tentativa["aluno"],
                "total_questoes": tentativa["total_questoes"],
                "acertos": tentativa["acertos"],
                "pontos_base": tentativa["pontos_base"],
                "pontos_gamificados": tentativa["pontos_gamificados"],
                "percentual": float(tentativa["percentual"]),
                "data_realizacao": tentativa["data_realizacao"]
            }
            for tentativa in tentativas
        ]

    def obter_estatisticas_provas(self):
        estatisticas = self.repo.obter_estatisticas_provas()

        return {
            "total_provas": int(estatisticas["total_provas"]),
            "total_questoes": int(estatisticas["total_questoes"]),
            "total_tentativas": int(estatisticas["total_tentativas"]),
            "media_percentual": float(estatisticas["media_percentual"])
        }