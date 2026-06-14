"""
Tests de los endpoints de authentication.
Casos del plan: 1-7 (registro, OTP, JWT, me).
"""
import pytest
from datetime import timedelta

from django.utils import timezone

from apps.authentication.models import OTPCode, User


REGISTER_URL = "/api/v1/auth/register/"
OTP_SEND_URL = "/api/v1/auth/otp/send/"
OTP_VERIFY_URL = "/api/v1/auth/otp/verify/"
TOKEN_REFRESH_URL = "/api/v1/auth/token/refresh/"
ME_URL = "/api/v1/auth/me/"


@pytest.mark.django_db
class TestRegisterView:
    def test_registro_correcto_devuelve_201(self, api_client):
        # Caso 1: registro correcto
        resp = api_client.post(REGISTER_URL, {
            "phone": "+529611200001",
            "first_name": "Ana",
            "last_name": "López",
            "email": "ana@test.com",
        })
        assert resp.status_code == 201
        assert User.objects.filter(phone="+529611200001").exists()

    def test_telefono_duplicado_devuelve_400(self, api_client, customer):
        # Caso 2: teléfono duplicado
        resp = api_client.post(REGISTER_URL, {
            "phone": customer.phone,
            "first_name": "Otro",
        })
        assert resp.status_code == 400

    def test_email_duplicado_devuelve_400(self, api_client, customer):
        # Caso 3: email duplicado
        resp = api_client.post(REGISTER_URL, {
            "phone": "+529611200002",
            "first_name": "Otro",
            "email": customer.email,
        })
        assert resp.status_code == 400

    def test_telefono_sin_formato_e164_devuelve_400(self, api_client):
        resp = api_client.post(REGISTER_URL, {
            "phone": "9611234567",
            "first_name": "Test",
        })
        assert resp.status_code == 400

    def test_first_name_requerido(self, api_client):
        resp = api_client.post(REGISTER_URL, {"phone": "+529611200003"})
        assert resp.status_code == 400


@pytest.mark.django_db
class TestSendOTPView:
    def test_envio_otp_usuario_existente(self, api_client, customer):
        # Caso 4: OTP generado
        resp = api_client.post(OTP_SEND_URL, {"phone": customer.phone})
        assert resp.status_code == 200
        assert OTPCode.objects.filter(phone=customer.phone, is_used=False).exists()

    def test_envio_otp_telefono_no_registrado_devuelve_200(self, api_client):
        # Siempre 200 para evitar user enumeration — no se crea OTP internamente.
        resp = api_client.post(OTP_SEND_URL, {"phone": "+529611999999"})
        assert resp.status_code == 200
        assert not OTPCode.objects.filter(phone="+529611999999").exists()

    def test_envio_otp_invalida_codigos_anteriores(self, api_client, customer):
        OTPCode.objects.create(
            phone=customer.phone,
            code="111111",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        api_client.post(OTP_SEND_URL, {"phone": customer.phone})
        assert not OTPCode.objects.filter(
            phone=customer.phone, code="111111", is_used=False
        ).exists()


@pytest.mark.django_db
class TestVerifyOTPView:
    def _create_otp(self, phone: str, code: str = "123456") -> OTPCode:
        return OTPCode.objects.create(
            phone=phone,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=10),
        )

    def test_otp_correcto_devuelve_tokens(self, api_client, customer):
        # Caso 5: OTP correcto → JWT generado
        self._create_otp(customer.phone)
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "123456",
        })
        assert resp.status_code == 200
        assert "access" in resp.data["data"]
        assert "refresh" in resp.data["data"]

    def test_otp_incorrecto_devuelve_401(self, api_client, customer):
        # Caso 6: OTP incorrecto → 401
        self._create_otp(customer.phone)
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "000000",
        })
        assert resp.status_code == 401

    def test_otp_expirado_devuelve_401(self, api_client, customer):
        OTPCode.objects.create(
            phone=customer.phone,
            code="999999",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "999999",
        })
        assert resp.status_code == 401

    def test_otp_code_no_numerico_devuelve_400(self, api_client, customer):
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "abcdef",
        })
        assert resp.status_code == 400

    def test_otp_length_incorrecta_devuelve_400(self, api_client, customer):
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "12345",
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestTokenRefreshView:
    def test_refresh_token_devuelve_nuevo_access(self, api_client, customer):
        # Caso 7: refresh token
        from apps.authentication.services import JWTService
        tokens = JWTService().generate_tokens(customer)
        resp = api_client.post(TOKEN_REFRESH_URL, {"refresh": tokens["refresh"]})
        assert resp.status_code == 200
        assert "access" in resp.data

    def test_refresh_token_invalido_devuelve_401(self, api_client):
        resp = api_client.post(TOKEN_REFRESH_URL, {"refresh": "token.invalido.xxx"})
        assert resp.status_code == 401


@pytest.mark.django_db
class TestMeView:
    def test_me_autenticado_devuelve_datos_usuario(self, auth_client, customer):
        resp = auth_client.get(ME_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["phone"] == customer.phone
        assert resp.data["data"]["role"] == "CUSTOMER"

    def test_me_sin_token_devuelve_401(self, api_client):
        # Caso 58: sin JWT → 401
        resp = api_client.get(ME_URL)
        assert resp.status_code == 401
