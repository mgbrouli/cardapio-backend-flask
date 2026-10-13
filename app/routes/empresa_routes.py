"""Rotas de empresas e configurações autenticadas."""

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, PlainTextResponse

from app.security import get_current_user
from app.services.empresa_service import EmpresaService
from app.services.produto_service import ProdutoService
from app.templating import templates

router = APIRouter(prefix="/empresa")
empresa_service = EmpresaService()
produto_service = ProdutoService()


@router.get("/home", name="empresa.home")
async def home(request: Request, current_user=Depends(get_current_user)):
    empresa_id = current_user.empresa_id
    empresa = empresa_service.obter_empresa(empresa_id)
    if not empresa:
        return PlainTextResponse("Empresa não encontrada", status_code=404)

    produtos_com_imagens = produto_service.obter_produtos_com_imagens(empresa_id)
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "produto": produtos_com_imagens,
            "empresa": empresa,
            "current_user": current_user,
        },
    )


async def _get_subscribe(empresa_id: int, request: Request, current_user):
    if current_user.empresa_id != empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    empresa = empresa_service.obter_empresa(empresa_id)
    if not empresa:
        return PlainTextResponse("Empresa não encontrada", status_code=404)

    return templates.TemplateResponse(
        request=request, name="checkout.html", context={"empresa": empresa}
    )


@router.get("/subscribe/{empresa_id:int}", name="empresa.subscribe")
async def subscribe_page(
    empresa_id: int, request: Request, current_user=Depends(get_current_user)
):
    return await _get_subscribe(empresa_id, request, current_user)


@router.post("/subscribe/{empresa_id:int}", name="empresa.subscribe_update")
async def subscribe(
    empresa_id: int, request: Request, current_user=Depends(get_current_user)
):
    if current_user.empresa_id != empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    empresa = empresa_service.obter_empresa(empresa_id)
    if not empresa:
        return PlainTextResponse("Empresa não encontrada", status_code=404)
    form = await request.form()
    plano = form.get("plano", "pro")
    empresa.plano = plano if plano in {"gratis", "pro", "premium"} else "pro"
    empresa_service.empresa_repo.update(empresa)
    return RedirectResponse(url="/empresa/home", status_code=303)


async def _get_config(
    empresa_id: int, request: Request, current_user
):
    if current_user.empresa_id != empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    empresa = empresa_service.obter_empresa(empresa_id)
    if not empresa:
        return PlainTextResponse("Empresa não encontrada", status_code=404)

    return templates.TemplateResponse(
        request=request, name="config.html", context={"empresa": empresa}
    )


@router.get("/config/{empresa_id:int}", name="empresa.config")
async def config_page(
    empresa_id: int, request: Request, current_user=Depends(get_current_user)
):
    return await _get_config(empresa_id, request, current_user)


@router.post("/config/{empresa_id:int}", name="empresa.config_update")
async def config(
    empresa_id: int, request: Request, current_user=Depends(get_current_user)
):
    if current_user.empresa_id != empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    empresa = empresa_service.obter_empresa(empresa_id)
    if not empresa:
        return PlainTextResponse("Empresa não encontrada", status_code=404)

    form = await request.form()
    dados = {
        key: form.get(key)
        for key in (
            "nome_est",
            "cnpj_est",
            "whatsapp",
            "short_description",
            "logradouro",
            "bairro",
            "cidade",
            "estado",
            "cep",
            "primary_color",
            "bg_color",
            "text_color",
        )
    }
    base_dir = Path(__file__).resolve().parents[2]
    try:
        for field, tipo in (("logo_file", "logo"), ("banner_file", "banner")):
            arquivo = form.get(field)
            if arquivo is not None and getattr(arquivo, "filename", ""):
                dados[f"{tipo}_path"] = empresa_service.processar_upload_arquivo(
                    arquivo, tipo, empresa_id, str(base_dir)
                )

        resultado = empresa_service.atualizar_configuracoes(
            empresa_id, dados, str(base_dir)
        )
        if resultado["success"]:
            return RedirectResponse(url="/empresa/home", status_code=303)
        return PlainTextResponse(resultado["message"], status_code=400)
    except Exception as exc:
        return PlainTextResponse(f"Erro ao salvar: {exc}", status_code=500)
