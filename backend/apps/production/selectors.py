"""
Selectores para la app production.
Encapsulan las consultas a la base de datos.
"""
from django.db.models import QuerySet

from apps.orders.models import OrderEvent

from .models import ProductionHistory


def get_production_history_for_order(order_id: str) -> QuerySet:
    """Retorna el historial de producción de un pedido en orden cronológico."""
    return (
        ProductionHistory.objects.filter(order_id=order_id)
        .select_related("changed_by")
        .order_by("changed_at")
    )


def get_events_for_order(order_id: str) -> QuerySet:
    """Retorna todos los eventos de un pedido en orden cronológico."""
    return (
        OrderEvent.objects.filter(order_id=order_id)
        .select_related("created_by")
        .order_by("created_at")
    )


def get_event_by_id(event_id: str, order_id: str) -> OrderEvent | None:
    """Retorna un evento específico de un pedido, o None si no existe."""
    return (
        OrderEvent.objects.filter(id=event_id, order_id=order_id)
        .select_related("created_by")
        .first()
    )
