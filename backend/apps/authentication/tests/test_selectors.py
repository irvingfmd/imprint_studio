"""
Tests de los selectores de authentication.
"""

import pytest

from apps.authentication.models import User
from apps.authentication.selectors import get_all_users, get_user_by_id


@pytest.mark.django_db
class TestGetAllUsers:
    def test_retorna_todos_los_usuarios_activos(self, customer, admin_user):
        users = get_all_users()
        ids = list(users.values_list("id", flat=True))
        assert customer.id in ids
        assert admin_user.id in ids

    def test_no_retorna_usuarios_eliminados(self, customer):
        customer.is_deleted = True
        customer.save(update_fields=["is_deleted"])
        users = get_all_users()
        assert customer.id not in list(users.values_list("id", flat=True))

    def test_retorna_queryset_ordenado_por_fecha_de_creacion(self, db):
        u1 = User.objects.create_user(phone="+529611800001", first_name="Primero")
        u2 = User.objects.create_user(phone="+529611800002", first_name="Segundo")
        ids = list(get_all_users().values_list("id", flat=True))
        assert ids.index(u1.id) < ids.index(u2.id)

    def test_sin_usuarios_retorna_queryset_vacio(self, db):
        assert get_all_users().count() == 0


@pytest.mark.django_db
class TestGetUserById:
    def test_retorna_usuario_existente(self, customer):
        result = get_user_by_id(str(customer.id))
        assert result is not None
        assert result.id == customer.id

    def test_retorna_none_si_no_existe(self, db):
        import uuid

        result = get_user_by_id(str(uuid.uuid4()))
        assert result is None

    def test_retorna_none_si_usuario_eliminado(self, customer):
        customer.is_deleted = True
        customer.save(update_fields=["is_deleted"])
        result = get_user_by_id(str(customer.id))
        assert result is None

    def test_retorna_usuario_admin(self, admin_user):
        result = get_user_by_id(str(admin_user.id))
        assert result is not None
        assert result.is_admin
