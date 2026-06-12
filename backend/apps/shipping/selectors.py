"""
Selectores para la app shipping.
"""
from django.db.models import QuerySet

from .models import Shipment, ShippingAddress


def get_address_by_id(address_id: str) -> ShippingAddress | None:
    try:
        return ShippingAddress.objects.get(id=address_id)
    except ShippingAddress.DoesNotExist:
        return None


def get_addresses_for_user(user_id) -> QuerySet:
    return ShippingAddress.objects.filter(user_id=user_id).order_by("-created_at")


def get_shipment_by_id(shipment_id: str) -> Shipment | None:
    try:
        return Shipment.objects.select_related("order").get(id=shipment_id)
    except Shipment.DoesNotExist:
        return None


def get_shipment_for_order(order_id: str) -> Shipment | None:
    try:
        return Shipment.objects.get(order_id=order_id)
    except Shipment.DoesNotExist:
        return None
