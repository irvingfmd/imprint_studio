"""
Servicios para la app materials.
"""

from decimal import Decimal

from django.db import transaction

from .models import Material


class MaterialService:
    @staticmethod
    @transaction.atomic
    def create_material(data: dict) -> Material:
        return Material.objects.create(
            name=data["name"],
            material_type=data["material_type"],
            brand=data.get("brand", ""),
            available_colors=data.get("available_colors", []),
            price_per_kg=data["price_per_kg"],
            stock_grams=data.get("stock_grams", Decimal("0")),
            min_stock_grams=data.get("min_stock_grams", Decimal("500")),
            is_active=data.get("is_active", True),
        )

    @staticmethod
    @transaction.atomic
    def update_material(material: Material, data: dict) -> Material:
        for field in ("name", "material_type", "brand", "available_colors", "price_per_kg", "stock_grams", "min_stock_grams", "is_active"):
            if field in data:
                setattr(material, field, data[field])
        material.save()
        return material

    @staticmethod
    @transaction.atomic
    def deduct_stock(material: Material, grams: Decimal) -> Material:
        if material.stock_grams < grams:
            raise ValueError(
                f"Stock insuficiente. Disponible: {material.stock_grams}g, solicitado: {grams}g."
            )
        material.stock_grams -= grams
        material.save(update_fields=["stock_grams", "updated_at"])
        return material

    @staticmethod
    @transaction.atomic
    def add_stock(material: Material, grams: Decimal) -> Material:
        material.stock_grams += grams
        material.save(update_fields=["stock_grams", "updated_at"])
        return material
