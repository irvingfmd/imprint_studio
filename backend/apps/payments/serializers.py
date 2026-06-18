"""
Serializers para la app payments.
"""

from decimal import Decimal

from rest_framework import serializers

from .models import Payment, PaymentMethod, PaymentType


class PaymentSerializer(serializers.ModelSerializer):
    """Representación completa de un pago."""

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "amount",
            "payment_type",
            "payment_method",
            "payment_status",
            "proof_file_url",
            "manual_confirmation",
            "confirmed_by",
            "confirmed_at",
            "notes",
            "created_at",
        ]
        read_only_fields = fields


class PaymentProofSerializer(serializers.Serializer):
    """Recibe la URL del comprobante ya almacenado en el storage externo."""

    file_url = serializers.URLField()


class ManualConfirmationSerializer(serializers.Serializer):
    """Confirmación manual de pago por parte del administrador."""

    payment_type = serializers.ChoiceField(choices=PaymentType.choices)
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    notes = serializers.CharField(required=False, default="", allow_blank=True)


class ConfirmPaymentSerializer(serializers.Serializer):
    """Confirmación de un pago pendiente."""

    notes = serializers.CharField(required=False, default="", allow_blank=True)


class RejectPaymentSerializer(serializers.Serializer):
    """Rechazo de un pago pendiente."""

    reason = serializers.CharField()


class RefundSerializer(serializers.Serializer):
    """Registro de un reembolso."""

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    reason = serializers.CharField()
