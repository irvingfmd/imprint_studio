"""
Modelos de la app shipping.

ShippingAddress: direcciones de envío de clientes.
Shipment: registros de envíos a domicilio.
"""
import uuid

from django.db import models

from apps.authentication.models import User


class ShippingAddress(models.Model):
    """
    Dirección de envío registrada por un cliente.
    Un cliente puede tener múltiples direcciones.
    Solo una puede ser la predeterminada.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="shipping_addresses",
    )

    address_name = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    external_number = models.CharField(max_length=50)
    internal_number = models.CharField(max_length=50, blank=True, default="")
    neighborhood = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Mexico")
    references = models.TextField(blank=True, default="")
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipping_addresses"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["postal_code"]),
            models.Index(fields=["city"]),
            models.Index(fields=["state"]),
        ]

    def __str__(self) -> str:
        return f"{self.address_name} — {self.city}, {self.state}"


class Shipment(models.Model):
    """
    Información de envío a domicilio de un pedido.
    Solo aplica cuando delivery_method = SHIPPING.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.RESTRICT,
        related_name="shipment",
    )

    carrier_name = models.CharField(max_length=100, blank=True, default="")
    tracking_number = models.CharField(max_length=100, blank=True, default="")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    shipping_notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipments"
        indexes = [
            models.Index(fields=["tracking_number"]),
            models.Index(fields=["shipped_at"]),
        ]

    def __str__(self) -> str:
        return f"Shipment — {self.order}"