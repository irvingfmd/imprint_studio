"""
Selectores para la app loyalty.
"""

from django.db.models import QuerySet

from .models import DiscountCode, DiscountRedemption


def get_discount_code_by_code(code: str) -> DiscountCode | None:
    try:
        return DiscountCode.objects.get(code=code.upper())
    except DiscountCode.DoesNotExist:
        return None


def get_discount_code_by_id(discount_id: str) -> DiscountCode | None:
    try:
        return DiscountCode.objects.get(id=discount_id)
    except DiscountCode.DoesNotExist:
        return None


def get_all_discount_codes(active_only: bool = False) -> QuerySet:
    qs = DiscountCode.objects.all()
    if active_only:
        qs = qs.filter(is_active=True)
    return qs.order_by("-created_at")


def get_redemptions_for_discount(discount_id: str) -> QuerySet:
    return DiscountRedemption.objects.filter(discount_code_id=discount_id).select_related(
        "customer", "order"
    ).order_by("-redeemed_at")


def get_redemptions_for_order(order_id: str) -> QuerySet:
    return DiscountRedemption.objects.filter(order_id=order_id).select_related("discount_code")
