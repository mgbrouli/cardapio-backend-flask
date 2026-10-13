"""Limitação persistente de tentativas de autenticação."""

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.database import db
from app.models import AuthRateLimit

WINDOW = timedelta(minutes=15)
LOCKOUT = timedelta(minutes=15)
MAX_FAILURES = 5


class LoginRateLimitService:
    @staticmethod
    def _keys(email, remote_ip, secret_key):
        identifiers = (
            f"email:{email.strip().casefold()[:254]}",
            f"ip:{remote_ip or 'unknown'}",
        )
        return [
            hmac.new(
                secret_key.encode("utf-8"),
                identifier.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            for identifier in identifiers
        ]

    def is_limited(self, email, remote_ip, secret_key):
        now = datetime.now(timezone.utc)
        keys = self._keys(email, remote_ip, secret_key)
        records = (
            db.session.query(AuthRateLimit)
            .filter(AuthRateLimit.key_hash.in_(keys))
            .all()
        )
        limited = False
        for record in records:
            blocked_until = record.blocked_until
            if blocked_until is None:
                continue
            if blocked_until.tzinfo is None:
                blocked_until = blocked_until.replace(tzinfo=timezone.utc)
            if blocked_until > now:
                limited = True
        if limited:
            return True

        stale_before = now - WINDOW
        db.session.execute(
            delete(AuthRateLimit)
            .where(AuthRateLimit.window_started_at < stale_before)
            .execution_options(synchronize_session=False)
        )
        db.session.commit()
        return False

    def record_failure(self, email, remote_ip, secret_key):
        now = datetime.now(timezone.utc)
        for key_hash in self._keys(email, remote_ip, secret_key):
            record = db.session.get(AuthRateLimit, key_hash)
            if record is None:
                record = AuthRateLimit(
                    key_hash=key_hash,
                    window_started_at=now,
                    attempt_count=0,
                )
                db.session.add(record)
            else:
                window_started_at = record.window_started_at
                if window_started_at.tzinfo is None:
                    window_started_at = window_started_at.replace(tzinfo=timezone.utc)
                if now - window_started_at >= WINDOW:
                    record.window_started_at = now
                    record.attempt_count = 0
                    record.blocked_until = None
            record.attempt_count += 1
            if record.attempt_count >= MAX_FAILURES:
                record.blocked_until = now + LOCKOUT
        db.session.commit()

    def clear(self, email, remote_ip, secret_key):
        db.session.execute(
            delete(AuthRateLimit).where(
                AuthRateLimit.key_hash.in_(
                    self._keys(email, remote_ip, secret_key)
                )
            ).execution_options(synchronize_session=False)
        )
        db.session.commit()
