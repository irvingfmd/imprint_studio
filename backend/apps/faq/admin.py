from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "display_order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    ordering = ("display_order",)
