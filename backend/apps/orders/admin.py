"""
Registro de modelos de orders en el panel de administración Django.
"""
from django.contrib import admin

from .models import Order, OrderEvent, RequestFile


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["title", "customer", "status", "priority", "payment_status", "created_at"]
    list_filter = ["status", "priority", "payment_status", "request_type", "delivery_method"]
    search_fields = ["title", "customer__phone", "customer__first_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(RequestFile)
class RequestFileAdmin(admin.ModelAdmin):
    list_display = ["original_filename", "file_type", "order", "uploaded_by", "uploaded_at"]
    list_filter = ["file_type"]
    readonly_fields = ["id", "uploaded_at"]
    ordering = ["-uploaded_at"]


@admin.register(OrderEvent)
class OrderEventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "order", "created_by", "created_at"]
    list_filter = ["event_type"]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]
