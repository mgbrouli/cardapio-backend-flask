"""Rotas de empresas e configurações autenticadas."""

from pathlib import Path
import logging
import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, PlainTextResponse
from starlette.concurrency import run_in_threadpool

from app.security import get_current_user, verify_csrf_token
from app.services.empresa_service import EmpresaService
from app.services.produto_service import ProdutoService
from app.services.subscription_service import SubscriptionService
from app.templating import templates

router = APIRouter(prefix="/empresa")
logger = logging.getLogger(__name__)
empresa_service = EmpresaService()
produto_service = ProdutoService()
subscription_service = SubscriptionService()
DATA_FIELD_MAX_LENGTHS = {
    "nome_est": 100,
    "cnpj_est": 20,
    "whatsapp": 20,
    "short_description": 255,
    "logradouro": 150,
    "bairro": 100,
    "cidade": 100,
    "estado": 2,
    "cep": 10,
}
COLOR_FIELDS = ("primary_color", "bg_color", "text_color")


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
            "product_count": len(produtos_com_imagens),
            "product_limit": 10 if empresa.plano not in {"pro", "premium"} else None,
            "can_add_product": empresa.plano in {"pro", "premium"}
            or len(produtos_com_imagens) < 10,
            "is_admin": current_user.email.casefold()
            in {
                email.strip().casefold()
                for email in getattr(request.app.state.settings, "ADMIN_EMAILS", "").split(",")
                if email.strip()
            },
        },
    )


async def _get_subscribe(empresa_id: int, request: Request, current_user):
    if current_user.empresa_id != empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    empresa = empresa_service.obter_empresa(empresa_id)
    if not empresa:
        return PlainTextResponse("Empresa não encontrada", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "empresa": empresa,
            "payment_provider": subscription_service.get_active_provider(),
        },
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
    if not verify_csrf_token(request, form.get("csrf_token")):
        return PlainTextResponse("Formulário inválido", status_code=403)
    plan = form.get("plano")
    if plan not in {"pro", "premium"}:
        return PlainTextResponse("Plano inválido", status_code=400)
    if empresa.plano in {"pro", "premium"}:
        return RedirectResponse(url="/empresa/home", status_code=303)

    provider = subscription_service.get_active_provider()
    if not subscription_service.provider_is_configured(provider):
        return templates.TemplateResponse(
            request=request,
            name="checkout.html",
            context={
                "empresa": empresa,
                "payment_provider": provider,
                "erro": "O provedor de pagamento não está configurado pelo administrador.",
            },
            status_code=503,
        )
    pending_url = subscription_service.get_pending_link(empresa.id, plan, provider)
    if pending_url:
        return RedirectResponse(url=pending_url, status_code=303)

    result = await run_in_threadpool(
        subscription_service.create_provider_payment_link,
        empresa.id,
        empresa.name_est,
        plan,
        provider,
        current_user.email,
    )
    if result["success"]:
        saved = subscription_service.save_pending_link(
            empresa.id, plan, provider, result["id"], result["url"]
        )
        return RedirectResponse(url=saved["url"], status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "empresa": empresa,
            "payment_provider": provider,
            "erro": result["message"],
        },
        status_code=503,
    )


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

    is_free = empresa.plano not in {"pro", "premium"}
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return PlainTextResponse("Formulário inválido", status_code=403)
    allowed_fields = list(DATA_FIELD_MAX_LENGTHS)
    if not is_free:
        allowed_fields.extend(COLOR_FIELDS)
    dados = {
        key: form.get(key)
        for key in allowed_fields
        if form.get(key) is not None
    }
    if any(not isinstance(value, str) for value in dados.values()):
        return PlainTextResponse("Dados de configuração inválidos", status_code=400)
    if not dados.get("nome_est", "").strip() or not dados.get("whatsapp", "").strip():
        return PlainTextResponse("Nome e WhatsApp são obrigatórios", status_code=400)
    for field, max_length in DATA_FIELD_MAX_LENGTHS.items():
        value = dados.get(field)
        if value is not None and len(value) > max_length:
            return PlainTextResponse(f"O campo {field} excede o tamanho permitido", status_code=400)
    for field in COLOR_FIELDS:
        value = dados.get(field)
        if value is not None and not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            return PlainTextResponse("Formato de cor inválido", status_code=400)
    base_dir = Path(__file__).resolve().parents[2]
    try:
        allowed_uploads = (("logo_file", "logo"),) if is_free else (
            ("logo_file", "logo"),
            ("banner_file", "banner"),
        )
        for field, tipo in allowed_uploads:
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
    except ValueError as exc:
        return PlainTextResponse(str(exc), status_code=400)
    except Exception:
        logger.exception("Falha ao atualizar configurações da empresa %s", empresa_id)
        return PlainTextResponse("Erro ao salvar as configurações", status_code=500)
