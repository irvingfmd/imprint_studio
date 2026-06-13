"""
Tests de los serializers de authentication.
"""
import pytest

from apps.authentication.serializers import (
    RegisterSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
)
from apps.authentication.models import User


@pytest.mark.django_db
class TestRegisterSerializer:
    def test_datos_validos(self):
        s = RegisterSerializer(data={
            "phone": "+529611300001",
            "first_name": "Test",
            "email": "valid@test.com",
        })
        assert s.is_valid(), s.errors

    def test_telefono_sin_plus_es_invalido(self):
        s = RegisterSerializer(data={"phone": "9611234567", "first_name": "Test"})
        assert not s.is_valid()
        assert "phone" in s.errors

    def test_telefono_muy_corto_es_invalido(self):
        s = RegisterSerializer(data={"phone": "+521", "first_name": "Test"})
        assert not s.is_valid()
        assert "phone" in s.errors

    def test_email_duplicado_es_invalido(self, customer):
        s = RegisterSerializer(data={
            "phone": "+529611300002",
            "first_name": "Otro",
            "email": customer.email,
        })
        assert not s.is_valid()
        assert "email" in s.errors

    def test_telefono_duplicado_es_invalido(self, customer):
        s = RegisterSerializer(data={
            "phone": customer.phone,
            "first_name": "Otro",
        })
        assert not s.is_valid()
        assert "phone" in s.errors


class TestSendOTPSerializer:
    def test_telefono_con_formato_valido(self):
        # El serializer solo valida formato — la existencia la verifica el servicio
        # para evitar user enumeration (siempre responde 200).
        s = SendOTPSerializer(data={"phone": "+529611999000"})
        assert s.is_valid(), s.errors

    def test_telefono_sin_plus_es_invalido(self):
        s = SendOTPSerializer(data={"phone": "9611234567"})
        assert not s.is_valid()
        assert "phone" in s.errors

    def test_telefono_vacio_es_invalido(self):
        s = SendOTPSerializer(data={"phone": ""})
        assert not s.is_valid()
        assert "phone" in s.errors


class TestVerifyOTPSerializer:
    def test_datos_validos(self):
        s = VerifyOTPSerializer(data={"phone": "+529611111111", "otp_code": "123456"})
        assert s.is_valid(), s.errors

    def test_otp_no_numerico_es_invalido(self):
        s = VerifyOTPSerializer(data={"phone": "+529611111111", "otp_code": "abc123"})
        assert not s.is_valid()
        assert "otp_code" in s.errors

    def test_otp_muy_corto_es_invalido(self):
        s = VerifyOTPSerializer(data={"phone": "+529611111111", "otp_code": "12345"})
        assert not s.is_valid()
