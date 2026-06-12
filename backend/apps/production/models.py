"""
Modelos de la app production.

ProductionHistory: historial inmutable de cambios de estado de un pedido.
"""
import uuid

from django.db import models

from apps.authentication.models import User
from apps.orders.models import Order, OrderStatus


class ProductionHistory(models.Model):
    """
    Registro de un cambio de estado en un pedido.
    Funciona como bitácora oficial del flujo de producción.
    Inmutable por diseño: nunca se modifica ni elimina.
    No tiene updated_at por diseño.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.RESTRICT,
        related_name="production_history",
    )

    # Null en el primer cambio de estado (cuando el pedido se crea)
    previous_status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        null=True,
        blank=True,
    )

    new_status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="production_history_changes",
    )

    notes = models.TextField(blank=True, default="")

    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "production_history"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["changed_at"]),
            models.Index(fields=["new_status"]),
            models.Index(fields=["order", "changed_at"]),
        ]

    def __str__(self) -> str:
        prev = self.previous_status or "—"
        return f"{prev} → {self.new_status} ({self.order_id})"
