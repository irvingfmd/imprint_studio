"""
Modelos de la app quotes.

Quote: cotización oficial generada por el administrador.
QuoteSnapshot: copia inmutable de la configuración usada al cotizar.
"""
import uuid

from django.db import models

from apps.authentication.models import User
from apps.configuration.models import Printer
from apps.orders.models import Order


class QuoteStatus(models.TextChoices):
    PENDING  = "PENDING",  "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    EXPIRED  = "EXPIRED",  "Expired"


class Quote(models.Model):
    """
    Cotización oficial para un pedido.
    Generada por el administrador con datos del laminado en Bambu Studio.
    Solo puede existir una cotización PENDING activa por pedido.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.RESTRICT,
        related_name="quotes",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="created_quotes",
    )

    printer = models.ForeignKey(
        Printer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )

    # Datos del laminado
    weight_grams = models.DecimalField(max_digits=10, decimal_places=2)
    print_time_hours = models.DecimalField(max_digits=10, decimal_places=2)

    # Desglose de costos
    material_cost = models.DecimalField(max_digits=10, decimal_places=2)
    energy_cost = models.DecimalField(max_digits=10, decimal_places=2)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    post_processing_cost = models.DecimalField(max_digits=10, decimal_places=2)
    packaging_cost = models.DecimalField(max_digits=10, decimal_places=2)
    risk_cost = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    profit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    quote_status = models.CharField(
        max_length=20,
        choices=QuoteStatus.choices,
        default=QuoteStatus.PENDING,
    )

    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotes"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["quote_status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["order", "quote_status"]),
        ]

    def __str__(self) -> str:
        return f"Quote {self.order} — {self.quote_status} — ${self.total_price}"


class QuoteSnapshot(models.Model):
    """
    Copia inmutable de la configuración de negocio usada al generar una cotización.
    Permite reconstruir el cálculo histórico aunque la configuración haya cambiado.
    No tiene updated_at por diseño: los snapshots nunca se modifican.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    quote = models.OneToOneField(
        Quote,
        on_delete=models.RESTRICT,
        related_name="snapshot",
    )

    # Copia de business_config al momento de cotizar
    material_cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    electricity_rate_kwh = models.DecimalField(max_digits=10, decimal_places=4, default="2.0000")
    labor_cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    post_processing_cost_per_gram = models.DecimalField(max_digits=10, decimal_places=2)
    packaging_cost = models.DecimalField(max_digits=10, decimal_places=2)
    failure_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    profit_margin_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    urgent_multiplier = models.DecimalField(max_digits=5, decimal_places=2)
    express_multiplier = models.DecimalField(max_digits=5, decimal_places=2)
    full_payment_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    # Copia de la impresora usada
    printer_name = models.CharField(max_length=255, blank=True, default="")
    printer_power_watts = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "quote_snapshots"

    def __str__(self) -> str:
        return f"Snapshot — Quote {self.quote_id}"