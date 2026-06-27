"""
models.py — Modelos de dados (DTOs) para o módulo de Gamificação.

Utiliza dataclasses para representar as entidades retornadas pelo banco,
garantindo type-safety e documentação explícita dos campos sem depender
de ORMs externos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class Nivel:
    """Representa uma faixa de nível do sistema."""
    id: int
    nome: str
    xp_minimo: int
    xp_maximo: Optional[int]       # None = nível máximo sem teto
    icone_url: Optional[str]
    criado_em: datetime


@dataclass(frozen=True)
class Medalha:
    """Catálogo de medalhas disponíveis."""
    id: UUID
    nome: str
    tipo: str                       # 'conquista' | 'streak' | 'ranking' | 'especial'
    descricao: Optional[str]
    icone_url: Optional[str]
    criado_em: datetime


@dataclass(frozen=True)
class HistoricoPontos:
    """Registro de um evento de pontuação (imutável após inserção)."""
    id: UUID
    usuario_id: UUID
    pontos: int                     # Positivo = ganho | Negativo = penalidade
    tipo_atividade: str
    criado_em: datetime
    descricao: Optional[str] = None
    referencia_id: Optional[UUID] = None


@dataclass(frozen=True)
class RankingUsuario:
    """Snapshot de pontuação e progressão de um usuário no ranking."""
    usuario_id: UUID
    total_pontos: int
    nivel_id: int
    streak_atual: int
    streak_maximo: int
    atualizado_em: datetime
    ultimo_login: Optional[date] = None
    posicao: Optional[int] = None   # Preenchida pela view vw_ranking_top


@dataclass(frozen=True)
class Conquista:
    """Medalha conquistada por um usuário específico."""
    id: UUID
    usuario_id: UUID
    medalha_id: UUID
    conquistado_em: datetime


@dataclass
class ResultadoInsercaoPontos:
    """
    DTO de resposta da operação inserir_pontos.
    Agrega o histórico criado, o novo total de pontos e
    se houve subida de nível ou novas conquistas.
    """
    historico: HistoricoPontos
    novo_total_pontos: int
    nivel_anterior_id: int
    nivel_atual_id: int
    subiu_de_nivel: bool
    novas_conquistas: list[Conquista] = field(default_factory=list)

    @property
    def resumo(self) -> str:
        """Retorna uma string resumida do resultado para logging."""
        partes = [
            f"Usuário {self.historico.usuario_id}: "
            f"+{self.historico.pontos}pts → total {self.novo_total_pontos}pts"
        ]
        if self.subiu_de_nivel:
            partes.append(f"[LEVEL UP: {self.nivel_anterior_id} → {self.nivel_atual_id}]")
        if self.novas_conquistas:
            partes.append(f"[{len(self.novas_conquistas)} nova(s) conquista(s)]")
        return " | ".join(partes)
