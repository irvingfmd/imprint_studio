"""
Modelos de la app reviews.

Review: calificación y comentario de un cliente sobre un pedido entregado.
"""

import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.authentication.models import User
from apps.orders.models import Order


class Review(models.Model):
    """
    Reseña de un cliente sobre un pedido entregado.
    Un pedido solo puede tener una reseña (OneToOneField).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.RESTRICT,
        related_name="review",
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="reviews",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    comment = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"Review {self.order_id} — {self.rating}/5"
