"""API package initialization."""
from .auth import router as auth_router
from .users import router as users_router
from .disciplinas import router as disciplinas_router
from .turmas import router as turmas_router
from .desafios import router as desafios_router
from .miniprovas import router as miniprovas_router
from .gamificacao import router as gamificacao_router
from .equipes import router as equipes_router
from .missoes import router as missoes_router
from .enquetes import router as enquetes_router

__all__ = [
    'auth_router',
    'users_router',
    'disciplinas_router',
    'turmas_router',
    'desafios_router',
    'miniprovas_router',
    'gamificacao_router',
    'equipes_router',
    'missoes_router',
    'enquetes_router',
]
