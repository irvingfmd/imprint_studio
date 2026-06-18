"""
Serializers para la app quotes.
"""

from decimal import Decimal

from rest_framework import serializers

from .models import Quote, QuoteSnapshot


class QuoteSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteSnapshot
        fields = [
            "material_cost_per_kg",
            "electricity_rate_kwh",
            "labor_cost_per_hour",
            "post_processing_cost_per_gram",
            "packaging_cost",
            "failure_percentage",
            "profit_margin_percentage",
            "urgent_multiplier",
            "express_multiplier",
            "full_payment_discount_percentage",
            "printer_name",
            "printer_power_watts",
            "created_at",
        ]


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = [
            "id",
            "order_id",
            "weight_grams",
            "print_time_hours",
            "material_cost",
            "energy_cost",
            "labor_cost",
            "post_processing_cost",
            "packaging_cost",
            "risk_cost",
            "shipping_cost",
            "subtotal",
            "profit_amount",
            "discount_amount",
            "total_price",
            "quote_status",
            "accepted_at",
            "rejected_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]


class CreateQuoteSerializer(serializers.Serializer):
    weight_grams = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    print_time_hours = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    shipping_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        default=Decimal("0.00"),
    )
    printer_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class AcceptQuoteSerializer(serializers.Serializer):
    PAYMENT_OPTIONS = [("DEPOSIT", "Deposit"), ("FULL_PAYMENT", "Full Payment")]
    payment_option = serializers.ChoiceField(choices=PAYMENT_OPTIONS)


class RejectQuoteSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, default="", allow_blank=True)


class CalculateSerializer(serializers.Serializer):
    weight_grams = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    print_time_hours = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    priority = serializers.ChoiceField(choices=[("NORMAL", "Normal"), ("URGENT", "Urgent"), ("EXPRESS", "Express")])
    shipping_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        default=Decimal("0.00"),
    )
    full_payment_selected = serializers.BooleanField(default=False)
    printer_id = serializers.UUIDField(required=False, allow_null=True, default=None)
