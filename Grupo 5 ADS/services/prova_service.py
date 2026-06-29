"""
Service responsável pelas regras de negócio.
"""

from repositories.prova_repository import repository


class ProvaService:

    def __init__(self):
        self.repository = repository

    # ==========================================
    # PROVAS
    # ==========================================

    def listar_provas(self):
        return self.repository.listar_provas()

    def buscar_prova(self, prova_id):
        prova = self.repository.buscar_prova(prova_id)
        if not prova:
            return None
        questoes = self.repository.buscar_questoes(prova_id)
        for questao in questoes:
            alternativas = self.repository.buscar_alternativas(questao["id"])
            questao["alternativas"] = alternativas
        prova["questoes"] = questoes
        return prova

    # ==========================================
    # TENTATIVAS
    # ==========================================

    def iniciar_tentativa(self, usuario_id, prova_id):
        """
        Cria uma tentativa para o usuário autenticado.
        Agora recebe usuario_id direto (não mais do .env).
        """
        resultado = self.repository.criar_tentativa(usuario_id, prova_id)
        if resultado and len(resultado) > 0:
            return resultado[0]
        return None

    # ==========================================
    # FINALIZAÇÃO
    # ==========================================

    def finalizar_prova(self, tentativa_id, respostas):
        acertos = 0
        total = len(respostas)

        for resposta in respostas:
            alternativa_id = resposta["alternativa_id"]
            questao_id = resposta["questao_id"]

            alternativa = self.repository.buscar_alternativa(alternativa_id)
            acertou = alternativa["correta"] if alternativa else False

            self.repository.salvar_resposta(
                tentativa_id, questao_id, alternativa_id, acertou
            )

            if acertou:
                acertos += 1

        nota = (acertos / total) * 10 if total > 0 else 0
        self.repository.finalizar_tentativa(tentativa_id, nota, dentro_do_prazo=True)

        return {
            "nota": round(nota, 2),
            "acertos": acertos,
            "total": total,
            "aprovado": nota >= 6
        }
