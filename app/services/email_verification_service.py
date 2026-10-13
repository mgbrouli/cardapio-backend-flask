"""Confirmação de endereço de e-mail por token temporário."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr

from app.database import db
from app.models import EmailVerification, Usuario
from app.services.email_service import send_email

TOKEN_LIFETIME = timedelta(hours=24)
REQUEST_COOLDOWN = timedelta(minutes=1)


class EmailVerificationService:
    def is_verified(self, user_id):
        verification = db.session.get(EmailVerification, user_id)
        return verification is None or verification.verified_at is not None

    def issue_token(self, user, settings, force=False):
        if not getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False):
            return
        if not getattr(settings, "MAIL_SERVER", ""):
            raise RuntimeError("SMTP de envio de e-mail não está configurado")

        now = datetime.now(timezone.utc)
        verification = db.session.get(EmailVerification, user.id)
        if verification is not None and verification.verified_at is not None:
            return
        if verification is not None and not force:
            requested_at = verification.requested_at
            if requested_at.tzinfo is None:
                requested_at = requested_at.replace(tzinfo=timezone.utc)
            if now - requested_at < REQUEST_COOLDOWN:
                return

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        if verification is None:
            verification = EmailVerification(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=now + TOKEN_LIFETIME,
                requested_at=now,
            )
            db.session.add(verification)
        else:
            verification.token_hash = token_hash
            verification.expires_at = now + TOKEN_LIFETIME
            verification.requested_at = now
        db.session.commit()

        base_url = getattr(settings, "PUBLIC_BASE_URL", "").rstrip("/")
        verification_url = f"{base_url}/verificar-email/{token}"
        message = EmailMessage()
        message["Subject"] = "Confirme seu e-mail - Cardápio Digital"
        sender = getattr(settings, "MAIL_FROM", "") or settings.MAIL_USERNAME
        message["From"] = formataddr(("Cardápio Digital", sender))
        message["To"] = user.email
        message.set_content(
            "Confirme o endereço de e-mail da sua conta do Cardápio Digital "
            "usando o link abaixo. Ele expira em 24 horas:\n\n"
            f"{verification_url}\n\n"
            "Se você não criou esta conta, ignore esta mensagem."
        )
        try:
            send_email(message, settings)
        except Exception:
            verification.token_hash = None
            verification.expires_at = None
            db.session.commit()
            raise

    def verify_token(self, token):
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        verification = (
            db.session.query(EmailVerification)
            .filter_by(token_hash=token_hash)
            .with_for_update()
            .first()
        )
        if verification is None:
            return False

        now = datetime.now(timezone.utc)
        expires_at = verification.expires_at
        if expires_at is None:
            return False
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now or db.session.get(Usuario, verification.user_id) is None:
            verification.token_hash = None
            verification.expires_at = None
            db.session.commit()
            return False

        verification.token_hash = None
        verification.expires_at = None
        verification.verified_at = now
        db.session.commit()
        return True
