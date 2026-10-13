"""Factory da aplicação FastAPI."""

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.database import request_scope
from app.models import db
from app.security import AuthenticationRequired
from config import DEFAULT_SECRET_KEY, get_config

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app(config=None):
    """Cria e configura a aplicação FastAPI."""
    settings = config or get_config()
    secret_key = getattr(settings, "SECRET_KEY")
    if not getattr(settings, "DEBUG", False) and secret_key == DEFAULT_SECRET_KEY:
        raise RuntimeError("Defina uma SECRET_KEY aleatória antes de iniciar em produção.")
    app = FastAPI(title="Cardápio Digital", version="1.0.0")
    app.state.settings = settings

    database_url = getattr(settings, "SQLALCHEMY_DATABASE_URI")
    db.configure(database_url)
    db.create_all()

    app.add_middleware(
        SessionMiddleware,
        secret_key=secret_key,
        max_age=7 * 24 * 60 * 60,
        same_site="lax",
        https_only=not getattr(settings, "DEBUG", False),
    )

    from app.routes.auth_routes import router as auth_router
    from app.routes.admin_routes import router as admin_router
    from app.routes.empresa_routes import router as empresa_router
    from app.routes.produto_routes import router as produto_router
    from app.routes.public_routes import router as public_router
    from app.routes.webhook_routes import router as webhook_router

    @app.middleware("http")
    async def database_session_scope(request: Request, call_next):
        token = request_scope.set(uuid4().hex)
        try:
            return await call_next(request)
        finally:
            db.session.remove()
            request_scope.reset(token)

    @app.exception_handler(AuthenticationRequired)
    async def redirect_unauthenticated(request: Request, exc: AuthenticationRequired):
        return RedirectResponse(
            url=request.url_for("auth.login").path, status_code=exc.status_code
        )

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
    app.include_router(public_router)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(empresa_router)
    app.include_router(produto_router)
    app.include_router(webhook_router)

    return app
