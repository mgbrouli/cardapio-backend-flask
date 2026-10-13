"""Rotas de autenticação."""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.services.empresa_service import EmpresaService
from app.services.auth_service import AuthService
from app.templating import templates

router = APIRouter()
auth_service = AuthService()
empresa_service = EmpresaService()


def _landing_context(**values):
    return {
        "empresas": empresa_service.listar_empresas_publicas(),
        **values,
    }


@router.get("/cadastro", name="auth.cadastro")
async def cadastro_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="landing.html", context=_landing_context()
    )


@router.post("/cadastro", name="auth.register")
async def cadastro(request: Request):
    form = await request.form()
    email = form.get("email")
    senha = form.get("senha")
    nome_loja = form.get("nome_loja")
    whatsapp = form.get("whatsapp")
    if not all((email, senha, nome_loja, whatsapp)):
        return templates.TemplateResponse(
            request=request,
            name="landing.html",
            context=_landing_context(
                erro_cadastro="Preencha todos os campos do cadastro."
            ),
            status_code=400,
        )

    resultado = auth_service.registrar_usuario(email, senha, nome_loja, whatsapp)
    if resultado["success"]:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context=_landing_context(erro_cadastro=resultado["message"]),
        status_code=400,
    )


@router.get("/login", name="auth.login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context=_landing_context(erro_login=None, email_login=None),
    )


@router.post("/login", name="auth.authenticate")
async def login(request: Request):
    form = await request.form()
    email = form.get("email")
    senha = form.get("senha")
    resultado = (
        auth_service.validar_credenciais(email, senha)
        if email and senha
        else {"success": False, "message": "Informe e-mail e senha"}
    )
    if resultado["success"]:
        request.session["user_id"] = resultado["usuario"].id
        return RedirectResponse(url="/empresa/home", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context=_landing_context(
            erro_login=resultado["message"], email_login=email
        ),
    )


@router.get("/logout", name="auth.logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
