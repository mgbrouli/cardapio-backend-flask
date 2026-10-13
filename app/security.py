"""Autenticação baseada em sessão para endpoints FastAPI."""

from datetime import datetime, timedelta, timezone
import hmac
import secrets

from fastapi import Depends, HTTPException, Request

from app.database import db
from app.models import UserActivity
from app.services.auth_service import AuthService


def get_csrf_token(request: Request):
    token = request.session.get("csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def verify_csrf_token(request: Request, supplied_token):
    expected_token = request.session.get("csrf_token")
    return bool(
        isinstance(expected_token, str)
        and isinstance(supplied_token, str)
        and hmac.compare_digest(expected_token, supplied_token)
    )


class AuthenticationRequired(Exception):
    """Indica que a sessão não contém um usuário autenticado."""

    status_code = 302


def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise AuthenticationRequired

    try:
        user = AuthService().obter_usuario(int(user_id))
    except (TypeError, ValueError):
        user = None

    if user is None:
        request.session.clear()
        raise AuthenticationRequired

    now = datetime.now(timezone.utc)
    activity = db.session.get(UserActivity, user.id)
    if activity is None:
        db.session.add(UserActivity(user_id=user.id, last_seen_at=now))
        db.session.commit()
    else:
        last_seen = activity.last_seen_at
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        if now - last_seen >= timedelta(minutes=1):
            activity.last_seen_at = now
            db.session.commit()
    return user


def get_current_admin(
    request: Request, current_user=Depends(get_current_user)
):
    if not is_admin_email(current_user.email, request.app.state.settings):
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador")
    return current_user


def get_admin_emails(settings):
    return {
        email.strip().casefold()
        for email in getattr(settings, "ADMIN_EMAILS", "").split(",")
        if email.strip()
    }


def is_admin_email(email, settings):
    return isinstance(email, str) and email.casefold() in get_admin_emails(settings)
