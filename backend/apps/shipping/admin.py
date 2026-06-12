"""
Registro de modelos de shipping en el panel de administración Django.
"""
from django.contrib import admin

from .models import Shipment, ShippingAddress


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["address_name", "user", "city", "state", "is_default", "created_at"]
    list_filter = ["city", "state", "is_default"]
    search_fields = ["address_name", "user__phone", "street", "neighborhood"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ["order", "carrier_name", "tracking_number", "shipped_at", "delivered_at"]
    list_filter = ["carrier_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]
