"""Emissão e validação de tokens de redefinição de senha."""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr

from sqlalchemy import func

from app.database import db
from app.models import EmailVerification, PasswordResetToken, Usuario
from app.services.auth_service import password_hasher
from app.services.email_service import send_email

logger = logging.getLogger(__name__)
TOKEN_LIFETIME = timedelta(hours=1)
REQUEST_COOLDOWN = timedelta(minutes=1)
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 1024


class PasswordResetService:
    def request_reset(self, email, settings):
        """Envia um link de redefinição, sem revelar se o e-mail está cadastrado."""
        user = Usuario.query.filter(
            func.lower(Usuario.email) == email.strip().lower()
        ).first()
        if user is None:
            return

        now = datetime.now(timezone.utc)
        previous_token = (
            db.session.query(PasswordResetToken)
            .filter_by(user_id=user.id)
            .order_by(PasswordResetToken.created_at.desc())
            .first()
        )
        if previous_token is not None:
            created_at = previous_token.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if now - created_at < REQUEST_COOLDOWN:
                return

        mail_username = getattr(settings, "MAIL_USERNAME", "")
        if not mail_username:
            raise RuntimeError("SMTP de envio de e-mail não está configurado")

        token = secrets.token_urlsafe(32)
        db.session.query(PasswordResetToken).filter_by(user_id=user.id).delete()
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            expires_at=now + TOKEN_LIFETIME,
            created_at=now,
        )
        db.session.add(reset_token)
        db.session.commit()

        base_url = getattr(settings, "PUBLIC_BASE_URL", "").rstrip("/")
        reset_url = f"{base_url}/redefinir-senha/{token}"
        message = EmailMessage()
        message["Subject"] = "Redefinição de senha - Cardápio Digital"
        message["From"] = formataddr(
            ("Cardápio Digital", getattr(settings, "MAIL_FROM", "") or mail_username)
        )
        message["To"] = user.email
        message.set_content(
            "Recebemos uma solicitação para redefinir a senha da sua conta.\n\n"
            f"Acesse o link para escolher uma nova senha (válido por 1 hora):\n{reset_url}\n\n"
            "Se você não solicitou esta alteração, ignore esta mensagem."
        )

        try:
            send_email(message, settings)
        except Exception:
            db.session.delete(reset_token)
            db.session.commit()
            raise

    def reset_password(self, token, new_password):
        if not MIN_PASSWORD_LENGTH <= len(new_password) <= MAX_PASSWORD_LENGTH:
            return False

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        reset_token = (
            db.session.query(PasswordResetToken)
            .filter_by(token_hash=token_hash)
            .with_for_update()
            .first()
        )
        if reset_token is None:
            return False

        now = datetime.now(timezone.utc)
        expires_at = reset_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now:
            db.session.delete(reset_token)
            db.session.commit()
            return False

        user = db.session.get(Usuario, reset_token.user_id)
        if user is None:
            db.session.delete(reset_token)
            db.session.commit()
            return False

        user.senha = password_hasher.hash(new_password)
        verification = db.session.get(EmailVerification, user.id)
        if verification is not None and verification.verified_at is None:
            verification.token_hash = None
            verification.expires_at = None
            verification.verified_at = now
        db.session.query(PasswordResetToken).filter_by(user_id=user.id).delete()
        db.session.commit()
        return True
