"""
Serializers para la app faq.
"""

from rest_framework import serializers

from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    """Representación pública de una FAQ."""

    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "display_order"]
        read_only_fields = fields


class FAQCreateUpdateSerializer(serializers.Serializer):
    """Validación para crear o actualizar FAQs (admin)."""

    question = serializers.CharField(max_length=500)
    answer = serializers.CharField()
    display_order = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)
