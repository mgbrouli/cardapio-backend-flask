"""Envio SMTP de mensagens transacionais."""

import smtplib
import ssl


def is_configured(settings):
    return all(
        (
            getattr(settings, "MAIL_SERVER", ""),
            getattr(settings, "MAIL_USERNAME", ""),
            getattr(settings, "MAIL_PASSWORD", ""),
        )
    )


def send_email(message, settings):
    if not is_configured(settings):
        raise RuntimeError("SMTP de envio de e-mail não está configurado")
    host = settings.MAIL_SERVER
    port = settings.MAIL_PORT
    username = settings.MAIL_USERNAME
    password = settings.MAIL_PASSWORD
    context = ssl.create_default_context()
    if settings.MAIL_USE_SSL:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as server:
            server.login(username, password)
            server.send_message(message)
        return

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(username, password)
        server.send_message(message)
