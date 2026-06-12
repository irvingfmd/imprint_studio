"""
Configuración del panel de administración para la app payments.
"""
from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "payment_type",
        "payment_method",
        "payment_status",
        "amount",
        "manual_confirmation",
        "confirmed_by",
        "confirmed_at",
        "created_at",
    ]
    list_filter = ["payment_type", "payment_method", "payment_status", "manual_confirmation"]
    search_fields = ["id", "order__id", "notes"]
    readonly_fields = [
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
    ordering = ["-created_at"]

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
