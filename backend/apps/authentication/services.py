"""
Servicios de la app authentication.

Contiene toda la lógica de negocio para registro,
generación y verificación de OTP, y autenticación JWT.
"""
import logging
import random
import string
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.models import OTPCode, User

logger = logging.getLogger(__name__)


class RegisterService:
    """
    Gestiona el registro de nuevos usuarios.
    """

    def register(self, validated_data: dict) -> User:
        """
        Crea un nuevo usuario cliente.
        """
        user = User.objects.create_user(
            phone=validated_data["phone"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ""),
            email=validated_data.get("email"),
        )

        logger.info("Usuario registrado: %s", user.phone)
        return user


class OTPService:
    """
    Gestiona la generación y verificación de códigos OTP.
    """

    def generate_and_send(self, phone: str) -> OTPCode:
        """
        Genera un nuevo código OTP e invalida los anteriores.
        En desarrollo imprime el código en consola.
        En producción lo envía por WhatsApp.
        """
        # Invalidar códigos anteriores del mismo teléfono.
        OTPCode.objects.filter(
            phone=phone,
            is_used=False,
        ).update(is_used=True)

        # Generar código de 6 dígitos.
        code = self._generate_code()

        # Calcular expiración.
        expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 10)
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

        # Guardar en base de datos.
        otp = OTPCode.objects.create(
            phone=phone,
            code=code,
            expires_at=expires_at,
        )

        # Enviar código.
        self._send(phone, code)

        return otp

    def verify(self, phone: str, code: str) -> User:
        """
        Verifica el código OTP y retorna el usuario autenticado.
        Lanza ValueError si el código es inválido.
        """
        max_attempts = getattr(settings, "OTP_MAX_ATTEMPTS", 5)

        # Buscar código activo más reciente.
        otp = OTPCode.objects.filter(
            phone=phone,
            is_used=False,
        ).order_by("-created_at").first()

        if not otp:
            raise ValueError("No existe un código OTP activo para este teléfono.")

        if otp.is_expired:
            raise ValueError("El código OTP ha expirado.")

        if otp.attempts >= max_attempts:
            raise ValueError("Demasiados intentos fallidos. Solicita un nuevo código.")

        if otp.code != code:
            # Registrar intento fallido.
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            intentos_restantes = max_attempts - otp.attempts
            raise ValueError(
                f"Código incorrecto. Te quedan {intentos_restantes} intentos."
            )

        # Marcar como usado.
        otp.is_used = True
        otp.used_at = timezone.now()
        otp.save(update_fields=["is_used", "used_at"])

        # Obtener usuario.
        try:
            user = User.objects.get(phone=phone, is_active=True)
        except User.DoesNotExist:
            raise ValueError("No existe una cuenta activa con este teléfono.")

        logger.info("OTP verificado correctamente: %s", phone)
        return user

    def _generate_code(self) -> str:
        """
        Genera un código numérico de 6 dígitos.
        """
        return "".join(random.choices(string.digits, k=6))

    def _send(self, phone: str, code: str) -> None:
        """
        Envía el código OTP al teléfono.
        En desarrollo lo imprime en consola.
        En producción usa WhatsApp Business API.
        """
        if settings.DEBUG:
            # En desarrollo mostramos el código en consola.
            logger.info("=" * 40)
            logger.info("OTP para %s: %s", phone, code)
            logger.info("=" * 40)
        else:
            # En producción enviar por WhatsApp.
            # TODO: Implementar WhatsAppNotificationService
            logger.info("OTP generado para %s (producción)", phone)


class JWTService:
    """
    Genera tokens JWT para usuarios autenticados.
    """

    def generate_tokens(self, user: User) -> dict:
        """
        Genera access y refresh token para el usuario.
        """
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }