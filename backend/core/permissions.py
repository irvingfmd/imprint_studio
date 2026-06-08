"""
Permisos base del sistema.

Documentados en 04-api-specification.md.
"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permite acceso únicamente a usuarios con rol ADMIN.
    """

    message = "Permission denied"

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsCustomer(BasePermission):
    """
    Permite acceso únicamente a usuarios con rol CUSTOMER.
    """

    message = "Permission denied"

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and request.user.is_customer
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permite acceso al propietario del recurso o a un administrador.
    El objeto debe tener un campo customer o user que apunte al usuario.
    """

    message = "Permission denied"

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_admin:
            return True

        # Soporte para objetos con campo customer o user.
        owner = getattr(obj, "customer", None) or getattr(obj, "user", None)
        return owner == request.user