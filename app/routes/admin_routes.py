"""Painel administrativo da plataforma."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.database import db
from app.models import Empresa, Produtos, UserActivity, Usuario
from app.security import get_current_admin, verify_csrf_token
from app.services.subscription_service import SubscriptionService
from app.templating import templates

router = APIRouter()
subscription_service = SubscriptionService()


@router.get("/admin", name="admin.dashboard")
async def dashboard(request: Request, admin=Depends(get_current_admin)):
    online_since = datetime.now(timezone.utc) - timedelta(minutes=15)
    company_count = db.session.query(func.count(Empresa.id)).scalar() or 0
    user_count = db.session.query(func.count(Usuario.id)).scalar() or 0
    product_count = db.session.query(func.count(Produtos.id)).scalar() or 0
    online_users = (
        db.session.query(func.count(UserActivity.user_id))
        .filter(UserActivity.last_seen_at >= online_since)
        .scalar()
        or 0
    )
    plans = dict(
        db.session.query(Empresa.plano, func.count(Empresa.id))
        .group_by(Empresa.plano)
        .all()
    )
    recent_users = (
        db.session.query(Usuario, UserActivity.last_seen_at)
        .outerjoin(UserActivity, UserActivity.user_id == Usuario.id)
        .options(joinedload(Usuario.empresa))
        .order_by(UserActivity.last_seen_at.desc())
        .limit(100)
        .all()
    )
    recent_users = [
        (
            user,
            last_seen.replace(tzinfo=timezone.utc)
            if last_seen and last_seen.tzinfo is None
            else last_seen,
        )
        for user, last_seen in recent_users
    ]
    companies = (
        db.session.query(Empresa, Usuario.email, func.count(Produtos.id))
        .outerjoin(Usuario, Usuario.empresa_id == Empresa.id)
        .outerjoin(Produtos, Produtos.empresa_id == Empresa.id)
        .group_by(Empresa.id, Usuario.id)
        .order_by(Empresa.id.desc())
        .limit(100)
        .all()
    )
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "admin": admin,
            "company_count": company_count,
            "user_count": user_count,
            "product_count": product_count,
            "online_users": online_users,
            "plans": plans,
            "recent_users": recent_users,
            "companies": companies,
            "online_since": online_since,
            "payment_provider": subscription_service.get_active_provider(),
            "provider_configured": {
                provider: subscription_service.provider_is_configured(provider)
                for provider in ("asaas", "stripe")
            },
        },
    )


@router.post(
    "/admin/payment-provider",
    name="admin.payment_provider",
    dependencies=[Depends(get_current_admin)],
)
async def update_payment_provider(request: Request):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return PlainTextResponse("Formulário inválido", status_code=403)
    result = subscription_service.set_active_provider(form.get("provider"))
    if not result["success"]:
        return PlainTextResponse(result["message"], status_code=400)
    return RedirectResponse(url="/admin", status_code=303)
