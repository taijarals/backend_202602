"""
config.py — Configuração e cliente Supabase para o módulo de Gamificação.

Responsabilidades:
    - Carregar variáveis de ambiente com validação antecipada (fail-fast).
    - Expor um cliente Supabase singleton para toda a aplicação.
    - Centralizar as constantes de negócio (nomes de tabelas, tipos de atividade).

Uso:
    from config import supabase, Tabelas, TipoAtividade
"""

import os
import logging
from enum import StrEnum

from dotenv import load_dotenv
from supabase import create_client, Client

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Variáveis de ambiente
# -----------------------------------------------------------------------------
load_dotenv()

_SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
_SUPABASE_KEY: str | None = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not _SUPABASE_URL or not _SUPABASE_KEY:
    raise EnvironmentError(
        "As variáveis SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY são obrigatórias. "
        "Verifique o arquivo .env."
    )

# -----------------------------------------------------------------------------
# Cliente Supabase (singleton)
# -----------------------------------------------------------------------------
supabase: Client = create_client(_SUPABASE_URL, _SUPABASE_KEY)
"""Cliente Supabase compartilhado. Importar diretamente nos módulos de serviço."""

logger.info("Cliente Supabase inicializado com sucesso. URL: %s", _SUPABASE_URL)


# -----------------------------------------------------------------------------
# Constantes de negócio
# -----------------------------------------------------------------------------

class Tabelas(StrEnum):
    """Nomes exatos das tabelas no banco de dados."""
    NIVEL             = "nivel"
    MEDALHA           = "medalha"
    HISTORICO_PONTOS  = "historico_pontos"
    RANKING           = "ranking"
    CONQUISTA         = "conquista"


class TipoAtividade(StrEnum):
    """
    Tipos de atividade aceitos pela tabela historico_pontos.
    Deve estar em sincronia com o CHECK CONSTRAINT do schema SQL.
    """
    QUIZ_COMPLETO            = "quiz_completo"
    LOGIN_DIARIO             = "login_diario"
    STREAK_BONUS             = "streak_bonus"
    CONQUISTA_DESBLOQUEADA   = "conquista_desbloqueada"
    NIVEL_ATINGIDO           = "nivel_atingido"
    PENALIDADE               = "penalidade"
    OUTRO                    = "outro"


class Views(StrEnum):
    """Views disponíveis no banco de dados."""
    RANKING_TOP = "vw_ranking_top"


# Pontuação padrão por tipo de atividade (pode ser sobrescrita por parâmetro)
PONTOS_PADRAO: dict[TipoAtividade, int] = {
    TipoAtividade.QUIZ_COMPLETO:          50,
    TipoAtividade.LOGIN_DIARIO:           10,
    TipoAtividade.STREAK_BONUS:           25,
    TipoAtividade.CONQUISTA_DESBLOQUEADA:  0,   # Informativo; sem XP extra
    TipoAtividade.NIVEL_ATINGIDO:          0,   # Informativo; sem XP extra
    TipoAtividade.PENALIDADE:            -20,
    TipoAtividade.OUTRO:                   5,
}
