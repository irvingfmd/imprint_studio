"""
Serializers para la app loyalty.
"""

from rest_framework import serializers

from .models import DiscountCode, DiscountRedemption, DiscountType


class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = [
            "id",
            "code",
            "discount_type",
            "discount_value",
            "min_order_amount",
            "max_uses",
            "current_uses",
            "valid_from",
            "valid_until",
            "is_active",
            "created_at",
        ]


class CreateDiscountCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    discount_type = serializers.ChoiceField(choices=DiscountType.choices)
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    min_order_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, default=0
    )
    max_uses = serializers.IntegerField(min_value=1, required=False, allow_null=True, default=None)
    valid_from = serializers.DateTimeField()
    valid_until = serializers.DateTimeField(required=False, allow_null=True, default=None)
    is_active = serializers.BooleanField(default=True)

    def validate_code(self, value: str) -> str:
        return value.upper().strip()


class ValidateDiscountCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)


class DiscountRedemptionSerializer(serializers.ModelSerializer):
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    customer_name = serializers.SerializerMethodField()
    order_title = serializers.CharField(source="order.title", read_only=True)

    class Meta:
        model = DiscountRedemption
        fields = [
            "id",
            "order",
            "customer",
            "customer_phone",
            "customer_name",
            "order_title",
            "discount_applied",
            "redeemed_at",
        ]

    def get_customer_name(self, obj) -> str:
        return f"{obj.customer.first_name} {obj.customer.last_name}".strip()
