"""
Fixtures compartidos entre todas las apps.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from apps.authentication.models import OTPCode, User, UserRole
from apps.authentication.services import _hash_otp


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    return User.objects.create_user(
        phone="+529611000001",
        first_name="Cliente",
        last_name="Prueba",
        email="cliente@prueba.com",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        phone="+529611000002",
        first_name="Admin",
        last_name="Prueba",
        email="admin@prueba.com",
        role=UserRole.ADMIN,
        is_staff=True,
    )


@pytest.fixture
def auth_client(api_client, customer):
    api_client.force_authenticate(user=customer)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def shipping_address(customer):
    from apps.shipping.models import ShippingAddress
    return ShippingAddress.objects.create(
        user=customer,
        address_name="Casa",
        street="Av. Central 123",
        city="Tuxtla Gutiérrez",
        state="Chiapas",
        postal_code="29000",
        country="México",
    )


def make_otp(phone: str, code: str = "123456", minutes: int = 10) -> OTPCode:
    """Crea un OTPCode válido para pruebas. Almacena el hash como en producción."""
    return OTPCode.objects.create(
        phone=phone,
        code=_hash_otp(code),
        expires_at=timezone.now() + timedelta(minutes=minutes),
    )
