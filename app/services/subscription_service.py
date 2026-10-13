"""Criação e confirmação de assinaturas recorrentes."""

from datetime import datetime, timezone
from urllib.parse import urlsplit

import requests
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Empresa, PlatformSetting, Subscription, WebhookEvent
from app.services.asaas_service import AsaasService

PLANS = {
    "pro": {"label": "Pro", "monthly_price": 49.0},
    "premium": {"label": "Premium", "monthly_price": 99.0},
}

PAID_EVENTS = {"PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"}
UNPAID_EVENTS = {"PAYMENT_OVERDUE", "PAYMENT_REFUNDED", "PAYMENT_DELETED"}


class SubscriptionService:
    def __init__(self):
        self.asaas_service = AsaasService()
        from config import get_config

        self.settings = get_config()

    def get_active_provider(self):
        setting = PlatformSetting.query.get("payment_provider")
        return setting.value if setting else "asaas"

    def provider_is_configured(self, provider):
        if provider == "asaas":
            return bool(
                self.settings.ASAAS_API_KEY and self.settings.WEBHOOK_SECRET
            )
        if provider == "stripe":
            configured = bool(
                self.settings.STRIPE_SECRET_KEY
                and self.settings.STRIPE_WEBHOOK_SECRET
            )
            base_url = urlsplit(self.settings.PUBLIC_BASE_URL)
            return configured and (
                base_url.scheme == "https" or getattr(self.settings, "DEBUG", False)
            )
        return False

    def set_active_provider(self, provider):
        if provider not in {"asaas", "stripe"}:
            return {"success": False, "message": "Provedor inválido"}
        if not self.provider_is_configured(provider):
            return {
                "success": False,
                "message": "Configure as chaves de API e webhook desse provedor no servidor.",
            }
        setting = PlatformSetting.query.get("payment_provider")
        if setting:
            setting.value = provider
        else:
            db.session.add(
                PlatformSetting(key="payment_provider", value=provider)
            )
        db.session.commit()
        return {"success": True}

    def get_pending_link(self, empresa_id, plan, provider):
        pending = Subscription.query.filter_by(
            empresa_id=empresa_id,
            status="pending",
            plano=plan,
            provider=provider,
        ).first()
        return pending.payment_url if pending else None

    def create_provider_payment_link(
        self, company_id, company_name, plan, provider, email
    ):
        if plan not in PLANS:
            return {"success": False, "message": "Plano inválido"}

        if provider == "asaas":
            result = self.asaas_service.create_recurring_payment_link(
                name=f"{company_name} - Plano {PLANS[plan]['label']}",
                description=f"Assinatura mensal do plano {PLANS[plan]['label']}",
                value=PLANS[plan]["monthly_price"],
            )
            if not result["success"]:
                return result
            checkout = result["data"]
            checkout_id = checkout.get("id")
            payment_url = checkout.get("url")
        elif provider == "stripe":
            if not self.settings.STRIPE_SECRET_KEY:
                return {"success": False, "message": "Stripe não está configurado."}
            base_url = self.settings.PUBLIC_BASE_URL.rstrip("/")
            stripe_payload = {
                "mode": "subscription",
                "success_url": f"{base_url}/empresa/home?checkout=pendente",
                "cancel_url": f"{base_url}/empresa/subscribe/{company_id}",
                "customer_email": email,
                "client_reference_id": str(company_id),
                "metadata[empresa_id]": str(company_id),
                "metadata[plan]": plan,
                "line_items[0][price_data][currency]": "brl",
                "line_items[0][price_data][unit_amount]": str(
                    round(PLANS[plan]["monthly_price"] * 100)
                ),
                "line_items[0][price_data][recurring][interval]": "month",
                "line_items[0][price_data][product_data][name]": (
                    f"Cardápio Digital - Plano {PLANS[plan]['label']}"
                ),
                "line_items[0][quantity]": "1",
            }
            try:
                response = requests.post(
                    "https://api.stripe.com/v1/checkout/sessions",
                    data=stripe_payload,
                    auth=(self.settings.STRIPE_SECRET_KEY, ""),
                    timeout=15,
                )
                response.raise_for_status()
                checkout = response.json()
                if not isinstance(checkout, dict):
                    return {
                        "success": False,
                        "message": "Resposta inválida recebida do Stripe.",
                    }
            except (requests.exceptions.RequestException, ValueError):
                return {
                    "success": False,
                    "message": "Não foi possível criar o checkout no Stripe.",
                }
            checkout_id = checkout.get("id")
            payment_url = checkout.get("url")
        else:
            return {"success": False, "message": "Provedor de pagamento inválido"}

        parsed_url = urlsplit(payment_url or "")
        if (
            not checkout_id
            or parsed_url.scheme != "https"
            or not parsed_url.hostname
            or not self._is_provider_checkout_host(provider, parsed_url.hostname)
        ):
            return {
                "success": False,
                "message": "O provedor não retornou um link de checkout válido.",
            }

        return {"success": True, "id": checkout_id, "url": payment_url}

    @staticmethod
    def _is_provider_checkout_host(provider, hostname):
        if provider == "asaas":
            return hostname == "asaas.com" or hostname.endswith(".asaas.com")
        if provider == "stripe":
            return hostname == "checkout.stripe.com"
        return False

    def save_pending_link(self, empresa_id, plan, provider, link_id, payment_url):
        try:
            db.session.add(
                Subscription(
                    empresa_id=empresa_id,
                    provider=provider,
                    plano=plan,
                    status="pending",
                    payment_link_id=link_id,
                    payment_url=payment_url,
                    updated_at=datetime.now(timezone.utc),
                )
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return {"success": True, "url": payment_url}

    def process_asaas_webhook(self, payload):
        data = payload.get("payment") or payload.get("subscription") or {}
        provider_subscription_id = data.get("subscription")
        if isinstance(provider_subscription_id, dict):
            provider_subscription_id = provider_subscription_id.get("id")
        if payload.get("event") in {"SUBSCRIPTION_DELETED", "SUBSCRIPTION_INACTIVATED"}:
            provider_subscription_id = data.get("id")
        return self._apply_webhook_event(
            provider="asaas",
            event_id=payload.get("id"),
            event_type=payload.get("event"),
            checkout_id=data.get("paymentLink"),
            provider_subscription_id=provider_subscription_id,
        )

    def process_stripe_webhook(self, payload):
        data = payload.get("data")
        event_object = data.get("object") if isinstance(data, dict) else None
        if not isinstance(event_object, dict):
            return {"success": False, "message": "Evento Stripe inválido"}

        event_type = payload.get("type")
        checkout_id = None
        provider_subscription_id = None
        if event_type in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
            if event_object.get("payment_status") != "paid":
                return {"success": True, "processed": False}
            checkout_id = event_object.get("id")
            provider_subscription_id = event_object.get("subscription")
        elif event_type in {
            "invoice.paid",
            "invoice.payment_failed",
            "checkout.session.expired",
        }:
            if event_type == "checkout.session.expired":
                checkout_id = event_object.get("id")
            else:
                provider_subscription_id = event_object.get("subscription")
        elif event_type == "customer.subscription.deleted":
            provider_subscription_id = event_object.get("id")
        else:
            return {"success": True, "processed": False}

        if isinstance(provider_subscription_id, dict):
            provider_subscription_id = provider_subscription_id.get("id")
        return self._apply_webhook_event(
            provider="stripe",
            event_id=payload.get("id"),
            event_type=event_type,
            checkout_id=checkout_id,
            provider_subscription_id=provider_subscription_id,
        )

    def _apply_webhook_event(
        self, provider, event_id, event_type, checkout_id, provider_subscription_id
    ):
        if not isinstance(event_id, str) or not event_id:
            return {"success": False, "message": "Evento sem identificador"}
        known_paid = event_type in PAID_EVENTS or event_type in {
            "checkout.session.completed",
            "checkout.session.async_payment_succeeded",
            "invoice.paid",
        }
        known_unpaid = event_type in UNPAID_EVENTS or event_type in {
            "invoice.payment_failed",
            "checkout.session.expired",
            "customer.subscription.deleted",
            "SUBSCRIPTION_DELETED",
            "SUBSCRIPTION_INACTIVATED",
        }
        if not known_paid and not known_unpaid:
            return {"success": True, "processed": False}

        filters = []
        if checkout_id:
            filters.append(Subscription.payment_link_id == checkout_id)
        if provider_subscription_id:
            filters.append(
                Subscription.provider_subscription_id == provider_subscription_id
            )
        if not filters:
            return {"success": True, "processed": False}

        subscription = Subscription.query.filter(
            Subscription.provider == provider, or_(*filters)
        ).first()
        if not subscription:
            return {"success": True, "processed": False}

        stored_event_id = f"{provider}:{event_id}"
        if WebhookEvent.query.get(stored_event_id):
            return {"success": True, "processed": False}

        company = Empresa.query.get(subscription.empresa_id)
        if not company:
            return {"success": False, "message": "Empresa da assinatura não encontrada"}

        if known_paid:
            subscription.status = "active"
            if provider_subscription_id:
                subscription.provider_subscription_id = provider_subscription_id
            company.plano = subscription.plano
        else:
            subscription.status = "inactive"
            company.plano = "gratis"

        subscription.updated_at = datetime.now(timezone.utc)
        db.session.add(
            WebhookEvent(
                event_id=stored_event_id, received_at=datetime.now(timezone.utc)
            )
        )
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"success": True, "processed": False}
        except Exception:
            db.session.rollback()
            raise

        return {"success": True, "processed": True}
