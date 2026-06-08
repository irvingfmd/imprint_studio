"""
Modelos base abstractos reutilizables.

Todas las entidades principales del sistema deben heredar
de BaseModel o SoftDeleteModel según corresponda.
"""
import uuid

from django.db import models


class BaseModel(models.Model):
    """
    Modelo base con UUID como clave primaria y campos de auditoría.
    Todas las entidades principales del sistema heredan de aquí.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(BaseModel):
    """
    Extiende BaseModel con soporte de eliminación lógica.

    Las entidades que no deben eliminarse físicamente heredan de aquí:
    users, orders, quotes, payments.
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True