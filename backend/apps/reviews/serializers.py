"""
Serializers para la app reviews.
"""

from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "order_id",
            "customer",
            "customer_name",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = fields

    def get_customer_name(self, obj) -> str:
        return f"{obj.customer.first_name} {obj.customer.last_name}".strip()


class CreateReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, default="", allow_blank=True, max_length=2000)
