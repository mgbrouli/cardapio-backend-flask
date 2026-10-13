"""Rotas de produtos."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, PlainTextResponse, Response

from app.models import Produtos
from app.security import get_current_user, verify_csrf_token
from app.services.produto_service import ProdutoService
from app.utils.image_utils import MAX_IMAGE_SIZE, validate_image_content

router = APIRouter()
produto_router = APIRouter(prefix="/produto")
produto_service = ProdutoService()


async def _product_form(request: Request, image_field: str):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return form, None, None
    image = form.get(image_field)
    image_name = getattr(image, "filename", None) or None
    image_data = await image.read(MAX_IMAGE_SIZE + 1) if image_name else None
    return form, image_name, image_data


def _validate_product_image(image_name, image_data):
    if not image_data:
        return None
    try:
        validate_image_content(image_name, image_data)
    except ValueError as exc:
        return PlainTextResponse(str(exc), status_code=400)
    return None


async def _create_product(empresa_id: int, request: Request):
    form, image_name, image_data = await _product_form(request, "image")
    if not verify_csrf_token(request, form.get("csrf_token")):
        return PlainTextResponse("Formulário inválido", status_code=403)
    image_error = _validate_product_image(image_name, image_data)
    if image_error:
        return image_error
    result = produto_service.criar_produto(
        empresa_id=empresa_id,
        nome=form.get("nome"),
        ingredientes=form.get("ingredientes") or "",
        preco=form.get("preco"),
        image_name=image_name,
        image_data=image_data,
    )
    if result["success"]:
        return RedirectResponse(url="/empresa/home", status_code=303)
    return PlainTextResponse(result["message"], status_code=400)


@router.post("/add/{empresa_id:int}", name="add_pizza")
async def add_legacy(empresa_id: int, request: Request, current_user=Depends(get_current_user)):
    if current_user.empresa_id != empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    return await _create_product(empresa_id, request)


@produto_router.post("/add/{empresa_id:int}", name="produto.add")
async def add_product(
    empresa_id: int, request: Request, current_user=Depends(get_current_user)
):
    if current_user.empresa_id != empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    return await _create_product(empresa_id, request)


async def _edit_product(produto_id: int, request: Request, current_user):
    product = Produtos.query.get(produto_id)
    if not product or product.empresa_id != current_user.empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)

    form, image_name, image_data = await _product_form(request, "imagem")
    if not verify_csrf_token(request, form.get("csrf_token")):
        return PlainTextResponse("Formulário inválido", status_code=403)
    image_error = _validate_product_image(image_name, image_data)
    if image_error:
        return image_error
    result = produto_service.atualizar_produto(
        produto_id=produto_id,
        nome=form.get("nome"),
        ingredientes=form.get("ingredientes") or "",
        preco=form.get("preco"),
        image_name=image_name,
        image_data=image_data,
    )
    if result["success"]:
        return RedirectResponse(url="/empresa/home", status_code=303)
    return PlainTextResponse(result["message"], status_code=400)


@router.post("/edit/{produto_id:int}", name="edit_pizza")
async def edit_legacy(
    produto_id: int, request: Request, current_user=Depends(get_current_user)
):
    return await _edit_product(produto_id, request, current_user)


@produto_router.post("/edit/{produto_id:int}", name="produto.edit")
async def edit_product(
    produto_id: int, request: Request, current_user=Depends(get_current_user)
):
    return await _edit_product(produto_id, request, current_user)


async def _delete_product(produto_id: int, request: Request, current_user):
    if not verify_csrf_token(request, request.headers.get("x-csrf-token")):
        return PlainTextResponse("Formulário inválido", status_code=403)
    product = Produtos.query.get(produto_id)
    if not product or product.empresa_id != current_user.empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    result = produto_service.deletar_produto(produto_id)
    if result["success"]:
        return Response(status_code=204)
    return PlainTextResponse(result["message"], status_code=400)


@router.delete("/remove/{produto_id:int}", name="delete")
async def delete_legacy(
    produto_id: int, request: Request, current_user=Depends(get_current_user)
):
    return await _delete_product(produto_id, request, current_user)


@produto_router.delete("/delete/{produto_id:int}", name="produto.delete")
async def delete_product(
    produto_id: int, request: Request, current_user=Depends(get_current_user)
):
    return await _delete_product(produto_id, request, current_user)


async def _redirect_config(empresa_id: int, current_user):
    if current_user.empresa_id != empresa_id:
        return PlainTextResponse("Acesso negado", status_code=403)
    return RedirectResponse(url=f"/empresa/config/{empresa_id}", status_code=302)


@router.get("/config/{empresa_id:int}", name="config")
async def config_legacy_get(
    empresa_id: int, current_user=Depends(get_current_user)
):
    return await _redirect_config(empresa_id, current_user)


@router.post("/config/{empresa_id:int}", name="config_update")
async def config_legacy_post(
    empresa_id: int, current_user=Depends(get_current_user)
):
    return await _redirect_config(empresa_id, current_user)


router.include_router(produto_router)
