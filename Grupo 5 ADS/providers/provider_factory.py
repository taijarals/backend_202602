"""
Factory responsável por fornecer
o Provider utilizado pelo sistema.
coloquei o supabase, tenho conta nos outros não. preciso de grana. <(＿　＿)>
"""

# Importa o provider do Supabase
from providers.supabase_provider import SupabaseProvider


class ProviderFactory:
    """
    Cria uma instância do Provider.
    """

    @staticmethod
    def criar_provider():
        """
        Retorna o provider utilizado pela aplicação.
        """
        return SupabaseProvider()