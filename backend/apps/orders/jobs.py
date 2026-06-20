"""
Jobs del scheduler para la app orders.
"""

import logging
from datetime import timedelta

from django.db.models import OuterRef, Subquery
from django.utils import timezone

logger = logging.getLogger(__name__)


def expire_pending_quotes() -> None:
    """
    Expira cotizaciones PENDING que superaron su expires_at.
    Corre diariamente.
    """
    from apps.orders.models import EventType, OrderEvent
    from apps.quotes.models import Quote, QuoteStatus

    expired_qs = Quote.objects.filter(
        quote_status=QuoteStatus.PENDING,
        expires_at__lt=timezone.now(),
        is_deleted=False,
    )

    count = 0
    for quote in expired_qs:
        try:
            quote.quote_status = QuoteStatus.EXPIRED
            quote.save(update_fields=["quote_status", "updated_at"])
            OrderEvent.objects.create(
                order=quote.order,
                event_type=EventType.STATUS_CHANGED,
                event_description=f"Cotización {quote.id} expirada automáticamente.",
                metadata={"quote_id": str(quote.id)},
                created_by=None,
            )
            count += 1
        except Exception as exc:
            logger.error("Error al expirar cotización %s: %s", quote.id, exc)

    if count:
        logger.info("Scheduler: %d cotización(es) expirada(s) automáticamente.", count)


def cancel_expired_deposits() -> None:
    """
    Cancela pedidos en PENDING_DEPOSIT que superaron deposit_deadline_hours.
    Fuente: docs/appendices/status-flow.md — Cancelación Automática por Vencimiento de Anticipo.
    """
    from apps.configuration.selectors import get_active_business_config
    from apps.orders.models import Order, OrderStatus
    from apps.production.models import ProductionHistory
    from apps.production.services import OrderStatusTransitionService

    config = get_active_business_config()
    if not config:
        logger.warning("cancel_expired_deposits: sin BusinessConfig activa, abortando.")
        return

    hours = int(config.deposit_deadline_hours)
    deadline = timezone.now() - timedelta(hours=hours)

    # Fecha en que cada pedido entró a PENDING_DEPOSIT (registro más reciente)
    pending_since_sq = (
        ProductionHistory.objects.filter(
            order=OuterRef("pk"),
            new_status=OrderStatus.PENDING_DEPOSIT,
        )
        .order_by("-changed_at")
        .values("changed_at")[:1]
    )

    expired = (
        Order.objects.filter(status=OrderStatus.PENDING_DEPOSIT, is_deleted=False)
        .annotate(pending_since=Subquery(pending_since_sq))
        .filter(pending_since__lt=deadline)
    )

    cancelled = 0
    for order in expired:
        try:
            OrderStatusTransitionService.cancel_order(
                order=order,
                cancelled_by=None,
                reason=f"Cancelación automática: anticipo no recibido en {hours} h.",
            )
            cancelled += 1
            logger.info("Pedido %s cancelado por vencimiento de anticipo.", order.id)
        except Exception as exc:
            logger.error("Error al cancelar pedido %s automáticamente: %s", order.id, exc)

    if cancelled:
        logger.info("Scheduler: %d pedido(s) cancelado(s) por vencimiento de anticipo.", cancelled)


def remind_pending_deposits() -> None:
    """
    Envía recordatorio a clientes con anticipo pendiente a 24h de vencerse.
    Solo notifica una vez por pedido (verifica que no se haya enviado antes).
    """
    from apps.configuration.selectors import get_active_business_config
    from apps.notifications.services import NotificationService
    from apps.orders.models import EventType, Order, OrderEvent, OrderStatus
    from apps.production.models import ProductionHistory

    config = get_active_business_config()
    if not config:
        return

    hours = int(config.deposit_deadline_hours)
    reminder_hours = 24
    if hours <= reminder_hours:
        return

    threshold = timezone.now() - timedelta(hours=hours - reminder_hours)

    pending_since_sq = (
        ProductionHistory.objects.filter(
            order=OuterRef("pk"),
            new_status=OrderStatus.PENDING_DEPOSIT,
        )
        .order_by("-changed_at")
        .values("changed_at")[:1]
    )

    due_soon = (
        Order.objects.filter(status=OrderStatus.PENDING_DEPOSIT, is_deleted=False)
        .annotate(pending_since=Subquery(pending_since_sq))
        .filter(pending_since__lt=threshold)
    )

    sent = 0
    for order in due_soon:
        already_reminded = OrderEvent.objects.filter(
            order=order,
            event_type=EventType.DEPOSIT_REMINDER,
        ).exists()
        if already_reminded:
            continue

        try:
            NotificationService.notify_deposit_reminder(order, reminder_hours)
            OrderEvent.objects.create(
                order=order,
                event_type=EventType.DEPOSIT_REMINDER,
                event_description="Recordatorio de anticipo enviado automáticamente.",
                metadata={"hours_remaining": reminder_hours},
                created_by=None,
            )
            sent += 1
        except Exception as exc:
            logger.error("Error al enviar recordatorio para pedido %s: %s", order.id, exc)

    if sent:
        logger.info("Scheduler: %d recordatorio(s) de anticipo enviado(s).", sent)
