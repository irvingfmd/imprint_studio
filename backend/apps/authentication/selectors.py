"""
Selectores de la app authentication.

Queries de solo lectura para usuarios.
"""

from django.db.models import QuerySet

from apps.authentication.models import User


def get_all_users() -> QuerySet:
    return User.objects.filter(is_deleted=False).order_by("created_at")


def get_user_by_id(user_id: str) -> User | None:
    try:
        return User.objects.get(id=user_id, is_deleted=False)
    except User.DoesNotExist:
        return None
