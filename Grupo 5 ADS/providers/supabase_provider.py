"""
Provider responsável por realizar todas as operações
no banco de dados Supabase.

Esta classe implementa o contrato definido em ProvaProvider.
"""

from database.connection import supabase
from providers.prova_provider import ProvaProvider


class SupabaseProvider(ProvaProvider):
    """
    Implementação do Provider utilizando Supabase.
    """

    # ==================================================
    # PROVAS
    # ==================================================

    def listar_provas(self):
        """Retorna todas as provas cadastradas."""
        resposta = (
            supabase
            .table("provas")
            .select("*")
            .execute()
        )
        return resposta.data

    def buscar_prova(self, prova_id):
        """Busca uma prova pelo ID."""
        resposta = (
            supabase
            .table("provas")
            .select("*")
            .eq("id", prova_id)
            .single()
            .execute()
        )
        return resposta.data

    # ==================================================
    # QUESTÕES
    # ==================================================

    def buscar_questoes(self, prova_id):
        """Busca todas as questões da prova."""
        resposta = (
            supabase
            .table("questoes")
            .select("*")
            .eq("prova_id", prova_id)
            .order("ordem")
            .execute()
        )
        return resposta.data

    # ==================================================
    # ALTERNATIVAS
    # ==================================================

    def buscar_alternativas(self, questao_id):
        """Busca todas as alternativas de uma questão."""
        resposta = (
            supabase
            .table("alternativas")
            .select("*")
            .eq("questao_id", questao_id)
            .order("ordem")
            .execute()
        )
        return resposta.data

    # CORREÇÃO: método novo para buscar uma alternativa específica
    def buscar_alternativa(self, alternativa_id):
        """Busca uma alternativa pelo ID."""
        resposta = (
            supabase
            .table("alternativas")
            .select("*")
            .eq("id", alternativa_id)
            .single()
            .execute()
        )
        return resposta.data

    # ==================================================
    # TENTATIVAS
    # ==================================================

    def criar_tentativa(self, usuario_id, prova_id):
        """Cria uma nova tentativa."""
        resposta = (
            supabase
            .table("tentativas")
            .insert({
                "usuario_id": usuario_id,
                "prova_id": prova_id
            })
            .execute()
        )
        return resposta.data

    def finalizar_tentativa(self, tentativa_id, nota, dentro_do_prazo):
        """Atualiza a tentativa quando a prova termina."""
        resposta = (
            supabase
            .table("tentativas")
            .update({
                "nota": nota,
                "dentro_do_prazo": dentro_do_prazo,
                "status": "FINALIZADA",
                "finalizado_em": "now()"
            })
            .eq("id", tentativa_id)
            .execute()
        )
        return resposta.data

    # ==================================================
    # RESPOSTAS
    # ==================================================

    def salvar_resposta(self, tentativa_id, questao_id, alternativa_id, acertou):
        """Salva uma resposta do aluno."""
        resposta = (
            supabase
            .table("respostas")
            .insert({
                "tentativa_id": tentativa_id,
                "questao_id": questao_id,
                "alternativa_escolhida": alternativa_id,
                "acertou": acertou
            })
            .execute()
        )
        return resposta.data
