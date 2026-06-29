"""
Rotas da aplicação.
"""

from fastapi import APIRouter, Request, Body, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from services.prova_service import ProvaService
from database.connection import supabase

router = APIRouter()
templates = Jinja2Templates(directory="templates")
service = ProvaService()


def obter_usuario(authorization: str = None):
    """
    Valida o token JWT enviado pelo frontend e retorna o ID do usuário.
    Redireciona para login se não tiver token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    try:
        usuario = supabase.auth.get_user(token)
        return usuario.user.id
    except Exception:
        return None


@router.get("/", response_class=HTMLResponse)
def pagina_inicial(request: Request):
    # Se não tiver token no cookie/header, serve a página normalmente
    # O JS verifica o token e redireciona para /login se necessário
    return templates.TemplateResponse(request=request, name="index.html")


@router.get("/login", response_class=HTMLResponse)
def pagina_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.get("/provas")
def listar_provas():
    return service.listar_provas()


@router.get("/provas/{prova_id}")
def obter_prova(prova_id: str):
    return service.buscar_prova(prova_id)


@router.post("/iniciar")
def iniciar(dados=Body(...), authorization: str = Header(default=None)):
    usuario_id = obter_usuario(authorization)
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Não autenticado.")
    return service.iniciar_tentativa(usuario_id, dados["prova_id"])


@router.post("/finalizar")
def finalizar(dados=Body(...), authorization: str = Header(default=None)):
    usuario_id = obter_usuario(authorization)
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Não autenticado.")
    return service.finalizar_prova(dados["tentativa_id"], dados["respostas"])
