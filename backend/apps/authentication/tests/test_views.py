"""
Tests de los endpoints de authentication.
Casos del plan: 1-7 (registro, OTP, JWT, me).
"""
import pytest
from datetime import timedelta

from django.utils import timezone

from apps.authentication.models import OTPCode, User
from apps.authentication.services import _hash_otp


REGISTER_URL = "/api/v1/auth/register/"
OTP_SEND_URL = "/api/v1/auth/otp/send/"
OTP_VERIFY_URL = "/api/v1/auth/otp/verify/"
TOKEN_REFRESH_URL = "/api/v1/auth/token/refresh/"
ME_URL = "/api/v1/auth/me/"

ADMIN_USERS_URL = "/api/v1/admin/users/"


def admin_user_detail_url(user_id):
    return f"/api/v1/admin/users/{user_id}/"


def admin_user_role_url(user_id):
    return f"/api/v1/admin/users/{user_id}/role/"


@pytest.mark.django_db
class TestRegisterView:
    def test_valid_registration_returns_201(self, api_client):
        # Caso 1: registro correcto
        resp = api_client.post(REGISTER_URL, {
            "phone": "+529611200001",
            "first_name": "Ana",
            "last_name": "López",
            "email": "ana@test.com",
        })
        assert resp.status_code == 201
        assert User.objects.filter(phone="+529611200001").exists()

    def test_duplicate_phone_returns_400(self, api_client, customer):
        # Caso 2: teléfono duplicado
        resp = api_client.post(REGISTER_URL, {
            "phone": customer.phone,
            "first_name": "Otro",
        })
        assert resp.status_code == 400

    def test_duplicate_email_returns_400(self, api_client, customer):
        # Caso 3: email duplicado
        resp = api_client.post(REGISTER_URL, {
            "phone": "+529611200002",
            "first_name": "Otro",
            "email": customer.email,
        })
        assert resp.status_code == 400

    def test_phone_without_e164_format_returns_400(self, api_client):
        resp = api_client.post(REGISTER_URL, {
            "phone": "9611234567",
            "first_name": "Test",
        })
        assert resp.status_code == 400

    def test_first_name_required(self, api_client):
        resp = api_client.post(REGISTER_URL, {"phone": "+529611200003"})
        assert resp.status_code == 400


@pytest.mark.django_db
class TestSendOTPView:
    def test_otp_send_existing_user(self, api_client, customer):
        # Caso 4: OTP generado
        resp = api_client.post(OTP_SEND_URL, {"phone": customer.phone})
        assert resp.status_code == 200
        assert OTPCode.objects.filter(phone=customer.phone, is_used=False).exists()

    def test_otp_send_unregistered_phone_returns_200(self, api_client):
        # Siempre 200 para evitar user enumeration — no se crea OTP internamente.
        resp = api_client.post(OTP_SEND_URL, {"phone": "+529611999999"})
        assert resp.status_code == 200
        assert not OTPCode.objects.filter(phone="+529611999999").exists()

    def test_otp_send_invalidates_previous_codes(self, api_client, customer):
        OTPCode.objects.create(
            phone=customer.phone,
            code=_hash_otp("111111"),
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
            code=_hash_otp(code),
            expires_at=timezone.now() + timedelta(minutes=10),
        )

    def test_correct_otp_returns_tokens(self, api_client, customer):
        # Caso 5: OTP correcto → JWT generado
        self._create_otp(customer.phone)
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "123456",
        })
        assert resp.status_code == 200
        assert "access" in resp.data["data"]
        assert "refresh" in resp.data["data"]

    def test_incorrect_otp_returns_401(self, api_client, customer):
        # Caso 6: OTP incorrecto → 401
        self._create_otp(customer.phone)
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "000000",
        })
        assert resp.status_code == 401

    def test_expired_otp_returns_401(self, api_client, customer):
        OTPCode.objects.create(
            phone=customer.phone,
            code=_hash_otp("999999"),
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "999999",
        })
        assert resp.status_code == 401

    def test_non_numeric_otp_code_returns_400(self, api_client, customer):
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "abcdef",
        })
        assert resp.status_code == 400

    def test_incorrect_otp_length_returns_400(self, api_client, customer):
        resp = api_client.post(OTP_VERIFY_URL, {
            "phone": customer.phone,
            "otp_code": "12345",
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestTokenRefreshView:
    def test_refresh_token_returns_new_access(self, api_client, customer):
        # Caso 7: refresh token
        from apps.authentication.services import JWTService
        tokens = JWTService().generate_tokens(customer)
        resp = api_client.post(TOKEN_REFRESH_URL, {"refresh": tokens["refresh"]})
        assert resp.status_code == 200
        assert "access" in resp.data

    def test_invalid_refresh_token_returns_401(self, api_client):
        resp = api_client.post(TOKEN_REFRESH_URL, {"refresh": "token.invalido.xxx"})
        assert resp.status_code == 401


@pytest.mark.django_db
class TestMeView:
    def test_authenticated_me_returns_user_data(self, auth_client, customer):
        resp = auth_client.get(ME_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["phone"] == customer.phone
        assert resp.data["data"]["role"] == "CUSTOMER"

    def test_me_incluye_campo_permissions(self, auth_client):
        resp = auth_client.get(ME_URL)
        assert resp.status_code == 200
        assert "permissions" in resp.data["data"]
        assert isinstance(resp.data["data"]["permissions"], list)

    def test_unauthenticated_me_returns_401(self, api_client):
        # Caso 58: sin JWT → 401
        resp = api_client.get(ME_URL)
        assert resp.status_code == 401


@pytest.mark.django_db
class TestAdminListUsersView:
    def test_admin_lista_todos_los_usuarios(self, admin_client, customer, admin_user):
        resp = admin_client.get(ADMIN_USERS_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["count"] >= 2

    def test_respuesta_incluye_campos_esperados(self, admin_client, customer):
        resp = admin_client.get(ADMIN_USERS_URL)
        assert resp.status_code == 200
        first = resp.data["data"]["results"][0]
        for field in ["id", "phone", "role", "is_active"]:
            assert field in first

    def test_respuesta_incluye_num_pages(self, admin_client, customer):
        resp = admin_client.get(ADMIN_USERS_URL)
        assert resp.status_code == 200
        assert "num_pages" in resp.data["data"]

    def test_page_size_parametro_funciona(self, admin_client, customer, admin_user):
        resp = admin_client.get(ADMIN_USERS_URL + "?page_size=1")
        assert resp.status_code == 200
        assert len(resp.data["data"]["results"]) == 1
        assert resp.data["data"]["num_pages"] >= 2

    def test_page_size_invalido_devuelve_400(self, admin_client):
        resp = admin_client.get(ADMIN_USERS_URL + "?page_size=abc")
        assert resp.status_code == 400

    def test_page_size_cap_en_100(self, admin_client, customer, admin_user):
        resp = admin_client.get(ADMIN_USERS_URL + "?page_size=9999")
        assert resp.status_code == 200
        # No debe devolver más de 100 resultados por página aunque se pidan más.
        assert len(resp.data["data"]["results"]) <= 100

    def test_cliente_recibe_403(self, auth_client):
        resp = auth_client.get(ADMIN_USERS_URL)
        assert resp.status_code == 403

    def test_sin_token_recibe_401(self, api_client):
        resp = api_client.get(ADMIN_USERS_URL)
        assert resp.status_code == 401


@pytest.mark.django_db
class TestAdminRetrieveUserView:
    def test_admin_obtiene_detalle_de_usuario(self, admin_client, customer):
        resp = admin_client.get(admin_user_detail_url(customer.id))
        assert resp.status_code == 200
        assert resp.data["data"]["phone"] == customer.phone

    def test_usuario_inexistente_devuelve_404(self, admin_client):
        import uuid
        resp = admin_client.get(admin_user_detail_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_cliente_recibe_403(self, auth_client, customer):
        resp = auth_client.get(admin_user_detail_url(customer.id))
        assert resp.status_code == 403

    def test_sin_token_recibe_401(self, api_client, customer):
        resp = api_client.get(admin_user_detail_url(customer.id))
        assert resp.status_code == 401


@pytest.mark.django_db
class TestAdminUpdateUserRoleView:
    def test_admin_promueve_cliente_a_admin(self, admin_client, customer):
        resp = admin_client.put(
            admin_user_role_url(customer.id),
            {"role": "ADMIN"},
            format="json",
        )
        assert resp.status_code == 200
        customer.refresh_from_db()
        assert customer.role == "ADMIN"
        assert customer.is_staff is True

    def test_admin_degrada_admin_a_cliente(self, admin_client, admin_user):
        # Crear segundo admin para degradar (no al mismo que hace la petición)
        segundo_admin = User.objects.create_user(
            phone="+529611777001",
            first_name="Segundo",
            role="ADMIN",
            is_staff=True,
        )
        resp = admin_client.put(
            admin_user_role_url(segundo_admin.id),
            {"role": "CUSTOMER"},
            format="json",
        )
        assert resp.status_code == 200
        segundo_admin.refresh_from_db()
        assert segundo_admin.role == "CUSTOMER"
        assert segundo_admin.is_staff is False

    def test_respuesta_incluye_datos_actualizados(self, admin_client, customer):
        resp = admin_client.put(
            admin_user_role_url(customer.id),
            {"role": "ADMIN"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["data"]["role"] == "ADMIN"

    def test_rol_invalido_devuelve_400(self, admin_client, customer):
        resp = admin_client.put(
            admin_user_role_url(customer.id),
            {"role": "SUPERUSER"},
            format="json",
        )
        assert resp.status_code == 400

    def test_usuario_inexistente_devuelve_404(self, admin_client):
        import uuid
        resp = admin_client.put(
            admin_user_role_url(uuid.uuid4()),
            {"role": "ADMIN"},
            format="json",
        )
        assert resp.status_code == 404

    def test_cliente_recibe_403(self, auth_client, customer):
        resp = auth_client.put(
            admin_user_role_url(customer.id),
            {"role": "ADMIN"},
            format="json",
        )
        assert resp.status_code == 403

    def test_admin_no_puede_cambiar_su_propio_rol(self, admin_client, admin_user):
        resp = admin_client.put(
            admin_user_role_url(admin_user.id),
            {"role": "CUSTOMER"},
            format="json",
        )
        assert resp.status_code == 400
        admin_user.refresh_from_db()
        assert admin_user.role == "ADMIN"

    def test_sin_token_recibe_401(self, api_client, customer):
        resp = api_client.put(
            admin_user_role_url(customer.id),
            {"role": "ADMIN"},
            format="json",
        )
        assert resp.status_code == 401
