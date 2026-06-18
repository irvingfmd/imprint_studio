"""
Selectores para la app faq.
"""

from django.db.models import QuerySet

from .models import FAQ


def get_active_faqs() -> QuerySet:
    """Retorna FAQs activas ordenadas por display_order."""
    return FAQ.objects.filter(is_active=True).order_by("display_order", "created_at")


def get_all_faqs() -> QuerySet:
    """Retorna todas las FAQs (admin)."""
    return FAQ.objects.all().order_by("display_order", "created_at")


def get_faq_by_id(faq_id: str) -> FAQ | None:
    try:
        return FAQ.objects.get(id=faq_id)
    except FAQ.DoesNotExist:
        return None
