"""
Servicios para la app payments.
Toda la lógica de negocio de pagos vive aquí.
"""

from django.db import transaction
from django.utils import timezone

from apps.notifications.services import NotificationService
from apps.orders.models import EventType, Order, OrderEvent, OrderPaymentStatus

from . import selectors
from .models import Payment, PaymentMethod, PaymentStatus, PaymentType


class PaymentService:
    @staticmethod
    @transaction.atomic
    def upload_proof(payment_id: str, file_url: str, user) -> Payment:
        """Asocia un comprobante de pago a un pago pendiente."""
        payment = selectors.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Pago no encontrado.")
        if payment.payment_status != PaymentStatus.PENDING:
            raise ValueError("Solo se puede subir comprobante a pagos en estado PENDING.")

        payment.proof_file_url = file_url
        payment.save(update_fields=["proof_file_url"])

        OrderEvent.objects.create(
            order=payment.order,
            event_type=EventType.PAYMENT_PROOF_UPLOADED,
            event_description=f"Comprobante subido para pago {payment.id}.",
            metadata={"payment_id": str(payment.id)},
            created_by=user,
        )

        return payment

    @staticmethod
    @transaction.atomic
    def confirm_payment(payment_id: str, confirmed_by, notes: str = "") -> Payment:
        """
        Confirma un pago pendiente.
        Actualiza el estado financiero del pedido y genera el evento correspondiente.
        """
        payment = selectors.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Pago no encontrado.")
        if payment.payment_status != PaymentStatus.PENDING:
            raise ValueError("Solo se pueden confirmar pagos en estado PENDING.")

        payment.payment_status = PaymentStatus.CONFIRMED
        payment.confirmed_by = confirmed_by
        payment.confirmed_at = timezone.now()
        payment.notes = notes
        payment.save(update_fields=["payment_status", "confirmed_by", "confirmed_at", "notes"])

        order = payment.order
        event_type = _resolve_confirmation_event(payment.payment_type)
        new_payment_status = _resolve_order_payment_status(payment.payment_type)

        if new_payment_status:
            order.payment_status = new_payment_status
            order.save(update_fields=["payment_status", "updated_at"])

        OrderEvent.objects.create(
            order=order,
            event_type=event_type,
            event_description=f"Pago {payment.id} confirmado.",
            metadata={"payment_id": str(payment.id), "amount": str(payment.amount)},
            created_by=confirmed_by,
        )

        NotificationService.notify_payment_confirmed(order)

        return payment

    @staticmethod
    @transaction.atomic
    def reject_payment(payment_id: str, confirmed_by, reason: str) -> Payment:
        """Rechaza un pago pendiente."""
        payment = selectors.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Pago no encontrado.")
        if payment.payment_status != PaymentStatus.PENDING:
            raise ValueError("Solo se pueden rechazar pagos en estado PENDING.")

        payment.payment_status = PaymentStatus.REJECTED
        payment.confirmed_by = confirmed_by
        payment.confirmed_at = timezone.now()
        payment.notes = reason
        payment.save(update_fields=["payment_status", "confirmed_by", "confirmed_at", "notes"])

        OrderEvent.objects.create(
            order=payment.order,
            event_type=EventType.PAYMENT_REJECTED,
            event_description=f"Pago {payment.id} rechazado. Razón: {reason}",
            metadata={"payment_id": str(payment.id), "reason": reason},
            created_by=confirmed_by,
        )

        NotificationService.notify_payment_rejected(payment.order)

        return payment

    @staticmethod
    @transaction.atomic
    def create_manual_confirmation(
        order_id: str,
        payment_type: str,
        payment_method: str,
        amount,
        notes: str,
        confirmed_by,
    ) -> Payment:
        """
        Crea un pago confirmado manualmente por el administrador.
        Se usa cuando el cliente envió comprobante por WhatsApp u otro canal externo.
        """
        try:
            order = Order.objects.get(id=order_id, is_deleted=False)
        except Order.DoesNotExist:
            raise ValueError("Pedido no encontrado.")

        payment = Payment.objects.create(
            order=order,
            amount=amount,
            payment_type=payment_type,
            payment_method=payment_method,
            payment_status=PaymentStatus.CONFIRMED,
            manual_confirmation=True,
            confirmed_by=confirmed_by,
            confirmed_at=timezone.now(),
            notes=notes,
        )

        event_type = _resolve_confirmation_event(payment_type)
        new_payment_status = _resolve_order_payment_status(payment_type)

        if new_payment_status:
            order.payment_status = new_payment_status
            order.save(update_fields=["payment_status", "updated_at"])

        OrderEvent.objects.create(
            order=order,
            event_type=event_type,
            event_description="Pago manual registrado y confirmado por administrador.",
            metadata={"payment_id": str(payment.id), "amount": str(payment.amount)},
            created_by=confirmed_by,
        )

        NotificationService.notify_payment_confirmed(order)

        return payment

    @staticmethod
    @transaction.atomic
    def process_refund(order_id: str, amount, reason: str, confirmed_by) -> Payment:
        """
        Registra un reembolso para un pedido.
        El administrador realiza la transferencia fuera del sistema y la registra aquí.
        Valida que el monto no exceda lo pagado menos reembolsos previos.
        """
        from decimal import Decimal

        from django.db.models import Sum

        try:
            order = Order.objects.get(id=order_id, is_deleted=False)
        except Order.DoesNotExist:
            raise ValueError("Pedido no encontrado.")

        total_paid = (
            Payment.objects.filter(
                order=order,
                payment_status=PaymentStatus.CONFIRMED,
                is_deleted=False,
            )
            .exclude(payment_type=PaymentType.REFUND)
            .aggregate(total=Sum("amount"))["total"]
        ) or Decimal("0.00")

        total_refunded = (
            Payment.objects.filter(
                order=order,
                payment_type=PaymentType.REFUND,
                payment_status=PaymentStatus.CONFIRMED,
                is_deleted=False,
            ).aggregate(total=Sum("amount"))["total"]
        ) or Decimal("0.00")

        available = total_paid - total_refunded
        if amount > available:
            raise ValueError(f"Monto excede lo disponible para reembolso (${available} MXN).")

        payment = Payment.objects.create(
            order=order,
            amount=amount,
            payment_type=PaymentType.REFUND,
            payment_method=PaymentMethod.BANK_TRANSFER,
            payment_status=PaymentStatus.CONFIRMED,
            manual_confirmation=True,
            confirmed_by=confirmed_by,
            confirmed_at=timezone.now(),
            notes=reason,
        )

        order.payment_status = OrderPaymentStatus.REFUNDED
        order.save(update_fields=["payment_status", "updated_at"])

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.REFUND_PROCESSED,
            event_description=f"Reembolso de ${amount} procesado. Razón: {reason}",
            metadata={"payment_id": str(payment.id), "amount": str(amount), "reason": reason},
            created_by=confirmed_by,
        )

        NotificationService.notify_refund_processed(order, amount)

        return payment


def _resolve_confirmation_event(payment_type: str) -> str:
    """Retorna el tipo de evento correspondiente al tipo de pago confirmado."""
    mapping = {
        PaymentType.DEPOSIT: EventType.DEPOSIT_CONFIRMED,
        PaymentType.BALANCE: EventType.BALANCE_CONFIRMED,
        PaymentType.FULL_PAYMENT: EventType.FULL_PAYMENT_CONFIRMED,
    }
    return mapping.get(payment_type, EventType.PAYMENT_CONFIRMED)


def _resolve_order_payment_status(payment_type: str) -> str | None:
    """Retorna el nuevo payment_status del pedido según el tipo de pago."""
    mapping = {
        PaymentType.DEPOSIT: OrderPaymentStatus.DEPOSIT_PAID,
        PaymentType.BALANCE: OrderPaymentStatus.FULLY_PAID,
        PaymentType.FULL_PAYMENT: OrderPaymentStatus.FULLY_PAID,
    }
    return mapping.get(payment_type)
