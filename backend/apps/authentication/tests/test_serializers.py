"""
Tests de los serializers de authentication.
"""

import pytest

from apps.authentication.serializers import (
    AdminUserSerializer,
    RegisterSerializer,
    SendOTPSerializer,
    UpdateUserRoleSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)


@pytest.mark.django_db
class TestRegisterSerializer:
    def test_valid_data(self):
        s = RegisterSerializer(
            data={
                "phone": "+529611300001",
                "first_name": "Test",
                "email": "valid@test.com",
            }
        )
        assert s.is_valid(), s.errors

    def test_phone_without_plus_is_invalid(self):
        s = RegisterSerializer(data={"phone": "9611234567", "first_name": "Test"})
        assert not s.is_valid()
        assert "phone" in s.errors

    def test_phone_too_short_is_invalid(self):
        s = RegisterSerializer(data={"phone": "+521", "first_name": "Test"})
        assert not s.is_valid()
        assert "phone" in s.errors

    def test_duplicate_email_is_invalid(self, customer):
        s = RegisterSerializer(
            data={
                "phone": "+529611300002",
                "first_name": "Otro",
                "email": customer.email,
            }
        )
        assert not s.is_valid()
        assert "email" in s.errors

    def test_duplicate_phone_is_invalid(self, customer):
        s = RegisterSerializer(
            data={
                "phone": customer.phone,
                "first_name": "Otro",
            }
        )
        assert not s.is_valid()
        assert "phone" in s.errors


class TestSendOTPSerializer:
    def test_phone_with_valid_format(self):
        # El serializer solo valida formato — la existencia la verifica el servicio
        # para evitar user enumeration (siempre responde 200).
        s = SendOTPSerializer(data={"phone": "+529611999000"})
        assert s.is_valid(), s.errors

    def test_phone_without_plus_is_invalid(self):
        s = SendOTPSerializer(data={"phone": "9611234567"})
        assert not s.is_valid()
        assert "phone" in s.errors

    def test_empty_phone_is_invalid(self):
        s = SendOTPSerializer(data={"phone": ""})
        assert not s.is_valid()
        assert "phone" in s.errors


class TestVerifyOTPSerializer:
    def test_valid_data(self):
        s = VerifyOTPSerializer(data={"phone": "+529611111111", "otp_code": "123456"})
        assert s.is_valid(), s.errors

    def test_non_numeric_otp_is_invalid(self):
        s = VerifyOTPSerializer(data={"phone": "+529611111111", "otp_code": "abc123"})
        assert not s.is_valid()
        assert "otp_code" in s.errors

    def test_short_otp_is_invalid(self):
        s = VerifyOTPSerializer(data={"phone": "+529611111111", "otp_code": "12345"})
        assert not s.is_valid()


@pytest.mark.django_db
class TestUserSerializer:
    def test_cliente_tiene_permissions_de_customer(self, customer):
        data = UserSerializer(customer).data
        assert "permissions" in data
        perms = data["permissions"]
        assert "create_order" in perms
        assert "view_own_orders" in perms
        assert "download_quote_pdf" in perms
        assert "view_all_orders" not in perms
        assert "manage_users" not in perms

    def test_admin_tiene_permissions_de_admin(self, admin_user):
        data = UserSerializer(admin_user).data
        perms = data["permissions"]
        assert "view_all_orders" in perms
        assert "manage_users" in perms
        assert "create_order" not in perms
        assert "view_own_orders" not in perms

    def test_campos_basicos_presentes(self, customer):
        data = UserSerializer(customer).data
        for field in ["id", "phone", "email", "first_name", "last_name", "role", "permissions"]:
            assert field in data

    def test_role_es_string_correcto(self, customer):
        data = UserSerializer(customer).data
        assert data["role"] == "CUSTOMER"


@pytest.mark.django_db
class TestAdminUserSerializer:
    def test_serializa_campos_esperados(self, customer):
        data = AdminUserSerializer(customer).data
        for field in ["id", "phone", "email", "first_name", "last_name", "role", "is_active", "created_at"]:
            assert field in data

    def test_no_expone_password(self, customer):
        data = AdminUserSerializer(customer).data
        assert "password" not in data

    def test_admin_user_role_es_admin(self, admin_user):
        data = AdminUserSerializer(admin_user).data
        assert data["role"] == "ADMIN"


class TestUpdateUserRoleSerializer:
    def test_role_admin_es_valido(self):
        s = UpdateUserRoleSerializer(data={"role": "ADMIN"})
        assert s.is_valid(), s.errors

    def test_role_customer_es_valido(self):
        s = UpdateUserRoleSerializer(data={"role": "CUSTOMER"})
        assert s.is_valid(), s.errors

    def test_role_invalido_falla(self):
        s = UpdateUserRoleSerializer(data={"role": "SUPERADMIN"})
        assert not s.is_valid()
        assert "role" in s.errors

    def test_sin_role_falla(self):
        s = UpdateUserRoleSerializer(data={})
        assert not s.is_valid()
        assert "role" in s.errors
