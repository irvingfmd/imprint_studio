"""
Serializers para la app materials.
"""

from decimal import Decimal

from rest_framework import serializers

from .models import Material, MaterialType


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = [
            "id",
            "name",
            "material_type",
            "brand",
            "available_colors",
            "price_per_kg",
            "stock_grams",
            "min_stock_grams",
            "is_active",
            "created_at",
            "updated_at",
        ]


class PublicMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = [
            "id",
            "name",
            "material_type",
            "brand",
            "available_colors",
            "price_per_kg",
        ]


class CreateUpdateMaterialSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    material_type = serializers.ChoiceField(choices=MaterialType.choices)
    brand = serializers.CharField(max_length=100, required=False, default="", allow_blank=True)
    available_colors = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
    )
    price_per_kg = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    stock_grams = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0"), required=False, default=Decimal("0"))
    min_stock_grams = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0"), required=False, default=Decimal("500"))
    is_active = serializers.BooleanField(default=True)


class StockAdjustmentSerializer(serializers.Serializer):
    OPERATIONS = [("add", "Add"), ("deduct", "Deduct")]
    grams = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    operation = serializers.ChoiceField(choices=OPERATIONS)
