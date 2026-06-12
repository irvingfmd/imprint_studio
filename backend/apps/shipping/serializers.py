"""
Serializers para la app shipping.
"""
from decimal import Decimal

from rest_framework import serializers

from .models import Shipment, ShippingAddress


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "id", "address_name", "street", "external_number", "internal_number",
            "neighborhood", "postal_code", "city", "state", "country",
            "references", "is_default", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ShippingAddressCreateSerializer(serializers.Serializer):
    address_name = serializers.CharField(max_length=100)
    street = serializers.CharField(max_length=255)
    external_number = serializers.CharField(max_length=50)
    internal_number = serializers.CharField(max_length=50, required=False, default="")
    neighborhood = serializers.CharField(max_length=255)
    postal_code = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100, required=False, default="Mexico")
    references = serializers.CharField(required=False, default="")
    is_default = serializers.BooleanField(required=False, default=False)


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            "id", "order_id", "carrier_name", "tracking_number",
            "shipping_cost", "shipped_at", "delivered_at",
            "shipping_notes", "created_at", "updated_at",
        ]


class CreateShipmentSerializer(serializers.Serializer):
    carrier_name = serializers.CharField(max_length=100, required=False, default="")
    tracking_number = serializers.CharField(max_length=100, required=False, default="")
    shipping_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        min_value=Decimal("0.00"),
        default=Decimal("0.00"),
    )
    shipping_notes = serializers.CharField(required=False, default="")
