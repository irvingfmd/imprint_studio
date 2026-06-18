"""
Selectores para la app payments.
Encapsulan las consultas a la base de datos.
"""

from django.db.models import QuerySet

from .models import Payment, PaymentStatus


def get_payments_for_order(order_id: str) -> QuerySet:
    """Retorna todos los pagos no eliminados de un pedido."""
    return (
        Payment.objects.filter(order_id=order_id, is_deleted=False)
        .select_related("confirmed_by")
        .order_by("-created_at")
    )


def get_payment_by_id(payment_id: str) -> Payment | None:
    """Retorna un pago por su ID, o None si no existe o está eliminado."""
    return Payment.objects.filter(id=payment_id, is_deleted=False).select_related("order", "confirmed_by").first()


def get_pending_payments() -> QuerySet:
    """Retorna todos los pagos en estado PENDING."""
    return (
        Payment.objects.filter(payment_status=PaymentStatus.PENDING, is_deleted=False)
        .select_related("order", "confirmed_by")
        .order_by("-created_at")
    )


def get_all_payments(
    payment_type: str | None = None,
    payment_method: str | None = None,
    payment_status: str | None = None,
    order_id: str | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
) -> QuerySet:
    """Retorna pagos con filtros opcionales. Para uso administrativo."""
    qs = Payment.objects.filter(is_deleted=False).select_related("order", "confirmed_by")

    if payment_type:
        qs = qs.filter(payment_type=payment_type)
    if payment_method:
        qs = qs.filter(payment_method=payment_method)
    if payment_status:
        qs = qs.filter(payment_status=payment_status)
    if order_id:
        qs = qs.filter(order_id=order_id)
    if created_from:
        qs = qs.filter(created_at__gte=created_from)
    if created_to:
        qs = qs.filter(created_at__lte=created_to)

    return qs.order_by("-created_at")
