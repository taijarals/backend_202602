"""
Classe abstrata responsável por definir
o contrato que qualquer Provider deve seguir.
"""

from abc import ABC, abstractmethod


class ProvaProvider(ABC):
    """
    Classe base para qualquer provider.
    """

    # ==========================
    # PROVAS
    # ==========================

    @abstractmethod
    def buscar_prova(self, prova_id):
        """Busca uma prova pelo ID."""
        pass

    @abstractmethod
    def listar_provas(self):
        """Lista todas as provas."""
        pass

    # ==========================
    # QUESTÕES
    # ==========================

    @abstractmethod
    def buscar_questoes(self, prova_id):
        """Busca todas as questões de uma prova."""
        pass

    # ==========================
    # ALTERNATIVAS
    # ==========================

    @abstractmethod
    def buscar_alternativas(self, questao_id):
        """Busca todas as alternativas de uma questão."""
        pass

    # CORREÇÃO: método novo — necessário para corrigir a prova no servidor
    @abstractmethod
    def buscar_alternativa(self, alternativa_id):
        """Busca uma alternativa pelo ID (para verificar se está correta)."""
        pass

    # ==========================
    # TENTATIVAS
    # ==========================

    @abstractmethod
    def criar_tentativa(self, usuario_id, prova_id):
        """Cria uma tentativa para um usuário."""
        pass

    @abstractmethod
    def finalizar_tentativa(self, tentativa_id, nota, dentro_do_prazo):
        """Finaliza uma tentativa."""
        pass

    # ==========================
    # RESPOSTAS
    # ==========================

    @abstractmethod
    def salvar_resposta(self, tentativa_id, questao_id, alternativa_id, acertou):
        """Salva uma resposta."""
        pass
