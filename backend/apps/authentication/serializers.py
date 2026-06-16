"""
Serializers de la app authentication.

Validan y serializan los datos de entrada y salida
para los endpoints de registro, OTP y JWT.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.authentication.models import User, UserRole


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios.
    Endpoint: POST /api/v1/auth/register/
    """

    class Meta:
        model = User
        fields = ["phone", "email", "first_name", "last_name"]
        extra_kwargs = {
            "phone": {
                "validators": [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="Este teléfono ya está registrado.",
                    )
                ],
            },
            "email": {
                "validators": [
                    UniqueValidator(
                        queryset=User.objects.filter(email__isnull=False),
                        message="Este email ya está registrado.",
                    )
                ],
            },
        }

    def validate_email(self, value: str) -> str | None:
        """
        Valida que el email no esté registrado.
        Convierte string vacío a None para respetar el unique constraint.
        """
        if not value:
            return None
        if User.objects.filter(email=value).exists():
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
        Valida solo el formato E.164. La existencia del usuario la verifica
        el servicio de forma silenciosa para evitar user enumeration.
        """
        if not value.startswith("+"):
            raise serializers.ValidationError(
                "El teléfono debe estar en formato E.164. Ejemplo: +5219611234567"
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

    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj: User) -> list[str]:
        if obj.is_admin:
            return [
                "view_all_orders",
                "create_quote",
                "confirm_payment",
                "reject_payment",
                "process_refund",
                "change_order_status",
                "manage_shipments",
                "manage_configuration",
                "view_dashboard",
                "manage_users",
            ]
        return [
            "create_order",
            "view_own_orders",
            "view_own_quotes",
            "download_quote_pdf",
            "upload_files",
            "upload_payment_proof",
            "view_own_payments",
            "manage_addresses",
            "request_cancellation",
        ]

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "email",
            "first_name",
            "last_name",
            "role",
            "permissions",
        ]
        read_only_fields = fields


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Serializer para listar y ver detalle de usuarios desde el panel admin.
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
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


class UpdateUserRoleSerializer(serializers.Serializer):
    """
    Serializer para cambiar el rol de un usuario.
    Endpoint: PUT /api/v1/admin/users/{user_id}/role/
    """

    role = serializers.ChoiceField(choices=UserRole.choices)