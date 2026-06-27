"""
Ponto de entrada da aplicação FastAPI da Plataforma Educacional.

Registra os routers de cada módulo do sistema. Outros módulos (desafios,
mini-provas, feedback, equipes, missões) devem ser incluídos da mesma forma
que o módulo de Gamificação abaixo.
"""

from fastapi import FastAPI

from routers import gamificacao

app = FastAPI(
    title="Plataforma Educacional - API",
    description="API da Plataforma Educacional Colaborativa (Módulo de Gamificação).",
    version="1.0.0",
)

app.include_router(gamificacao.router)


@app.get("/", tags=["Status"])
async def status_da_api() -> dict:
    """Endpoint simples para verificar se a API está no ar."""
    return {"status": "online", "mensagem": "API da Plataforma Educacional rodando com sucesso."}
