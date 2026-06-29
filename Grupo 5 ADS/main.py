"""
Arquivo principal da aplicação.

Formas de executar:
  - Clique duplo em start.bat (Windows) ou start.sh (Linux/Mac)
  - Ou pelo terminal: python main.py
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.prova_api import router as prova_router
from api.auth_api import router as auth_router

app = FastAPI(title="Sistema Mini Provas", version="1.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(prova_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
