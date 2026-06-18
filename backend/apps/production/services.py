"""
Servicios para la app production.

OrderStatusTransitionService: gestiona las transiciones de estado de pedidos.
Fuente oficial de transiciones: docs/appendices/status-flow.md
En caso de conflicto con otro documento, status-flow.md prevalece.
"""

from django.db import transaction
from django.utils import timezone

from apps.notifications.services import NotificationService
from apps.orders.models import (
    EventType,
    Order,
    OrderEvent,
    OrderPaymentStatus,
    OrderStatus,
)

from .models import ProductionHistory

# Matriz completa de transiciones válidas — fuente: docs/appendices/status-flow.md
VALID_TRANSITIONS: dict[str, list[str]] = {
    OrderStatus.RECEIVED: [OrderStatus.QUOTED, OrderStatus.CANCELLED],
    OrderStatus.PENDING_ANALYSIS: [OrderStatus.QUOTED, OrderStatus.CANCELLED],
    OrderStatus.QUOTED: [OrderStatus.APPROVED, OrderStatus.CANCELLED],
    OrderStatus.APPROVED: [OrderStatus.PENDING_DEPOSIT, OrderStatus.FULLY_PAID, OrderStatus.CANCELLED],
    OrderStatus.PENDING_DEPOSIT: [OrderStatus.DEPOSIT_PAID, OrderStatus.CANCELLED],
    OrderStatus.DEPOSIT_PAID: [OrderStatus.PRINTING],
    OrderStatus.PRINTING: [OrderStatus.POST_PROCESSING],
    OrderStatus.POST_PROCESSING: [OrderStatus.READY],
    OrderStatus.READY: [OrderStatus.PENDING_BALANCE, OrderStatus.FULLY_PAID, OrderStatus.DELIVERED],
    OrderStatus.PENDING_BALANCE: [OrderStatus.FULLY_PAID],
    OrderStatus.FULLY_PAID: [OrderStatus.PRINTING, OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}

# Estados desde los que se puede cancelar
CANCELLABLE_STATUSES: set[str] = {
    OrderStatus.RECEIVED,
    OrderStatus.PENDING_ANALYSIS,
    OrderStatus.QUOTED,
    OrderStatus.APPROVED,
    OrderStatus.PENDING_DEPOSIT,
}


class OrderStatusTransitionService:
    @staticmethod
    @transaction.atomic
    def transition(order: Order, new_status: str, changed_by, notes: str = "") -> Order:
        """
        Realiza una transición de estado válida.
        Valida la transición, actualiza el pedido, y genera registros de auditoría.
        """
        current_status = order.status
        allowed = VALID_TRANSITIONS.get(current_status, [])

        if new_status not in allowed:
            raise ValueError(f"Transición inválida: {current_status} → {new_status}.")

        # READY → DELIVERED solo si el pedido ya está completamente pagado
        if new_status == OrderStatus.DELIVERED:
            if order.payment_status != OrderPaymentStatus.FULLY_PAID:
                raise ValueError("No se puede marcar como DELIVERED: el pedido no está completamente pagado.")

        previous_status = order.status
        order.status = new_status
        now = timezone.now()

        update_fields = ["status", "updated_at"]

        if new_status == OrderStatus.APPROVED:
            order.approved_at = now
            update_fields.append("approved_at")
        elif new_status == OrderStatus.READY:
            order.ready_at = now
            update_fields.append("ready_at")
        elif new_status == OrderStatus.DELIVERED:
            order.delivered_at = now
            update_fields.append("delivered_at")

        order.save(update_fields=update_fields)

        ProductionHistory.objects.create(
            order=order,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            notes=notes,
        )

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.STATUS_CHANGED,
            event_description=f"Estado cambiado de {previous_status} a {new_status}.",
            metadata={
                "previous_status": previous_status,
                "new_status": new_status,
                "notes": notes,
            },
            created_by=changed_by,
        )

        _send_status_notification(order, new_status)

        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order, cancelled_by, reason: str) -> Order:
        """
        Cancela un pedido.
        Solo permitido desde: RECEIVED, PENDING_ANALYSIS, QUOTED, APPROVED, PENDING_DEPOSIT.
        Fuente oficial: docs/appendices/status-flow.md — sección Cancelaciones.
        """
        if order.status not in CANCELLABLE_STATUSES:
            raise ValueError(f"No se puede cancelar un pedido en estado {order.status}.")

        previous_status = order.status
        now = timezone.now()

        order.status = OrderStatus.CANCELLED
        order.cancelled_at = now
        order.cancellation_reason = reason
        order.save(update_fields=["status", "cancelled_at", "cancellation_reason", "updated_at"])

        ProductionHistory.objects.create(
            order=order,
            previous_status=previous_status,
            new_status=OrderStatus.CANCELLED,
            changed_by=cancelled_by,
            notes=reason,
        )

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.ORDER_CANCELLED,
            event_description=f"Pedido cancelado. Razón: {reason}",
            metadata={"previous_status": previous_status, "reason": reason},
            created_by=cancelled_by,
        )

        NotificationService.notify_order_cancelled(order)

        return order


def _send_status_notification(order: Order, new_status: str) -> None:
    """Envía notificación al cliente según el nuevo estado del pedido."""
    if new_status == OrderStatus.PRINTING:
        NotificationService.notify_order_in_production(order)
    elif new_status == OrderStatus.READY:
        from apps.orders.models import OrderPaymentStatus

        if order.payment_status == OrderPaymentStatus.DEPOSIT_PAID:
            NotificationService.notify_balance_pending(order)
        else:
            NotificationService.notify_order_ready(order)
    elif new_status == OrderStatus.DELIVERED:
        NotificationService.notify_order_delivered(order)
