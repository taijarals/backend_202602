"""
Repository responsável por intermediar a comunicação
entre o Service e o Provider.

O Service nunca acessa diretamente o Supabase.
"""

from providers.provider_factory import ProviderFactory


class ProvaRepository:
    """
    Repository da aplicação.
    """

    def __init__(self):
        self.provider = ProviderFactory.criar_provider()

    # =====================================
    # PROVAS
    # =====================================

    def listar_provas(self):
        return self.provider.listar_provas()

    def buscar_prova(self, prova_id):
        return self.provider.buscar_prova(prova_id)

    # =====================================
    # QUESTÕES
    # =====================================

    def buscar_questoes(self, prova_id):
        return self.provider.buscar_questoes(prova_id)

    # =====================================
    # ALTERNATIVAS
    # =====================================

    def buscar_alternativas(self, questao_id):
        return self.provider.buscar_alternativas(questao_id)

    # CORREÇÃO: método novo para buscar alternativa por ID
    def buscar_alternativa(self, alternativa_id):
        return self.provider.buscar_alternativa(alternativa_id)

    # =====================================
    # TENTATIVAS
    # =====================================

    def criar_tentativa(self, usuario_id, prova_id):
        return self.provider.criar_tentativa(usuario_id, prova_id)

    def finalizar_tentativa(self, tentativa_id, nota, dentro_do_prazo):
        return self.provider.finalizar_tentativa(tentativa_id, nota, dentro_do_prazo)

    # =====================================
    # RESPOSTAS
    # =====================================

    def salvar_resposta(self, tentativa_id, questao_id, alternativa_id, acertou):
        return self.provider.salvar_resposta(
            tentativa_id, questao_id, alternativa_id, acertou
        )


# Instância única do Repository
repository = ProvaRepository()
