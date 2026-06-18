"""
Selectores para la app quotes.
"""

from django.db.models import QuerySet

from .models import Quote, QuoteStatus


def get_quote_by_id(quote_id: str) -> Quote | None:
    try:
        return Quote.objects.select_related("order__customer", "snapshot").get(id=quote_id, is_deleted=False)
    except Quote.DoesNotExist:
        return None


def get_quotes_for_order(order_id: str) -> QuerySet:
    return Quote.objects.filter(order_id=order_id, is_deleted=False).order_by("-created_at")


def get_active_quote_for_order(order_id: str) -> Quote | None:
    """Retorna la cotización PENDING activa de un pedido, si existe."""
    return Quote.objects.filter(
        order_id=order_id,
        quote_status=QuoteStatus.PENDING,
        is_deleted=False,
    ).first()
