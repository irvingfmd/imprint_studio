"""
Serializers de la app authentication.

Validan y serializan los datos de entrada y salida
para los endpoints de registro, OTP y JWT.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.authentication.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios.
    Endpoint: POST /api/v1/auth/register/
    """

    class Meta:
        model = User
        fields = ["phone", "email", "first_name", "last_name"]

    def validate_phone(self, value: str) -> str:
        """
        Valida que el teléfono esté en formato E.164.
        Ejemplo válido: +5219611234567
        """
        if not value.startswith("+"):
            raise serializers.ValidationError(
                "El teléfono debe estar en formato E.164. Ejemplo: +5219611234567"
            )
        if not value[1:].isdigit():
            raise serializers.ValidationError(
                "El teléfono solo debe contener dígitos después del símbolo +."
            )
        if len(value) < 10 or len(value) > 16:
            raise serializers.ValidationError(
                "El teléfono debe tener entre 10 y 16 caracteres."
            )
        return value

    def validate_email(self, value: str) -> str:
        """
        Valida que el email no esté registrado.
        """
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Este email ya está registrado."
            )
        return value

    def validate_phone(self, value: str) -> str:
        """
        Valida formato E.164 y que el teléfono no esté registrado.
        """
        if not value.startswith("+"):
            raise serializers.ValidationError(
                "El teléfono debe estar en formato E.164. Ejemplo: +5219611234567"
            )
        if not value[1:].isdigit():
            raise serializers.ValidationError(
                "El teléfono solo debe contener dígitos después del símbolo +."
            )
        if len(value) < 10 or len(value) > 16:
            raise serializers.ValidationError(
                "El teléfono debe tener entre 10 y 16 caracteres."
            )
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "Este teléfono ya está registrado."
            )
        return value


class SendOTPSerializer(serializers.Serializer):
    """
    Serializer para solicitar envío de OTP.
    Endpoint: POST /api/v1/auth/otp/send/
    """

    phone = serializers.CharField(max_length=20)

    def validate_phone(self, value: str) -> str:
        """
        Valida que el teléfono esté registrado en el sistema.
        """
        if not value.startswith("+"):
            raise serializers.ValidationError(
                "El teléfono debe estar en formato E.164. Ejemplo: +5219611234567"
            )
        if not User.objects.filter(phone=value, is_active=True).exists():
            raise serializers.ValidationError(
                "No existe una cuenta activa con este teléfono."
            )
        return value


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer para verificar código OTP.
    Endpoint: POST /api/v1/auth/otp/verify/
    """

    phone = serializers.CharField(max_length=20)
    otp_code = serializers.CharField(max_length=6, min_length=6)

    def validate_otp_code(self, value: str) -> str:
        """
        Valida que el código OTP sea numérico.
        """
        if not value.isdigit():
            raise serializers.ValidationError(
                "El código OTP debe contener solo dígitos."
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar información del usuario autenticado.
    Endpoint: GET /api/v1/auth/me/
    """

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "email",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = fields