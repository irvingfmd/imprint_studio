"""
Serializers para la app orders.
"""

from django.core.exceptions import ObjectDoesNotExist
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
            "id",
            "title",
            "description",
            "color",
            "quantity",
            "dimensions_notes",
            "request_type",
            "priority",
            "status",
            "payment_status",
            "delivery_method",
            "estimated_delivery_date",
            "approved_at",
            "ready_at",
            "delivered_at",
            "cancelled_at",
            "cancellation_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "payment_status",
            "approved_at",
            "ready_at",
            "delivered_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]


class AdminOrderDetailSerializer(OrderDetailSerializer):
    """Serializer de detalle para admins. Incluye envío anidado y cotización activa."""

    shipment = serializers.SerializerMethodField()
    active_quote = serializers.SerializerMethodField()

    class Meta(OrderDetailSerializer.Meta):
        fields = OrderDetailSerializer.Meta.fields + ["shipment", "active_quote"]

    def get_active_quote(self, obj) -> dict | None:
        from apps.quotes.models import Quote
        from apps.quotes.serializers import QuoteSerializer

        quote = Quote.objects.filter(order=obj, is_deleted=False).order_by("-created_at").first()
        if not quote:
            return None
        return QuoteSerializer(quote).data

    def get_shipment(self, obj) -> dict | None:
        try:
            s = obj.shipment
            return {
                "id": str(s.id),
                "carrier_name": s.carrier_name,
                "tracking_number": s.tracking_number,
                "shipping_cost": str(s.shipping_cost),
                "shipped_at": s.shipped_at.isoformat() if s.shipped_at else None,
                "delivered_at": s.delivered_at.isoformat() if s.delivered_at else None,
                "shipping_notes": s.shipping_notes,
            }
        except ObjectDoesNotExist:
            return None


class OrderCreateSerializer(serializers.Serializer):
    request_type = serializers.ChoiceField(choices=RequestType.choices)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    color = serializers.CharField(max_length=100, required=False, default="", allow_blank=True)
    quantity = serializers.IntegerField(min_value=1)
    dimensions_notes = serializers.CharField(required=False, default="", allow_blank=True)
    priority = serializers.ChoiceField(choices=OrderPriority.choices, default=OrderPriority.NORMAL)
    delivery_method = serializers.ChoiceField(choices=DeliveryMethod.choices, default=DeliveryMethod.PICKUP)


class RequestFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestFile
        fields = [
            "id",
            "file_type",
            "file_url",
            "original_filename",
            "mime_type",
            "file_size_bytes",
            "uploaded_at",
        ]


class RequestFileUploadSerializer(serializers.Serializer):
    file_url = serializers.URLField(max_length=2048)
    file_type = serializers.ChoiceField(choices=FileType.choices)
    original_filename = serializers.CharField(max_length=255)
    mime_type = serializers.CharField(max_length=100, required=False, default="text/uri-list")
    file_size_bytes = serializers.IntegerField(min_value=0, required=False, default=0)

    def validate(self, attrs: dict) -> dict:
        # Los archivos físicos deben tener MIME y tamaño reales
        if attrs["file_type"] != FileType.WEB_MODEL:
            if not attrs.get("mime_type") or attrs["mime_type"] == "text/uri-list":
                raise serializers.ValidationError({"mime_type": "Este campo es requerido para archivos físicos."})
            if attrs["file_size_bytes"] < 1:
                raise serializers.ValidationError({"file_size_bytes": "Debe ser mayor a 0 para archivos físicos."})
        return attrs


class AssignShippingAddressSerializer(serializers.Serializer):
    shipping_address_id = serializers.UUIDField()


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=1000)


class AdminOrderCreateSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField()
    request_type = serializers.ChoiceField(choices=RequestType.choices)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    color = serializers.CharField(max_length=100, required=False, default="", allow_blank=True)
    quantity = serializers.IntegerField(min_value=1)
    dimensions_notes = serializers.CharField(required=False, default="", allow_blank=True)
    priority = serializers.ChoiceField(choices=OrderPriority.choices, default=OrderPriority.NORMAL)
    delivery_method = serializers.ChoiceField(choices=DeliveryMethod.choices, default=DeliveryMethod.PICKUP)


class AdminOrderListSerializer(serializers.ModelSerializer):
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "title",
            "status",
            "priority",
            "payment_status",
            "request_type",
            "delivery_method",
            "customer_phone",
            "created_at",
        ]
