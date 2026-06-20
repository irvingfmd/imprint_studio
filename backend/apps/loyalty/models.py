"""
Modelos de la app loyalty.

DiscountCode: códigos de descuento configurables.
DiscountRedemption: registro de uso de un código por un cliente.
"""

import uuid

from django.db import models

from apps.authentication.models import User
from apps.orders.models import Order


class DiscountType(models.TextChoices):
    PERCENTAGE = "PERCENTAGE", "Percentage"
    FIXED_AMOUNT = "FIXED_AMOUNT", "Fixed Amount"


class DiscountCode(models.Model):
    """Código de descuento con reglas de uso."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    current_uses = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "discount_codes"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.code} — {self.discount_type} {self.discount_value}"


class DiscountRedemption(models.Model):
    """Registro de uso de un código de descuento."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    discount_code = models.ForeignKey(
        DiscountCode, on_delete=models.RESTRICT, related_name="redemptions"
    )
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, related_name="discount_redemptions")
    customer = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="discount_redemptions")
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)

    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "discount_redemptions"
        ordering = ["-redeemed_at"]

    def __str__(self) -> str:
        return f"{self.discount_code.code} → Order {self.order_id} (${self.discount_applied})"
