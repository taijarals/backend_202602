"""Repositories package initialization."""
from .base import BaseRepository
from .user_repository import UserRepository, AuthRepository
from .disciplina_repository import DisciplinaRepository
from .turma_repository import TurmaRepository, TurmaAlunoRepository
from .desafio_repository import DesafioRepository, SubmissaoRepository, VotoRepository
from .miniprova_repository import (
    MiniProvaRepository, QuestaoRepository,
    TentativaRepository, RespostaRepository
)
from .gamificacao_repository import (
    PontuacaoRepository, MedalhaRepository,
    ConquistaRepository, NivelRepository, LeaderboardRepository
)
from .equipe_repository import EquipeRepository, EquipeMembroRepository
from .missao_repository import (
    MissaoRepository, MissaoEtapaRepository, ProgressoMissaoRepository
)
from .enquete_repository import (
    EnqueteRepository, OpcaoEnqueteRepository, VotoEnqueteRepository
)

__all__ = [
    'BaseRepository',
    'UserRepository', 'AuthRepository',
    'DisciplinaRepository',
    'TurmaRepository', 'TurmaAlunoRepository',
    'DesafioRepository', 'SubmissaoRepository', 'VotoRepository',
    'MiniProvaRepository', 'QuestaoRepository', 'TentativaRepository', 'RespostaRepository',
    'PontuacaoRepository', 'MedalhaRepository', 'ConquistaRepository', 'NivelRepository', 'LeaderboardRepository',
    'EquipeRepository', 'EquipeMembroRepository',
    'MissaoRepository', 'MissaoEtapaRepository', 'ProgressoMissaoRepository',
    'EnqueteRepository', 'OpcaoEnqueteRepository', 'VotoEnqueteRepository',
]
