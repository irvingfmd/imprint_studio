"""
Serializers para la app orders.
"""
from rest_framework import serializers

from .models import DeliveryMethod, FileType, Order, OrderPriority, RequestFile, RequestType


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "title", "status", "priority", "payment_status", "created_at"]


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "title", "description", "color", "quantity", "dimensions_notes",
            "request_type", "priority", "status", "payment_status",
            "delivery_method", "estimated_delivery_date",
            "approved_at", "ready_at", "delivered_at", "cancelled_at", "cancellation_reason",
            "created_at", "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    request_type = serializers.ChoiceField(choices=RequestType.choices)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    color = serializers.CharField(max_length=100, required=False, default="")
    quantity = serializers.IntegerField(min_value=1)
    dimensions_notes = serializers.CharField(required=False, default="")
    priority = serializers.ChoiceField(choices=OrderPriority.choices, default=OrderPriority.NORMAL)
    delivery_method = serializers.ChoiceField(choices=DeliveryMethod.choices, default=DeliveryMethod.PICKUP)


class RequestFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestFile
        fields = [
            "id", "file_type", "file_url", "original_filename",
            "mime_type", "file_size_bytes", "uploaded_at",
        ]


class RequestFileUploadSerializer(serializers.Serializer):
    file_url = serializers.URLField(max_length=2048)
    file_type = serializers.ChoiceField(choices=FileType.choices)
    original_filename = serializers.CharField(max_length=255)
    mime_type = serializers.CharField(max_length=100)
    file_size_bytes = serializers.IntegerField(min_value=1)


class AssignShippingAddressSerializer(serializers.Serializer):
    shipping_address_id = serializers.UUIDField()


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField()


class AdminOrderListSerializer(serializers.ModelSerializer):
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "title", "status", "priority", "payment_status",
            "request_type", "delivery_method", "customer_phone", "created_at",
        ]
