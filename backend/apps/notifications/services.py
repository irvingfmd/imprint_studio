"""
Servicios de notificaciones para Imprint Studio.

WhatsAppService: mensajes vía WhatsApp Business Cloud API.
EmailService: correos vía Brevo REST API.
NotificationService: notificaciones de negocio de alto nivel.

En desarrollo (sin credenciales configuradas), ambos servicios registran
el mensaje en el log en lugar de enviarlo.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Envía mensajes de texto por WhatsApp Business Cloud API."""

    BASE_URL = "https://graph.facebook.com/v18.0"

    @classmethod
    def send_message(cls, to_phone: str, message: str) -> bool:
        """
        Envía un mensaje de texto a un número en formato E.164.
        Sin credenciales configuradas, registra en log (modo desarrollo).
        """
        token = getattr(settings, "WHATSAPP_ACCESS_TOKEN", "")
        phone_id = getattr(settings, "WHATSAPP_PHONE_ID", "")

        if not token or not phone_id:
            logger.info("[WhatsApp DEV] Para: %s | %s", to_phone, message)
            return True

        try:
            response = requests.post(
                f"{cls.BASE_URL}/{phone_id}/messages",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "messaging_product": "whatsapp",
                    "to": to_phone,
                    "type": "text",
                    "text": {"body": message},
                },
                timeout=10,
            )
            response.raise_for_status()
            logger.info("WhatsApp enviado a %s", to_phone)
            return True
        except Exception as exc:
            logger.error("Error enviando WhatsApp a %s: %s", to_phone, exc)
            return False


class EmailService:
    """Envía correos electrónicos vía Brevo REST API."""

    BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
    SENDER_NAME = "Imprint Studio"
    SENDER_EMAIL = "noreply@imprintstudio.com"

    @classmethod
    def send_email(cls, to_email: str, subject: str, body: str, to_name: str = "") -> bool:
        """
        Envía un correo electrónico.
        Sin API key configurada, registra en log (modo desarrollo).
        """
        api_key = getattr(settings, "BREVO_API_KEY", "")

        if not api_key:
            logger.info("[Email DEV] Para: %s | Asunto: %s | %s", to_email, subject, body)
            return True

        try:
            response = requests.post(
                cls.BREVO_API_URL,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "sender": {"name": cls.SENDER_NAME, "email": cls.SENDER_EMAIL},
                    "to": [{"email": to_email, "name": to_name or to_email}],
                    "subject": subject,
                    "textContent": body,
                },
                timeout=10,
            )
            response.raise_for_status()
            logger.info("Email enviado a %s", to_email)
            return True
        except Exception as exc:
            logger.error("Error enviando email a %s: %s", to_email, exc)
            return False


class NotificationService:
    """
    Notificaciones de negocio de alto nivel.
    Canal primario: WhatsApp (autenticación por teléfono).
    Canal secundario: email, solo si el cliente tiene uno registrado.
    Los errores de envío no propagan excepciones — se registran en log.
    """

    @classmethod
    def _notify_customer(cls, order, message: str, email_subject: str) -> None:
        """Envía la notificación por WhatsApp y opcionalmente por email."""
        customer = order.customer
        WhatsAppService.send_message(customer.phone, message)
        if customer.email:
            EmailService.send_email(
                to_email=customer.email,
                subject=email_subject,
                body=message,
                to_name=customer.first_name,
            )

    @classmethod
    def notify_quote_ready(cls, order) -> None:
        """Cotización generada y lista para que el cliente la revise."""
        msg = (
            f"Hola {order.customer.first_name}, tu cotización para «{order.title}» ya está lista. "
            "Ingresa a la plataforma para revisarla y aceptarla o rechazarla."
        )
        cls._notify_customer(order, msg, f"Tu cotización está lista — {order.title}")

    @classmethod
    def notify_payment_confirmed(cls, order) -> None:
        """Pago confirmado (anticipo, saldo o pago completo)."""
        msg = (
            f"Hola {order.customer.first_name}, tu pago para «{order.title}» fue confirmado. "
            "¡Estamos preparando tu pedido!"
        )
        cls._notify_customer(order, msg, f"Pago confirmado — {order.title}")

    @classmethod
    def notify_payment_rejected(cls, order) -> None:
        """Comprobante de pago rechazado por el administrador."""
        msg = (
            f"Hola {order.customer.first_name}, tu comprobante de pago para «{order.title}» "
            "no pudo verificarse. Por favor sube uno nuevo o contáctanos."
        )
        cls._notify_customer(order, msg, f"Comprobante rechazado — {order.title}")

    @classmethod
    def notify_order_ready(cls, order) -> None:
        """Pedido completamente liquidado y listo para entrega o recolección."""
        msg = (
            f"Hola {order.customer.first_name}, tu pedido «{order.title}» está listo. "
            "Puedes pasar a recogerlo o coordinar el envío con nosotros."
        )
        cls._notify_customer(order, msg, f"Tu pedido está listo — {order.title}")

    @classmethod
    def notify_balance_pending(cls, order) -> None:
        """Pedido listo pero con saldo pendiente por pagar."""
        msg = (
            f"Hola {order.customer.first_name}, tu pedido «{order.title}» está listo. "
            "Para coordinar la entrega realiza el pago del saldo restante."
        )
        cls._notify_customer(order, msg, f"Saldo pendiente — {order.title}")

    @classmethod
    def notify_order_cancelled(cls, order) -> None:
        """Pedido cancelado."""
        reason = order.cancellation_reason or "Sin especificar."
        msg = (
            f"Hola {order.customer.first_name}, tu pedido «{order.title}» fue cancelado. "
            f"Motivo: {reason} Si tienes dudas, contáctanos."
        )
        cls._notify_customer(order, msg, f"Pedido cancelado — {order.title}")

    @classmethod
    def notify_refund_processed(cls, order, amount) -> None:
        """Reembolso procesado y transferido fuera del sistema."""
        msg = (
            f"Hola {order.customer.first_name}, tu reembolso de ${amount} MXN "
            f"para «{order.title}» fue procesado. "
            "Recibirás el monto en los próximos días hábiles."
        )
        cls._notify_customer(order, msg, f"Reembolso procesado — {order.title}")

    @classmethod
    def notify_order_in_production(cls, order) -> None:
        """Pedido entró a impresión."""
        msg = (
            f"Hola {order.customer.first_name}, tu pedido «{order.title}» "
            "entró a producción. Te avisamos cuando esté listo."
        )
        cls._notify_customer(order, msg, f"En producción — {order.title}")

    @classmethod
    def notify_order_delivered(cls, order) -> None:
        """Pedido entregado al cliente."""
        msg = (
            f"Hola {order.customer.first_name}, tu pedido «{order.title}» "
            "fue entregado. ¡Gracias por tu preferencia!"
        )
        cls._notify_customer(order, msg, f"Pedido entregado — {order.title}")

    @classmethod
    def notify_deposit_reminder(cls, order, hours_remaining: int) -> None:
        """Recordatorio de anticipo pendiente antes del vencimiento."""
        msg = (
            f"Hola {order.customer.first_name}, tu anticipo para «{order.title}» "
            f"vence en {hours_remaining} horas. Realiza tu pago para que podamos "
            "iniciar la producción."
        )
        cls._notify_customer(order, msg, f"Recordatorio de anticipo — {order.title}")

    @classmethod
    def notify_admin_new_order(cls, order) -> None:
        """Notifica a los administradores que hay un nuevo pedido."""
        from apps.authentication.models import User, UserRole
        admins = User.objects.filter(role=UserRole.ADMIN, is_active=True)
        msg = (
            f"Nuevo pedido recibido: «{order.title}» "
            f"de {order.customer.first_name} ({order.customer.phone}). "
            f"Tipo: {order.request_type}."
        )
        for admin in admins:
            WhatsAppService.send_message(admin.phone, msg)
            if admin.email:
                EmailService.send_email(
                    to_email=admin.email,
                    subject=f"Nuevo pedido — {order.title}",
                    body=msg,
                    to_name=admin.first_name,
                )
