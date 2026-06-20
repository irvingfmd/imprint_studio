from django.contrib import admin

from .models import DiscountCode, DiscountRedemption


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_type", "discount_value", "current_uses", "max_uses", "is_active"]
    list_filter = ["discount_type", "is_active"]
    search_fields = ["code"]


@admin.register(DiscountRedemption)
class DiscountRedemptionAdmin(admin.ModelAdmin):
    list_display = ["discount_code", "order", "customer", "discount_applied", "redeemed_at"]
    list_filter = ["redeemed_at"]
