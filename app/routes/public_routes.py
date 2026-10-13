"""Rotas públicas (sem autenticação)."""

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, RedirectResponse

from app.security import get_admin_emails, is_admin_email
from app.services.empresa_service import EmpresaService
from app.services.produto_service import ProdutoService
from app.templating import templates

router = APIRouter()
produto_service = ProdutoService()
empresa_service = EmpresaService()


@router.get("/", name="public.landing")
async def landing(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={
            "empresas": empresa_service.listar_empresas_publicas(
                emails_privados=get_admin_emails(request.app.state.settings)
            )
        },
    )


@router.get("/{empresa_id:int}", name="public.menu")
async def index(empresa_id: int, request: Request):
    empresa = empresa_service.obter_empresa(empresa_id)
    if not empresa:
        return RedirectResponse(url="/", status_code=302)
    owner = empresa.dono
    if owner and is_admin_email(owner.email, request.app.state.settings):
        response = templates.TemplateResponse(
            request=request,
            name="support.html",
            context={},
        )
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        response.headers["Cache-Control"] = "no-store"
        return response
    if not empresa.ativo:
        return PlainTextResponse(
            "Este cardápio está temporariamente suspenso. "
            "Entre em contato com o administrador.",
            status_code=403,
        )

    produtos_com_imagens = produto_service.obter_produtos_com_imagens(empresa_id)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"produto": produtos_com_imagens, "empresa": empresa},
    )
