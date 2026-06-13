"""
Tests de RegisterService, OTPService y JWTService.
Casos del plan: 1-7 (registro, OTP, JWT).
"""
import pytest
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from apps.authentication.models import OTPCode, User
from apps.authentication.services import JWTService, OTPService, RegisterService


@pytest.mark.django_db
class TestRegisterService:
    def test_registro_correcto_crea_usuario(self):
        # Caso 1: registro correcto
        user = RegisterService().register({
            "phone": "+529611000010",
            "first_name": "Prueba",
            "last_name": "Usuario",
            "email": "prueba@test.com",
        })
        assert User.objects.filter(phone="+529611000010").exists()
        assert user.role == "CUSTOMER"
        assert user.is_active is True

    def test_registro_sin_email(self):
        user = RegisterService().register({
            "phone": "+529611000011",
            "first_name": "SinEmail",
        })
        assert user.email is None

    def test_registro_asigna_rol_customer(self):
        user = RegisterService().register({
            "phone": "+529611000012",
            "first_name": "Rol",
        })
        assert user.is_customer is True
        assert user.is_admin is False


@pytest.mark.django_db
class TestOTPService:
    def _create_user(self, phone: str = "+529611000020") -> User:
        return User.objects.create_user(phone=phone, first_name="Test")

    def test_genera_otp_valido(self):
        # Caso 4: OTP generado
        self._create_user()
        otp = OTPService().generate_and_send("+529611000020")
        assert len(otp.code) == 6
        assert otp.code.isdigit()
        assert otp.is_expired is False
        assert otp.is_used is False

    def test_invalidar_otps_anteriores_al_generar(self):
        # Generar dos OTPs seguidos: el primero debe quedar como usado
        self._create_user("+529611000021")
        otp1 = OTPService().generate_and_send("+529611000021")
        otp2 = OTPService().generate_and_send("+529611000021")

        otp1.refresh_from_db()
        assert otp1.is_used is True
        assert otp2.is_used is False

    def test_otp_correcto_retorna_usuario(self):
        # Caso 5: OTP correcto → JWT generado
        user = self._create_user("+529611000022")
        OTPCode.objects.create(
            phone="+529611000022",
            code="999888",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        resultado = OTPService().verify("+529611000022", "999888")
        assert resultado.id == user.id

    def test_otp_incorrecto_incrementa_intentos(self):
        # Caso 6: OTP incorrecto
        self._create_user("+529611000023")
        otp = OTPCode.objects.create(
            phone="+529611000023",
            code="111111",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        with pytest.raises(ValueError, match="Código incorrecto"):
            OTPService().verify("+529611000023", "000000")
        otp.refresh_from_db()
        assert otp.attempts == 1

    def test_otp_expirado_lanza_error(self):
        self._create_user("+529611000024")
        OTPCode.objects.create(
            phone="+529611000024",
            code="222222",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        with pytest.raises(ValueError, match="expirado"):
            OTPService().verify("+529611000024", "222222")

    def test_sin_otp_activo_lanza_error(self):
        self._create_user("+529611000025")
        with pytest.raises(ValueError, match="No existe"):
            OTPService().verify("+529611000025", "333333")

    def test_max_intentos_bloquea_verificacion(self):
        self._create_user("+529611000026")
        OTPCode.objects.create(
            phone="+529611000026",
            code="444444",
            expires_at=timezone.now() + timedelta(minutes=10),
            attempts=5,
        )
        with pytest.raises(ValueError, match="Demasiados intentos"):
            OTPService().verify("+529611000026", "444444")

    def test_otp_marcado_como_usado_al_verificar(self):
        self._create_user("+529611000027")
        otp = OTPCode.objects.create(
            phone="+529611000027",
            code="555555",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        OTPService().verify("+529611000027", "555555")
        otp.refresh_from_db()
        assert otp.is_used is True
        assert otp.used_at is not None


@pytest.mark.django_db
class TestJWTService:
    def test_genera_access_y_refresh_token(self, customer):
        # Caso 7: refresh token
        tokens = JWTService().generate_tokens(customer)
        assert "access" in tokens
        assert "refresh" in tokens
        assert len(tokens["access"]) > 20
        assert len(tokens["refresh"]) > 20
