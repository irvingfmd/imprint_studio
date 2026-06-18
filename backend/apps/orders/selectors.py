"""
Selectores para la app orders.
Encapsulan las consultas a la base de datos.
"""

from django.db.models import QuerySet

from .models import Order, RequestFile


def get_order_by_id(order_id: str) -> Order | None:
    try:
        return Order.objects.select_related("customer", "shipping_address").get(id=order_id, is_deleted=False)
    except Order.DoesNotExist:
        return None


def get_orders_for_customer(customer_id: str) -> QuerySet:
    return Order.objects.filter(customer_id=customer_id, is_deleted=False).order_by("-created_at")


def get_all_orders(
    status: str | None = None,
    priority: str | None = None,
    customer_id: str | None = None,
    request_type: str | None = None,
    delivery_method: str | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
) -> QuerySet:
    qs = Order.objects.select_related("customer").filter(is_deleted=False)

    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if customer_id:
        qs = qs.filter(customer_id=customer_id)
    if request_type:
        qs = qs.filter(request_type=request_type)
    if delivery_method:
        qs = qs.filter(delivery_method=delivery_method)
    if created_from:
        qs = qs.filter(created_at__date__gte=created_from)
    if created_to:
        qs = qs.filter(created_at__date__lte=created_to)

    return qs.order_by("-created_at")


def get_files_for_order(order_id: str) -> QuerySet:
    return RequestFile.objects.filter(order_id=order_id).order_by("uploaded_at")
