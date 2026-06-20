from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("order", "customer", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("comment",)
    readonly_fields = ("id", "order", "customer", "rating", "comment", "created_at")
