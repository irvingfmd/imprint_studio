"""
Modelos de la app payments.

Payment: registro de movimiento financiero asociado a un pedido.
Los pagos nunca se eliminan físicamente ni se modifican una vez confirmados.
"""

import uuid

from django.db import models

from apps.authentication.models import User
from apps.orders.models import Order


class PaymentType(models.TextChoices):
    DEPOSIT = "DEPOSIT", "Deposit"
    BALANCE = "BALANCE", "Balance"
    FULL_PAYMENT = "FULL_PAYMENT", "Full Payment"
    REFUND = "REFUND", "Refund"


class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    CASH = "CASH", "Cash"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    REJECTED = "REJECTED", "Rejected"


class Payment(models.Model):
    """
    Movimiento financiero asociado a un pedido.
    Incluye anticipos, pagos finales, pagos completos y reembolsos.
    Sin updated_at por diseño: los pagos son registros inmutables.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.RESTRICT,
        related_name="payments",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_type = models.CharField(
        max_length=30,
        choices=PaymentType.choices,
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    # URL del comprobante en Cloudinary o Supabase Storage
    proof_file_url = models.TextField(blank=True, default="")

    # Confirmación sin comprobante digital (ej. el cliente envió por WhatsApp)
    manual_confirmation = models.BooleanField(default=False)

    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_payments",
    )

    confirmed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True, default="")

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["payment_type"]),
            models.Index(fields=["payment_method"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["confirmed_at"]),
            models.Index(fields=["order", "payment_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.payment_type} — {self.payment_status} — ${self.amount}"
