"""
Configuración del panel de administración para la app production.
"""

from django.contrib import admin

from .models import ProductionHistory


@admin.register(ProductionHistory)
class ProductionHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "previous_status",
        "new_status",
        "changed_by",
        "notes",
        "changed_at",
    ]
    list_filter = ["new_status", "previous_status"]
    search_fields = ["order__id", "notes"]
    readonly_fields = [
        "id",
        "order",
        "previous_status",
        "new_status",
        "changed_by",
        "notes",
        "changed_at",
    ]
    ordering = ["-changed_at"]

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
