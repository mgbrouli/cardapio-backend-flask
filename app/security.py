"""Autenticação baseada em sessão para endpoints FastAPI."""

from fastapi import Request

from app.services.auth_service import AuthService


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
    return user
