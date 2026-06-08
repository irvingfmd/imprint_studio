"""
Modelos de la app authentication.
User y OTPCode.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.authentication.managers import UserManager


class UserRole(models.TextChoices):
    CUSTOMER = "CUSTOMER", "Customer"
    ADMIN = "ADMIN", "Admin"


class User(AbstractBaseUser, PermissionsMixin):
    """
    Usuario del sistema. Se autentica por teléfono y OTP.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    phone = models.CharField(
        max_length=20,
        unique=True,
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
    )

    is_active = models.BooleanField(default=True)

    # Requerido por PermissionsMixin para el admin de Django.
    is_staff = models.BooleanField(default=False)

    last_login = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # El teléfono reemplaza al username estándar de Django.
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} ({self.phone})"

    @property
    def is_admin(self) -> bool:
        """
        Verifica si el usuario tiene rol de administrador.
        """
        return self.role == UserRole.ADMIN

    @property
    def is_customer(self) -> bool:
        """
        Verifica si el usuario tiene rol de cliente.
        """
        return self.role == UserRole.CUSTOMER


class OTPCode(models.Model):
    """
    Código OTP para autenticación. Expira en 10 minutos.
    Máximo 5 intentos fallidos.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Sin FK a users: puede generarse antes del registro.
    phone = models.CharField(max_length=20)

    code = models.CharField(max_length=6)

    is_used = models.BooleanField(default=False)

    attempts = models.PositiveSmallIntegerField(default=0)

    expires_at = models.DateTimeField()

    used_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_codes"
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["is_used"]),
            models.Index(
                fields=["phone", "is_used", "expires_at"],
                name="idx_otp_active_lookup",
            ),
        ]

    def __str__(self) -> str:
        return f"OTP {self.phone}"

    @property
    def is_expired(self) -> bool:
        """
        Verifica si el código ha expirado.
        """
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """
        Verifica si el código puede usarse para autenticarse.
        """
        return (
            not self.is_used
            and not self.is_expired
            and self.attempts < 5
        )