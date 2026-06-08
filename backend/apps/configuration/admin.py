"""
Registro de modelos de configuration en el admin de Django.
"""
from django.contrib import admin

from apps.configuration.models import (
    BusinessConfig,
    BusinessHours,
    Holiday,
    PaymentInstructions,
)


@admin.register(BusinessConfig)
class BusinessConfigAdmin(admin.ModelAdmin):
    list_display = ["id", "profit_margin_percentage", "is_active", "created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ["weekday", "is_open", "opening_time", "closing_time"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["holiday_name", "holiday_date", "affects_shipping", "affects_pickup"]
    readonly_fields = ["id", "created_at"]


@admin.register(PaymentInstructions)
class PaymentInstructionsAdmin(admin.ModelAdmin):
    list_display = ["bank_name", "account_holder", "is_active", "updated_at"]
    readonly_fields = ["id", "created_at", "updated_at"]