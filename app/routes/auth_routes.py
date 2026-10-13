"""Rotas de autenticação."""

import logging
import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from starlette.concurrency import run_in_threadpool

from app.security import (
    get_admin_emails,
    get_current_user,
    get_csrf_token,
    verify_csrf_token,
)
from app.services.empresa_service import EmpresaService
from app.services.auth_service import AuthService
from app.services.email_service import is_configured as smtp_is_configured
from app.services.email_verification_service import EmailVerificationService
from app.services.login_rate_limit_service import LoginRateLimitService
from app.services.password_reset_service import PasswordResetService
from app.templating import templates

logger = logging.getLogger(__name__)
router = APIRouter()
auth_service = AuthService()
empresa_service = EmpresaService()
password_reset_service = PasswordResetService()
email_verification_service = EmailVerificationService()
login_rate_limit_service = LoginRateLimitService()


def _landing_context(request, **values):
    return {
        "empresas": empresa_service.listar_empresas_publicas(
            emails_privados=get_admin_emails(request.app.state.settings)
        ),
        **values,
    }


@router.get("/cadastro", name="auth.cadastro")
async def cadastro_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="landing.html", context=_landing_context(request)
    )


@router.post("/cadastro", name="auth.register")
async def cadastro(request: Request):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return templates.TemplateResponse(
            request=request,
            name="landing.html",
            context=_landing_context(request, erro_cadastro="Formulário expirado. Atualize a página e tente novamente."),
            status_code=403,
        )
    email = form.get("email")
    senha = form.get("senha")
    nome_loja = form.get("nome_loja")
    whatsapp = form.get("whatsapp")
    if not all(
        isinstance(value, str)
        for value in (email, senha, nome_loja, whatsapp)
    ) or not all(value.strip() for value in (email, senha, nome_loja, whatsapp)):
        return templates.TemplateResponse(
            request=request,
            name="landing.html",
            context=_landing_context(
                request,
                erro_cadastro="Preencha todos os campos do cadastro."
            ),
            status_code=400,
        )

    email = email.strip().casefold()
    nome_loja = nome_loja.strip()
    whatsapp = whatsapp.strip()
    if (
        len(email) > 254
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
        or not 12 <= len(senha) <= 1024
        or len(nome_loja) > 100
        or len(whatsapp) > 20
    ):
        return templates.TemplateResponse(
            request=request,
            name="landing.html",
            context=_landing_context(
                request,
                erro_cadastro=(
                    "Informe um e-mail válido e uma senha com pelo menos "
                    "12 caracteres."
                ),
            ),
            status_code=400,
        )

    settings = request.app.state.settings
    require_verification = getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False)
    if require_verification and not smtp_is_configured(settings):
        return templates.TemplateResponse(
            request=request,
            name="landing.html",
            context=_landing_context(
                request,
                erro_cadastro=(
                    "O cadastro está temporariamente indisponível porque o "
                    "envio de e-mail não está configurado."
                ),
            ),
            status_code=503,
        )

    resultado = auth_service.registrar_usuario(email, senha, nome_loja, whatsapp)
    if resultado["success"]:
        if require_verification:
            user = auth_service.obter_usuario(resultado["usuario_id"])
            try:
                await run_in_threadpool(
                    email_verification_service.issue_token, user, settings
                )
                return RedirectResponse(url="/login?registered=1", status_code=303)
            except Exception:
                logger.exception("Falha ao enviar confirmação de cadastro")
                return RedirectResponse(url="/login?verification_retry=1", status_code=303)
        return RedirectResponse(url="/login?registered=1", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context=_landing_context(request, erro_cadastro=resultado["message"]),
        status_code=400,
    )


@router.get("/login", name="auth.login")
async def login_page(request: Request):
    info_login = None
    if request.query_params.get("registered") == "1":
        if getattr(request.app.state.settings, "REQUIRE_EMAIL_VERIFICATION", False):
            info_login = (
                "Conta criada. Confirme seu e-mail antes de entrar. "
                "Se a mensagem não chegar, use a opção de reenvio."
            )
        else:
            info_login = "Conta criada. Entre com seu e-mail e senha."
    elif request.query_params.get("verification_retry") == "1":
        info_login = (
            "A conta foi criada, mas o envio da confirmação falhou. "
            "Use a opção de reenvio da confirmação."
        )
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context=_landing_context(
            request, erro_login=None, info_login=info_login, email_login=None
        ),
    )


@router.get("/reenviar-verificacao", name="auth.resend_verification_page")
async def resend_verification_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="email_verification.html",
        context={"stage": "resend"},
    )


@router.post("/reenviar-verificacao", name="auth.resend_verification")
async def resend_verification(request: Request):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return templates.TemplateResponse(
            request=request,
            name="email_verification.html",
            context={
                "stage": "resend",
                "error": "Formulário expirado. Atualize a página e tente novamente.",
            },
            status_code=403,
        )
    email = form.get("email")
    if isinstance(email, str) and email.strip():
        user = auth_service.usuario_repo.get_by_email(email.strip().casefold())
        if user is not None and not email_verification_service.is_verified(user.id):
            try:
                await run_in_threadpool(
                    email_verification_service.issue_token,
                    user,
                    request.app.state.settings,
                )
            except Exception:
                logger.exception("Falha ao reenviar confirmação de e-mail")

    return templates.TemplateResponse(
        request=request,
        name="email_verification.html",
        context={
            "stage": "resend",
            "message": (
                "Se a conta precisar de confirmação, enviaremos um link para "
                "o endereço cadastrado. O link expira em 24 horas."
            ),
        },
    )


@router.get("/verificar-email/{token}", name="auth.verify_email_page")
async def verify_email_page(request: Request, token: str):
    response = templates.TemplateResponse(
        request=request,
        name="email_verification.html",
        context={"stage": "confirm", "token": token},
    )
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    return response


@router.post("/verificar-email/{token}", name="auth.verify_email")
async def verify_email(request: Request, token: str):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return templates.TemplateResponse(
            request=request,
            name="email_verification.html",
            context={
                "stage": "confirm",
                "token": token,
                "error": "Formulário expirado. Atualize a página e tente novamente.",
            },
            status_code=403,
        )
    verified = await run_in_threadpool(
        email_verification_service.verify_token, token
    )
    return templates.TemplateResponse(
        request=request,
        name="email_verification.html",
        context={
            "stage": "complete" if verified else "invalid",
            "message": (
                "E-mail confirmado. Agora você já pode entrar."
                if verified
                else "Link inválido ou expirado. Solicite um novo link de confirmação."
            ),
        },
        status_code=200 if verified else 400,
    )


@router.get("/redefinir-senha", name="auth.request_password_reset")
async def request_password_reset_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="password_reset.html",
        context={"stage": "request"},
    )


@router.post("/redefinir-senha", name="auth.send_password_reset")
async def send_password_reset(request: Request):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return templates.TemplateResponse(
            request=request,
            name="password_reset.html",
            context={
                "stage": "request",
                "error": "Formulário expirado. Atualize a página e tente novamente.",
            },
            status_code=403,
        )

    email = form.get("email")
    if not isinstance(email, str) or not email.strip():
        return templates.TemplateResponse(
            request=request,
            name="password_reset.html",
            context={"stage": "request", "error": "Informe um e-mail válido."},
            status_code=400,
        )

    try:
        await run_in_threadpool(
            password_reset_service.request_reset,
            email,
            request.app.state.settings,
        )
    except Exception:
        logger.exception("Falha ao processar pedido de redefinição de senha")

    return templates.TemplateResponse(
        request=request,
        name="password_reset.html",
        context={
            "stage": "request",
            "message": (
                "Se houver uma conta associada a esse e-mail, enviaremos um link "
                "de redefinição válido por 1 hora."
            ),
        },
    )


@router.get(
    "/redefinir-senha/{token}",
    name="auth.reset_password_form",
)
async def reset_password_page(request: Request, token: str):
    return templates.TemplateResponse(
        request=request,
        name="password_reset.html",
        context={"stage": "reset", "token": token},
    )


@router.post(
    "/redefinir-senha/{token}",
    name="auth.reset_password",
)
async def reset_password(request: Request, token: str):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return templates.TemplateResponse(
            request=request,
            name="password_reset.html",
            context={
                "stage": "reset",
                "token": token,
                "error": "Formulário expirado. Atualize a página e tente novamente.",
            },
            status_code=403,
        )

    password = form.get("password")
    password_confirmation = form.get("password_confirmation")
    if not isinstance(password, str) or not isinstance(password_confirmation, str):
        password = ""
        password_confirmation = ""
    if password != password_confirmation:
        return templates.TemplateResponse(
            request=request,
            name="password_reset.html",
            context={
                "stage": "reset",
                "token": token,
                "error": "As senhas não coincidem.",
            },
            status_code=400,
        )
    if not 12 <= len(password) <= 1024:
        return templates.TemplateResponse(
            request=request,
            name="password_reset.html",
            context={
                "stage": "reset",
                "token": token,
                "error": "A senha deve ter entre 12 e 1024 caracteres.",
            },
            status_code=400,
        )

    if await run_in_threadpool(
        password_reset_service.reset_password, token, password
    ):
        return templates.TemplateResponse(
            request=request,
            name="password_reset.html",
            context={
                "stage": "complete",
                "message": "Senha redefinida. Você já pode entrar com a nova senha.",
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="password_reset.html",
        context={
            "stage": "reset",
            "error": "Link inválido ou expirado. Solicite uma nova redefinição.",
        },
        status_code=400,
    )


@router.post("/login", name="auth.authenticate")
async def login(request: Request):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return templates.TemplateResponse(
            request=request,
            name="landing.html",
            context=_landing_context(
                request,
                erro_login="Formulário expirado. Atualize a página e tente novamente.",
                email_login=None,
            ),
            status_code=403,
        )
    email_value = form.get("email")
    email = email_value.strip().casefold() if isinstance(email_value, str) else ""
    password = form.get("senha")
    senha = password if isinstance(password, str) else ""
    settings = request.app.state.settings
    remote_ip = request.client.host if request.client else "unknown"
    secret_key = getattr(settings, "SECRET_KEY", "")
    if login_rate_limit_service.is_limited(email, remote_ip, secret_key):
        response = templates.TemplateResponse(
            request=request,
            name="landing.html",
            context=_landing_context(
                request,
                erro_login="Muitas tentativas. Aguarde 15 minutos e tente novamente.",
                email_login=email,
            ),
            status_code=429,
        )
        response.headers["Retry-After"] = "900"
        return response

    resultado = (
        auth_service.validar_credenciais(email, senha)
        if email and senha and len(email) <= 254 and len(senha) <= 1024
        else {"success": False, "message": "Credenciais inválidas"}
    )
    if resultado["success"]:
        user = resultado["usuario"]
        if (
            getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False)
            and not email_verification_service.is_verified(user.id)
        ):
            return templates.TemplateResponse(
                request=request,
                name="landing.html",
                context=_landing_context(
                    request,
                    erro_login=(
                        "Confirme seu e-mail antes de entrar. "
                        "Você pode solicitar outro link de confirmação abaixo."
                    ),
                    email_login=email,
                ),
            )
        login_rate_limit_service.clear(email, remote_ip, secret_key)
        request.session.clear()
        request.session["user_id"] = user.id
        get_csrf_token(request)
        return RedirectResponse(url="/empresa/home", status_code=303)

    login_rate_limit_service.record_failure(email, remote_ip, secret_key)
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context=_landing_context(
            request,
            erro_login="E-mail ou senha inválidos.", email_login=email
        ),
    )


@router.post("/logout", name="auth.logout")
async def logout(request: Request):
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token")):
        return PlainTextResponse("Formulário inválido", status_code=403)
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@router.get(
    "/session/heartbeat",
    name="auth.heartbeat",
    include_in_schema=False,
    dependencies=[Depends(get_current_user)],
)
async def heartbeat():
    return Response(status_code=204)
