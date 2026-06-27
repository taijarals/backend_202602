"""
services.py — Camada de Serviços e Regras de Negócio do módulo de Gamificação.

Cada função desta camada representa um caso de uso completo:
    - Comunica-se EXCLUSIVAMENTE com o Supabase via `supabase-py`.
    - Não expõe detalhes do banco para cima (retorna modelos/DTOs).
    - Toda lógica de negócio sensível ao estado do DB é delegada
      aos Triggers SQL (cálculo de pontos totais, streak, nível).
    - Funções Python tratam apenas orquestração e regras que dependem
      de múltiplas consultas ou contexto de aplicação.

Dependências:
    pip install supabase python-dotenv

Não criar rotas de API aqui — esta camada é consumida pelos controllers.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from postgrest.exceptions import APIError

from config.config import supabase, Tabelas, TipoAtividade, Views, PONTOS_PADRAO
from models.models import (
    Conquista,
    HistoricoPontos,
    Medalha,
    Nivel,
    RankingUsuario,
    ResultadoInsercaoPontos,
)

logger = logging.getLogger(__name__)


# =============================================================================
# UTILITÁRIOS INTERNOS
# =============================================================================

def _parse_uuid(value: str | UUID) -> UUID:
    """Garante que o valor retornado seja sempre um UUID tipado."""
    return UUID(str(value)) if not isinstance(value, UUID) else value


def _row_to_historico(row: dict) -> HistoricoPontos:
    """Converte um dicionário raw do Supabase em HistoricoPontos."""
    return HistoricoPontos(
        id=_parse_uuid(row["id"]),
        usuario_id=_parse_uuid(row["usuario_id"]),
        pontos=row["pontos"],
        tipo_atividade=row["tipo_atividade"],
        descricao=row.get("descricao"),
        referencia_id=_parse_uuid(row["referencia_id"]) if row.get("referencia_id") else None,
        criado_em=datetime.fromisoformat(row["criado_em"]),
    )


def _row_to_ranking(row: dict) -> RankingUsuario:
    """Converte um dicionário raw do Supabase em RankingUsuario."""
    return RankingUsuario(
        usuario_id=_parse_uuid(row["usuario_id"]),
        total_pontos=row["total_pontos"],
        nivel_id=row.get("nivel_id", 1),
        streak_atual=row["streak_atual"],
        streak_maximo=row["streak_maximo"],
        ultimo_login=date.fromisoformat(row["ultimo_login"]) if row.get("ultimo_login") else None,
        atualizado_em=datetime.fromisoformat(row["atualizado_em"]) if row.get("atualizado_em") else None,
        posicao=row.get("posicao"),
    )


def _row_to_conquista(row: dict) -> Conquista:
    """Converte um dicionário raw do Supabase em Conquista."""
    return Conquista(
        id=_parse_uuid(row["id"]),
        usuario_id=_parse_uuid(row["usuario_id"]),
        medalha_id=_parse_uuid(row["medalha_id"]),
        conquistado_em=datetime.fromisoformat(row["conquistado_em"]),
    )


# =============================================================================
# SERVIÇO: PONTOS E HISTÓRICO
# =============================================================================

def inserir_pontos(
    usuario_id: str | UUID,
    tipo_atividade: TipoAtividade,
    pontos: Optional[int] = None,
    descricao: Optional[str] = None,
    referencia_id: Optional[str | UUID] = None,
) -> ResultadoInsercaoPontos:
    """
    Registra um evento de pontuação para o usuário e retorna o resultado completo.

    O Trigger `trg_atualizar_ranking` no banco cuida automaticamente de:
        - Somar o delta ao total de pontos.
        - Recalcular o nível atual.
        - Atualizar o streak (quando tipo_atividade == 'login_diario').

    Args:
        usuario_id:      UUID do usuário (auth.users).
        tipo_atividade:  Categoria do evento (use TipoAtividade).
        pontos:          Quantidade de pontos. Se None, usa PONTOS_PADRAO.
        descricao:       Texto livre para exibição ao usuário.
        referencia_id:   UUID do recurso que originou o evento (opcional).

    Returns:
        ResultadoInsercaoPontos com histórico criado, totais e flags de level-up.

    Raises:
        APIError: Em falhas de comunicação com o Supabase.
        ValueError: Se tipo_atividade for inválido.
    """
    uid = str(_parse_uuid(usuario_id))
    delta = pontos if pontos is not None else PONTOS_PADRAO[tipo_atividade]

    # Captura o nível ANTES da inserção para detectar level-up
    nivel_anterior = _buscar_nivel_usuario(uid)

    payload: dict = {
        "usuario_id":     uid,
        "pontos":         delta,
        "tipo_atividade": str(tipo_atividade),
        "descricao":      descricao,
    }
    if referencia_id:
        payload["referencia_id"] = str(_parse_uuid(referencia_id))

    try:
        resp = (
            supabase.table(Tabelas.HISTORICO_PONTOS)
            .insert(payload)
            .execute()
        )
    except APIError as exc:
        logger.error("Falha ao inserir pontos para usuario=%s: %s", uid, exc)
        raise

    historico = _row_to_historico(resp.data[0])

    # Aguarda o trigger propagar e busca o estado atualizado
    ranking_atual = buscar_ranking_usuario(uid)
    novas_conquistas = _verificar_e_conceder_conquistas(uid, ranking_atual)

    resultado = ResultadoInsercaoPontos(
        historico=historico,
        novo_total_pontos=ranking_atual.total_pontos,
        nivel_anterior_id=nivel_anterior,
        nivel_atual_id=ranking_atual.nivel_id,
        subiu_de_nivel=ranking_atual.nivel_id != nivel_anterior,
        novas_conquistas=novas_conquistas,
    )

    logger.info(resultado.resumo)
    return resultado


def buscar_historico_usuario(
    usuario_id: str | UUID,
    limite: int = 20,
    offset: int = 0,
    tipo_atividade: Optional[TipoAtividade] = None,
) -> list[HistoricoPontos]:
    """
    Retorna o histórico de pontos de um usuário, do mais recente para o mais antigo.

    Args:
        usuario_id:     UUID do usuário.
        limite:         Máximo de registros retornados (padrão: 20).
        offset:         Paginação — registros a pular (padrão: 0).
        tipo_atividade: Filtro opcional por categoria de atividade.

    Returns:
        Lista de HistoricoPontos ordenada por data decrescente.

    Raises:
        APIError: Em falhas de comunicação com o Supabase.
    """
    uid = str(_parse_uuid(usuario_id))

    query = (
        supabase.table(Tabelas.HISTORICO_PONTOS)
        .select("*")
        .eq("usuario_id", uid)
        .order("criado_em", desc=True)
        .range(offset, offset + limite - 1)
    )

    if tipo_atividade:
        query = query.eq("tipo_atividade", str(tipo_atividade))

    try:
        resp = query.execute()
    except APIError as exc:
        logger.error("Falha ao buscar histórico de usuario=%s: %s", uid, exc)
        raise

    return [_row_to_historico(row) for row in resp.data]


# =============================================================================
# SERVIÇO: RANKING
# =============================================================================

def buscar_ranking_usuario(usuario_id: str | UUID) -> RankingUsuario:
    """
    Retorna o snapshot de ranking de um único usuário.

    Args:
        usuario_id: UUID do usuário.

    Returns:
        RankingUsuario com total de pontos, nível, streak e posição global.

    Raises:
        APIError:  Em falhas de comunicação.
        LookupError: Se o usuário não possui registro no ranking.
    """
    uid = str(_parse_uuid(usuario_id))

    try:
        resp = (
            supabase.table(Views.RANKING_TOP)
            .select("*")
            .eq("usuario_id", uid)
            .single()
            .execute()
        )
    except APIError as exc:
        logger.error("Falha ao buscar ranking de usuario=%s: %s", uid, exc)
        raise

    if not resp.data:
        raise LookupError(f"Usuário {uid} não encontrado no ranking.")

    # .single() retorna um dict diretamente em resp.data (não uma lista)
    return _row_to_ranking(resp.data if isinstance(resp.data, dict) else resp.data[0])


def buscar_top_ranking(limite: int = 10) -> list[RankingUsuario]:
    """
    Retorna os N melhores usuários do ranking global, ordenados por pontuação.

    Utiliza a view `vw_ranking_top` que calcula a posição via RANK() no banco.

    Args:
        limite: Quantidade de posições a retornar (padrão: 10).

    Returns:
        Lista de RankingUsuario ordenada por posição (1º ao Nº).

    Raises:
        APIError: Em falhas de comunicação com o Supabase.
    """
    try:
        resp = (
            supabase.table(Views.RANKING_TOP)
            .select("*")
            .order("total_pontos", desc=True)
            .limit(limite)
            .execute()
        )
    except APIError as exc:
        logger.error("Falha ao buscar top %d do ranking: %s", limite, exc)
        raise

    return [_row_to_ranking(row) for row in resp.data]


# =============================================================================
# SERVIÇO: NÍVEL
# =============================================================================

def _buscar_nivel_usuario(usuario_id: str) -> int:
    """
    Busca o nivel_id atual do usuário diretamente na tabela ranking.
    Retorna 1 (Iniciante) como fallback se não existir registro.

    Args:
        usuario_id: UUID como string.

    Returns:
        ID do nível atual do usuário.
    """
    try:
        resp = (
            supabase.table(Tabelas.RANKING)
            .select("nivel_id")
            .eq("usuario_id", usuario_id)
            .maybe_single()
            .execute()
        )
        return resp.data["nivel_id"] if resp and hasattr(resp, "data") and resp.data else 1
    except APIError:
        return 1


def buscar_todos_niveis() -> list[Nivel]:
    """
    Retorna todos os níveis cadastrados, ordenados pelo XP mínimo.

    Returns:
        Lista de Nivel do menor para o maior.

    Raises:
        APIError: Em falhas de comunicação com o Supabase.
    """
    try:
        resp = (
            supabase.table(Tabelas.NIVEL)
            .select("*")
            .order("xp_minimo", desc=False)
            .execute()
        )
    except APIError as exc:
        logger.error("Falha ao buscar níveis: %s", exc)
        raise

    return [
        Nivel(
            id=row["id"],
            nome=row["nome"],
            xp_minimo=row["xp_minimo"],
            xp_maximo=row.get("xp_maximo"),
            icone_url=row.get("icone_url"),
            criado_em=datetime.fromisoformat(row["criado_em"]),
        )
        for row in resp.data
    ]


# =============================================================================
# SERVIÇO: MEDALHAS E CONQUISTAS
# =============================================================================

def buscar_medalhas_usuario(usuario_id: str | UUID) -> list[Medalha]:
    """
    Retorna todas as medalhas já conquistadas por um usuário.

    Realiza um JOIN via Supabase entre `conquista` e `medalha`.

    Args:
        usuario_id: UUID do usuário.

    Returns:
        Lista de Medalha ordenada pela data de conquista (mais recente primeiro).

    Raises:
        APIError: Em falhas de comunicação com o Supabase.
    """
    uid = str(_parse_uuid(usuario_id))

    try:
        resp = (
            supabase.table(Tabelas.CONQUISTA)
            .select("conquistado_em, medalha(*)")
            .eq("usuario_id", uid)
            .order("conquistado_em", desc=True)
            .execute()
        )
    except APIError as exc:
        logger.error("Falha ao buscar medalhas de usuario=%s: %s", uid, exc)
        raise

    medalhas: list[Medalha] = []
    for row in resp.data:
        m = row["medalha"]
        medalhas.append(
            Medalha(
                id=_parse_uuid(m["id"]),
                nome=m["nome"],
                tipo=m["tipo"],
                descricao=m.get("descricao"),
                icone_url=m.get("icone_url"),
                criado_em=datetime.fromisoformat(m["criado_em"]),
            )
        )
    return medalhas


def conceder_medalha(
    usuario_id: str | UUID,
    medalha_id: str | UUID,
) -> Conquista | None:
    """
    Concede uma medalha ao usuário se ele ainda não a possui.

    A restrição UNIQUE (usuario_id, medalha_id) no banco previne duplicatas;
    esta função trata o conflito de forma silenciosa retornando None.

    Args:
        usuario_id: UUID do usuário.
        medalha_id: UUID da medalha a conceder.

    Returns:
        Conquista recém-criada, ou None se o usuário já possui a medalha.

    Raises:
        APIError: Em falhas inesperadas de comunicação.
    """
    uid = str(_parse_uuid(usuario_id))
    mid = str(_parse_uuid(medalha_id))

    try:
        resp = (
            supabase.table(Tabelas.CONQUISTA)
            .insert({"usuario_id": uid, "medalha_id": mid})
            .execute()
        )
        conquista = _row_to_conquista(resp.data[0])
        logger.info("Medalha %s concedida ao usuário %s.", mid, uid)
        return conquista

    except APIError as exc:
        # Código 23505 = unique_violation (medalha já concedida)
        if "23505" in str(exc):
            logger.debug("Usuário %s já possui a medalha %s.", uid, mid)
            return None
        logger.error("Falha ao conceder medalha %s ao usuario=%s: %s", mid, uid, exc)
        raise


# =============================================================================
# REGRAS DE NEGÓCIO: VERIFICAÇÃO AUTOMÁTICA DE CONQUISTAS
# =============================================================================

# Mapeamento de regras: nome da medalha → função verificadora
# Adicionar novas regras aqui sem alterar o restante do código.
_REGRAS_CONQUISTAS: dict[str, callable] = {}


def _regra(nome_medalha: str):
    """Decorator para registrar uma função como regra de conquista."""
    def decorator(fn):
        _REGRAS_CONQUISTAS[nome_medalha] = fn
        return fn
    return decorator


@_regra("Primeira Conquista")
def _regra_primeira_conquista(ranking: RankingUsuario) -> bool:
    """Concedida quando o usuário acumula qualquer ponto."""
    return ranking.total_pontos > 0


@_regra("Semana Perfeita")
def _regra_semana_perfeita(ranking: RankingUsuario) -> bool:
    """Concedida ao atingir 7 dias de streak consecutivos."""
    return ranking.streak_atual >= 7


@_regra("Mês Dedicado")
def _regra_mes_dedicado(ranking: RankingUsuario) -> bool:
    """Concedida ao atingir 30 dias de streak consecutivos."""
    return ranking.streak_atual >= 30


@_regra("Centurião")
def _regra_centuriao(ranking: RankingUsuario) -> bool:
    """Concedida ao acumular 100 pontos ou mais."""
    return ranking.total_pontos >= 100


def _verificar_e_conceder_conquistas(
    usuario_id: str,
    ranking: RankingUsuario,
) -> list[Conquista]:
    """
    Avalia todas as regras de conquista e concede as medalhas elegíveis.

    Busca o catálogo de medalhas do banco, filtra pelas que têm regra
    registrada e tenta conceder as elegíveis (conceder_medalha ignora
    duplicatas silenciosamente).

    Args:
        usuario_id: UUID como string.
        ranking:    Estado atual de ranking do usuário (pós-inserção).

    Returns:
        Lista de Conquista efetivamente criadas nesta verificação.
    """
    try:
        resp = (
            supabase.table(Tabelas.MEDALHA)
            .select("id, nome")
            .in_("nome", list(_REGRAS_CONQUISTAS.keys()))
            .execute()
        )
    except APIError as exc:
        logger.warning("Falha ao buscar medalhas para verificação: %s", exc)
        return []

    novas: list[Conquista] = []
    for row in resp.data:
        regra = _REGRAS_CONQUISTAS.get(row["nome"])
        if regra and regra(ranking):
            conquista = conceder_medalha(usuario_id, row["id"])
            if conquista:
                novas.append(conquista)

    return novas
