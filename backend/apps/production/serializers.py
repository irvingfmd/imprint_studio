"""
Serializers para la app production.
"""

from rest_framework import serializers

from apps.orders.models import OrderEvent, OrderStatus

from .models import ProductionHistory


class ProductionHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductionHistory
        fields = [
            "id",
            "previous_status",
            "new_status",
            "changed_by",
            "changed_by_name",
            "notes",
            "changed_at",
        ]
        read_only_fields = fields

    def get_changed_by_name(self, obj) -> str:
        return obj.changed_by.first_name if obj.changed_by else ""


class OrderEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderEvent
        fields = [
            "id",
            "event_type",
            "event_description",
            "metadata",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = fields

    def get_created_by_name(self, obj) -> str:
        return obj.created_by.first_name if obj.created_by else ""


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)
    notes = serializers.CharField(required=False, default="", allow_blank=True)


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField()


class RevertOrderStatusSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=1000)
