from fastapi import FastAPI

from api.aluno_api import router as aluno_router

from api.desafio_api import router as desafio_router

from api.pontuacao_api import router as pontuacao_router

from api.submissao_api import (
    router as submissao_router
)

app = FastAPI()

app.include_router(aluno_router)
app.include_router(desafio_router)
app.include_router(pontuacao_router)
app.include_router(submissao_router)

@app.get("/")
def home():

    return {
        "mensagem": "Projeto Educacional"
    }