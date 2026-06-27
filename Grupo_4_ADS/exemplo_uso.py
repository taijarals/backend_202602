"""
exemplo_uso.py — Demonstração completa do módulo de Gamificação.

Execute este arquivo para ver o fluxo completo funcionando:
    python exemplo_uso.py

Pré-requisito: arquivo .env configurado com credenciais válidas do Supabase
e o schema SQL já executado no banco.
"""

import uuid
from config.config import TipoAtividade
from services import (
    buscar_historico_usuario,
    buscar_medalhas_usuario,
    buscar_todos_niveis,
    buscar_top_ranking,
    inserir_pontos,
)

# =============================================================================
# Simula um UUID de usuário existente em auth.users
# Em produção, este ID vem da sessão autenticada do Supabase Auth.
# =============================================================================
USUARIO_DEMO = uuid.UUID("ecf2a886-dee6-4102-acbe-2dc1052d699d")


def demo_fluxo_completo():
    """Demonstra o fluxo completo de gamificação para um usuário."""

    print("\n" + "=" * 60)
    print("  MÓDULO DE GAMIFICAÇÃO — Demo de Fluxo Completo")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Registrar login diário (atualiza streak via trigger)
    # ------------------------------------------------------------------
    print("\n[1] Registrando login diário...")
    resultado_login = inserir_pontos(
        usuario_id=USUARIO_DEMO,
        tipo_atividade=TipoAtividade.LOGIN_DIARIO,
        descricao="Login do dia registrado.",
    )
    print(f"    → {resultado_login.resumo}")

    # ------------------------------------------------------------------
    # 2. Registrar conclusão de quiz com referência ao objeto
    # ------------------------------------------------------------------
    print("\n[2] Registrando conclusão de quiz...")
    id_quiz = uuid.uuid4()
    resultado_quiz = inserir_pontos(
        usuario_id=USUARIO_DEMO,
        tipo_atividade=TipoAtividade.QUIZ_COMPLETO,
        pontos=75,                              # Sobrescreve o padrão de 50pts
        descricao="Quiz de Python Avançado concluído com 90% de acerto.",
        referencia_id=id_quiz,
    )
    print(f"    → {resultado_quiz.resumo}")

    if resultado_quiz.subiu_de_nivel:
        print(f"    🎉 LEVEL UP! Nível {resultado_quiz.nivel_anterior_id} → {resultado_quiz.nivel_atual_id}")

    if resultado_quiz.novas_conquistas:
        print(f"    🏅 Novas conquistas: {len(resultado_quiz.novas_conquistas)} medalha(s) desbloqueada(s)!")

    # ------------------------------------------------------------------
    # 3. Consultar histórico de pontos (paginado)
    # ------------------------------------------------------------------
    print("\n[3] Histórico de pontos (últimas 5 atividades):")
    historico = buscar_historico_usuario(USUARIO_DEMO, limite=5)
    for evento in historico:
        sinal = "+" if evento.pontos >= 0 else ""
        print(f"    [{evento.criado_em:%d/%m %H:%M}] {sinal}{evento.pontos}pts — {evento.tipo_atividade}")

    # ------------------------------------------------------------------
    # 4. Consultar medalhas conquistadas
    # ------------------------------------------------------------------
    print("\n[4] Medalhas do usuário:")
    medalhas = buscar_medalhas_usuario(USUARIO_DEMO)
    if medalhas:
        for m in medalhas:
            print(f"    🏅 {m.nome} ({m.tipo})")
    else:
        print("    Nenhuma medalha conquistada ainda.")

    # ------------------------------------------------------------------
    # 5. Consultar todos os níveis disponíveis
    # ------------------------------------------------------------------
    print("\n[5] Tabela de níveis:")
    niveis = buscar_todos_niveis()
    for n in niveis:
        teto = str(n.xp_maximo) if n.xp_maximo else "∞"
        print(f"    Nível {n.id}: {n.nome:<15} XP [{n.xp_minimo} → {teto})")

    # ------------------------------------------------------------------
    # 6. Top 10 do Ranking Global
    # ------------------------------------------------------------------
    print("\n[6] Top 10 — Ranking Global:")
    top10 = buscar_top_ranking(limite=10)
    if top10:
        for usuario in top10:
            posicao = usuario.posicao or "?"
            print(
                f"    #{posicao:<3} | {str(usuario.usuario_id)[:8]}... | "
                f"{usuario.total_pontos:>6} pts | "
                f"Streak: {usuario.streak_atual}d | "
                f"Nível: {usuario.nivel_id}"
            )
    else:
        print("    Ranking ainda vazio.")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    demo_fluxo_completo()
