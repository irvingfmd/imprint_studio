"""
Serializers para la app configuration.
"""
from rest_framework import serializers

from .models import BusinessConfig, BusinessHours, Holiday, PaymentInstructions


class BusinessConfigSerializer(serializers.ModelSerializer):
    """Configuración financiera y operativa del negocio."""

    class Meta:
        model = BusinessConfig
        fields = [
            "material_cost_per_kg",
            "energy_cost_per_hour",
            "labor_cost_per_hour",
            "post_processing_cost_per_gram",
            "packaging_cost",
            "failure_percentage",
            "profit_margin_percentage",
            "urgent_multiplier",
            "express_multiplier",
            "full_payment_discount_percentage",
            "deposit_deadline_hours",
            "balance_deadline_days",
        ]


class BusinessHoursSerializer(serializers.ModelSerializer):
    """Horario de atención de un día de la semana."""

    class Meta:
        model = BusinessHours
        fields = [
            "id",
            "weekday",
            "is_open",
            "opening_time",
            "closing_time",
            "notes",
        ]


class UpdateBusinessHoursSerializer(serializers.Serializer):
    """Actualización de horario para un día específico."""

    weekday = serializers.IntegerField(min_value=1, max_value=7)
    is_open = serializers.BooleanField()
    opening_time = serializers.TimeField(required=False, allow_null=True)
    closing_time = serializers.TimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, default="", allow_blank=True)


class HolidaySerializer(serializers.ModelSerializer):
    """Día festivo."""

    class Meta:
        model = Holiday
        fields = [
            "id",
            "holiday_date",
            "holiday_name",
            "affects_shipping",
            "affects_pickup",
        ]


class CreateHolidaySerializer(serializers.Serializer):
    """Creación de un día festivo."""

    holiday_date = serializers.DateField()
    holiday_name = serializers.CharField(max_length=255)
    affects_shipping = serializers.BooleanField(default=True)
    affects_pickup = serializers.BooleanField(default=True)


class PaymentInstructionsSerializer(serializers.ModelSerializer):
    """Instrucciones de pago bancario."""

    class Meta:
        model = PaymentInstructions
        fields = [
            "bank_name",
            "account_holder",
            "account_number",
            "clabe",
            "card_number",
            "additional_notes",
        ]
