"""
Tests del modelo User y OTPCode.
Casos del plan: estructura de campos, propiedades, constraints.
"""
import pytest
from datetime import timedelta

from django.utils import timezone

from apps.authentication.models import OTPCode, User, UserRole


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_defaults(self):
        user = User.objects.create_user(
            phone="+529611111111",
            first_name="Ana",
        )
        assert user.role == UserRole.CUSTOMER
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_deleted is False
        assert user.email is None

    def test_is_admin_property(self):
        user = User(role=UserRole.ADMIN)
        assert user.is_admin is True
        assert user.is_customer is False

    def test_is_customer_property(self):
        user = User(role=UserRole.CUSTOMER)
        assert user.is_customer is True
        assert user.is_admin is False

    def test_str_representation(self):
        user = User(first_name="Ana", phone="+529611111111")
        assert "Ana" in str(user)
        assert "+529611111111" in str(user)

    def test_phone_is_unique(self, db):
        User.objects.create_user(phone="+529611111112", first_name="A")
        with pytest.raises(Exception):
            User.objects.create_user(phone="+529611111112", first_name="B")

    def test_email_is_unique(self, db):
        User.objects.create_user(
            phone="+529611111113", first_name="A", email="dup@test.com"
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                phone="+529611111114", first_name="B", email="dup@test.com"
            )

    def test_email_is_optional(self, db):
        user = User.objects.create_user(phone="+529611111115", first_name="A")
        assert user.email is None


@pytest.mark.django_db
class TestOTPCodeModel:
    def test_is_expired_false_when_fresh(self, db):
        otp = OTPCode.objects.create(
            phone="+529611111111",
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        assert otp.is_expired is False

    def test_is_expired_true_when_past(self, db):
        otp = OTPCode.objects.create(
            phone="+529611111111",
            code="123456",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        assert otp.is_expired is True

    def test_is_valid_fresh_unused(self, db):
        otp = OTPCode.objects.create(
            phone="+529611111111",
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        assert otp.is_valid is True

    def test_is_valid_false_when_used(self, db):
        otp = OTPCode.objects.create(
            phone="+529611111111",
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=10),
            is_used=True,
        )
        assert otp.is_valid is False

    def test_is_valid_false_when_expired(self, db):
        otp = OTPCode.objects.create(
            phone="+529611111111",
            code="123456",
            expires_at=timezone.now() - timedelta(seconds=1),
        )
        assert otp.is_valid is False

    def test_is_valid_false_when_max_attempts(self, db):
        otp = OTPCode.objects.create(
            phone="+529611111111",
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=10),
            attempts=5,
        )
        assert otp.is_valid is False

    def test_str_representation(self):
        otp = OTPCode(phone="+529611111111")
        assert "+529611111111" in str(otp)
