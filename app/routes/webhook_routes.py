"""Webhooks autenticados dos provedores de pagamento."""

import hashlib
import hmac
import json
import time

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.subscription_service import SubscriptionService

router = APIRouter()
subscription_service = SubscriptionService()


@router.post("/webhooks/asaas", name="webhooks.asaas")
async def asaas_webhook(request: Request):
    secret = getattr(request.app.state.settings, "WEBHOOK_SECRET", "")
    if not secret:
        return JSONResponse(
            {"detail": "Webhook não configurado"}, status_code=503
        )

    supplied = request.headers.get("asaas-access-token", "")
    if not hmac.compare_digest(supplied, secret):
        return JSONResponse({"detail": "Não autorizado"}, status_code=401)

    try:
        payload = await request.json()
    except ValueError:
        return JSONResponse({"detail": "JSON inválido"}, status_code=400)
    if not isinstance(payload, dict):
        return JSONResponse({"detail": "Payload inválido"}, status_code=400)

    result = subscription_service.process_asaas_webhook(payload)
    if not result["success"]:
        return JSONResponse({"detail": result["message"]}, status_code=400)
    return JSONResponse({"received": True, "processed": result["processed"]})


@router.post("/webhooks/stripe", name="webhooks.stripe")
async def stripe_webhook(request: Request):
    secret = getattr(request.app.state.settings, "STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        return JSONResponse(
            {"detail": "Webhook não configurado"}, status_code=503
        )

    body = await request.body()
    signature_header = request.headers.get("stripe-signature", "")
    signature_parts = [
        part.strip().split("=", 1)
        for part in signature_header.split(",")
        if "=" in part
    ]
    timestamps = [value for key, value in signature_parts if key == "t"]
    signatures = [value for key, value in signature_parts if key == "v1"]
    if not timestamps or not signatures:
        return JSONResponse({"detail": "Assinatura Stripe inválida"}, status_code=401)

    timestamp = timestamps[0]
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return JSONResponse({"detail": "Assinatura expirada"}, status_code=401)
    except ValueError:
        return JSONResponse({"detail": "Assinatura Stripe inválida"}, status_code=401)

    signed_payload = timestamp.encode() + b"." + body
    expected_signature = hmac.new(
        secret.encode(), signed_payload, hashlib.sha256
    ).hexdigest()
    if not any(
        hmac.compare_digest(expected_signature, signature)
        for signature in signatures
    ):
        return JSONResponse({"detail": "Assinatura Stripe inválida"}, status_code=401)

    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JSONResponse({"detail": "JSON inválido"}, status_code=400)
    if not isinstance(payload, dict):
        return JSONResponse({"detail": "Payload inválido"}, status_code=400)

    result = subscription_service.process_stripe_webhook(payload)
    if not result["success"]:
        return JSONResponse({"detail": result["message"]}, status_code=400)
    return JSONResponse({"received": True, "processed": result["processed"]})
