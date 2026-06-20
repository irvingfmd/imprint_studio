from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "material_type", "brand", "price_per_kg", "stock_grams", "is_active")
    list_filter = ("material_type", "is_active")
    search_fields = ("name", "brand")
