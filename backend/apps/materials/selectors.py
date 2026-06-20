"""
Selectores para la app materials.
"""

from django.db.models import F, QuerySet

from .models import Material


def get_all_materials(active_only: bool = False, low_stock: bool = False) -> QuerySet:
    qs = Material.objects.all()
    if active_only:
        qs = qs.filter(is_active=True)
    if low_stock:
        qs = qs.filter(stock_grams__lt=F("min_stock_grams"))
    return qs.order_by("material_type", "name")


def get_material_by_id(material_id: str) -> Material | None:
    try:
        return Material.objects.get(id=material_id)
    except Material.DoesNotExist:
        return None


def get_low_stock_materials() -> QuerySet:
    return Material.objects.filter(
        is_active=True,
        stock_grams__lt=F("min_stock_grams"),
    ).order_by("stock_grams")
