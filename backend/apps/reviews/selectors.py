"""
Selectores de la app reviews.
"""

from django.db.models import QuerySet

from .models import Review


def get_review_for_order(order_id: str) -> Review | None:
    try:
        return Review.objects.select_related("customer").get(order_id=order_id)
    except Review.DoesNotExist:
        return None


def get_reviews_for_customer(customer_id: str) -> QuerySet:
    return Review.objects.filter(customer_id=customer_id).order_by("-created_at")


def get_all_reviews() -> QuerySet:
    return Review.objects.select_related("customer", "order").order_by("-created_at")
