import os
from providers.sql_provider import SQLProvider


class ProviderFactory:
    @staticmethod
    def create():
        # Busca a estratégia no ambiente, padrão para 'sql'
        strategy = os.getenv("DB_STRATEGY", "sql").lower()
        
        if strategy == "sql":
            return SQLProvider()
            
        raise ValueError(f"Provider '{strategy}' não suportado")
