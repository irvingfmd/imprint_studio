"""
Registro de modelos de quotes en el panel de administración Django.
"""

from django.contrib import admin

from .models import Quote, QuoteSnapshot


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ["order", "total_price", "quote_status", "created_by", "created_at"]
    list_filter = ["quote_status"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(QuoteSnapshot)
class QuoteSnapshotAdmin(admin.ModelAdmin):
    list_display = ["quote", "material_cost_per_kg", "profit_margin_percentage", "created_at"]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]
