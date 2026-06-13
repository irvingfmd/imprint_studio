"""
Tests de modelos de la app payments.
Cubre: Payment — campos, defaults, str, sin updated_at, soft delete.
"""
import pytest
from decimal import Decimal

from apps.orders.models import Order, OrderStatus, RequestType
from apps.payments.models import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    PaymentType,
)


def _make_order(customer) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Figura Test",
        description="Para prueba",
        quantity=1,
        priority="NORMAL",
        status=OrderStatus.RECEIVED,
    )


def _make_payment(order, **kwargs) -> Payment:
    defaults = dict(
        order=order,
        amount=Decimal("218.24"),
        payment_type=PaymentType.DEPOSIT,
        payment_method=PaymentMethod.BANK_TRANSFER,
    )
    defaults.update(kwargs)
    return Payment.objects.create(**defaults)


@pytest.mark.django_db
class TestPaymentModel:
    def test_defaults_on_create(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        assert payment.payment_status == PaymentStatus.PENDING
        assert payment.proof_file_url == ""
        assert payment.manual_confirmation is False
        assert payment.confirmed_by is None
        assert payment.confirmed_at is None
        assert payment.notes == ""
        assert payment.is_deleted is False
        assert payment.deleted_at is None

    def test_str_representation(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        s = str(payment)
        assert "DEPOSIT" in s
        assert "PENDING" in s
        assert "218.24" in s

    def test_uuid_primary_key(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        assert payment.id is not None
        assert "-" in str(payment.id)

    def test_created_at_set_on_create(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        assert payment.created_at is not None

    def test_no_updated_at_field(self, customer):
        # Los pagos son registros inmutables por diseño: no tienen updated_at
        order = _make_order(customer)
        payment = _make_payment(order)
        assert not hasattr(payment, "updated_at")

    def test_soft_delete_fields_exist(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        assert hasattr(payment, "is_deleted")
        assert hasattr(payment, "deleted_at")

    def test_order_reverse_relation(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        assert payment in order.payments.all()

    def test_full_payment_type_stored(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order, payment_type=PaymentType.FULL_PAYMENT)
        assert payment.payment_type == PaymentType.FULL_PAYMENT

    def test_refund_type_stored(self, customer):
        order = _make_order(customer)
        payment = _make_payment(
            order,
            payment_type=PaymentType.REFUND,
            payment_status=PaymentStatus.CONFIRMED,
        )
        assert payment.payment_type == PaymentType.REFUND
        assert payment.payment_status == PaymentStatus.CONFIRMED

    def test_confirmed_by_nullable(self, customer, admin_user):
        order = _make_order(customer)
        payment = _make_payment(order, confirmed_by=admin_user)
        payment.refresh_from_db()
        assert payment.confirmed_by == admin_user
