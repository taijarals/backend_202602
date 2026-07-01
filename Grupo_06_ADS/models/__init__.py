"""Models package initialization."""
from .base import (
    BaseResponseModel, TimestampMixin, IDMixin,
    PaginationParams, PaginatedResponse, MessageResponse, ErrorResponse
)
from .user import (
    UserBase, UserCreate, UserUpdate, UserLogin,
    UserResponse, UserStats, TokenResponse, AuthUser
)
from .disciplina import (
    DisciplinaBase, DisciplinaCreate, DisciplinaUpdate,
    DisciplinaResponse, DisciplinaWithDetails
)
from .turma import (
    TurmaBase, TurmaCreate, TurmaUpdate, TurmaResponse,
    TurmaWithDetails, TurmaAlunoCreate, TurmaAlunoResponse
)
from .desafio import (
    DesafioBase, DesafioCreate, DesafioUpdate, DesafioResponse,
    DesafioWithDetails, SubmissaoBase, SubmissaoCreate, SubmissaoUpdate,
    SubmissaoResponse, SubmissaoWithDetails, VotoCreate, VotoResponse,
    RankingEntry
)
from .miniprova import (
    QuestaoBase, QuestaoCreate, QuestaoResponse, QuestaoForStudent,
    MiniProvaBase, MiniProvaCreate, MiniProvaUpdate, MiniProvaResponse,
    MiniProvaWithQuestoes, MiniProvaForStudent, RespostaCreate,
    TentativaCreate, TentativaUpdate, TentativaResponse, TentativaWithDetails
)
from .gamificacao import (
    PontuacaoCreate, PontuacaoResponse,
    MedalhaBase, MedalhaCreate, MedalhaResponse,
    ConquistaResponse, NivelResponse, NivelProgress,
    UserGamificationStats, LeaderboardEntry
)
from .equipe import (
    EquipeBase, EquipeCreate, EquipeUpdate, EquipeResponse,
    EquipeMembroResponse, EquipeWithDetails, EquipeMembroCreate,
    TeamFormationRequest, TeamFormationResult
)
from .missao import (
    MissaoEtapaBase, MissaoEtapaCreate, MissaoEtapaResponse,
    MissaoBase, MissaoCreate, MissaoUpdate, MissaoResponse,
    MissaoWithEtapas, MissaoProgress, ProgressoEtapaCreate,
    ProgressoEtapaResponse, UserMissionStats
)
from .enquete import (
    OpcaoEnqueteBase, OpcaoEnqueteCreate, OpcaoEnqueteResponse,
    EnqueteBase, EnqueteCreate, EnqueteUpdate, EnqueteResponse,
    EnqueteWithOpcoes, VotoEnqueteCreate, VotoEnqueteResponse,
    EnqueteStats
)

__all__ = [
    # Base
    'BaseResponseModel', 'TimestampMixin', 'IDMixin',
    'PaginationParams', 'PaginatedResponse', 'MessageResponse', 'ErrorResponse',
    # User
    'UserBase', 'UserCreate', 'UserUpdate', 'UserLogin',
    'UserResponse', 'UserStats', 'TokenResponse', 'AuthUser',
    # Disciplina
    'DisciplinaBase', 'DisciplinaCreate', 'DisciplinaUpdate',
    'DisciplinaResponse', 'DisciplinaWithDetails',
    # Turma
    'TurmaBase', 'TurmaCreate', 'TurmaUpdate', 'TurmaResponse',
    'TurmaWithDetails', 'TurmaAlunoCreate', 'TurmaAlunoResponse',
    # Desafio
    'DesafioBase', 'DesafioCreate', 'DesafioUpdate', 'DesafioResponse',
    'DesafioWithDetails', 'SubmissaoBase', 'SubmissaoCreate', 'SubmissaoUpdate',
    'SubmissaoResponse', 'SubmissaoWithDetails', 'VotoCreate', 'VotoResponse',
    'RankingEntry',
    # Mini Prova
    'QuestaoBase', 'QuestaoCreate', 'QuestaoResponse', 'QuestaoForStudent',
    'MiniProvaBase', 'MiniProvaCreate', 'MiniProvaUpdate', 'MiniProvaResponse',
    'MiniProvaWithQuestoes', 'MiniProvaForStudent', 'RespostaCreate',
    'TentativaCreate', 'TentativaUpdate', 'TentativaResponse', 'TentativaWithDetails',
    # Gamificacao
    'PontuacaoCreate', 'PontuacaoResponse',
    'MedalhaBase', 'MedalhaCreate', 'MedalhaResponse',
    'ConquistaResponse', 'NivelResponse', 'NivelProgress',
    'UserGamificationStats', 'LeaderboardEntry',
    # Equipe
    'EquipeBase', 'EquipeCreate', 'EquipeUpdate', 'EquipeResponse',
    'EquipeMembroResponse', 'EquipeWithDetails', 'EquipeMembroCreate',
    'TeamFormationRequest', 'TeamFormationResult',
    # Missao
    'MissaoEtapaBase', 'MissaoEtapaCreate', 'MissaoEtapaResponse',
    'MissaoBase', 'MissaoCreate', 'MissaoUpdate', 'MissaoResponse',
    'MissaoWithEtapas', 'MissaoProgress', 'ProgressoEtapaCreate',
    'ProgressoEtapaResponse', 'UserMissionStats',
    # Enquete
    'OpcaoEnqueteBase', 'OpcaoEnqueteCreate', 'OpcaoEnqueteResponse',
    'EnqueteBase', 'EnqueteCreate', 'EnqueteUpdate', 'EnqueteResponse',
    'EnqueteWithOpcoes', 'VotoEnqueteCreate', 'VotoEnqueteResponse',
    'EnqueteStats',
]
