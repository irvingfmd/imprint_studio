"""
Modelos de la app materials.

Material: filamento o resina disponible para impresión 3D.
"""

import uuid

from django.db import models


class MaterialType(models.TextChoices):
    PLA = "PLA", "PLA"
    PETG = "PETG", "PETG"
    ABS = "ABS", "ABS"
    TPU = "TPU", "TPU"
    RESIN = "RESIN", "Resina"
    OTHER = "OTHER", "Otro"


class Material(models.Model):
    """
    Material de impresión 3D con inventario de stock.
    available_colors es un JSONField con lista de strings.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(max_length=100)
    material_type = models.CharField(
        max_length=20,
        choices=MaterialType.choices,
    )
    brand = models.CharField(max_length=100, blank=True, default="")
    available_colors = models.JSONField(default=list)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    stock_grams = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_grams = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "materials"
        ordering = ["material_type", "name"]
        indexes = [
            models.Index(fields=["material_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        label = f"{self.brand} {self.name}".strip() if self.brand else self.name
        return f"{label} ({self.material_type})"
