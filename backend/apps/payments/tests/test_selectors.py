"""
Tests de selectores de la app payments.
Cubre: get_payment_by_id, get_payments_for_order,
       get_pending_payments, get_all_payments.
Verifica aislamiento y filtros.
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
from apps.payments import selectors


def _make_order(customer) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido Selector",
        description="Test",
        quantity=1,
        priority="NORMAL",
        status=OrderStatus.RECEIVED,
    )


def _make_payment(order, status=PaymentStatus.PENDING, ptype=PaymentType.DEPOSIT, is_deleted=False) -> Payment:
    return Payment.objects.create(
        order=order,
        amount=Decimal("218.24"),
        payment_type=ptype,
        payment_method=PaymentMethod.BANK_TRANSFER,
        payment_status=status,
        is_deleted=is_deleted,
    )


@pytest.mark.django_db
class TestGetPaymentById:
    def test_retorna_pago_existente(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        result = selectors.get_payment_by_id(str(payment.id))
        assert result is not None
        assert result.id == payment.id

    def test_retorna_none_cuando_no_existe(self):
        import uuid
        result = selectors.get_payment_by_id(str(uuid.uuid4()))
        assert result is None

    def test_retorna_none_cuando_eliminado(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order, is_deleted=True)
        result = selectors.get_payment_by_id(str(payment.id))
        assert result is None


@pytest.mark.django_db
class TestGetPaymentsForOrder:
    def test_retorna_pagos_del_pedido(self, customer):
        order = _make_order(customer)
        _make_payment(order)
        _make_payment(order, status=PaymentStatus.CONFIRMED)
        qs = selectors.get_payments_for_order(str(order.id))
        assert qs.count() == 2

    def test_excluye_eliminados(self, customer):
        order = _make_order(customer)
        _make_payment(order)
        _make_payment(order, is_deleted=True)
        qs = selectors.get_payments_for_order(str(order.id))
        assert qs.count() == 1

    def test_excluye_pagos_de_otro_pedido(self, customer):
        order1 = _make_order(customer)
        order2 = _make_order(customer)
        _make_payment(order1)
        _make_payment(order2)
        qs = selectors.get_payments_for_order(str(order1.id))
        assert qs.count() == 1

    def test_ordenados_por_created_at_desc(self, customer):
        order = _make_order(customer)
        _make_payment(order)
        _make_payment(order)
        qs = list(selectors.get_payments_for_order(str(order.id)))
        assert qs[0].created_at >= qs[-1].created_at


@pytest.mark.django_db
class TestGetPendingPayments:
    def test_retorna_solo_pendientes(self, customer):
        order = _make_order(customer)
        _make_payment(order, status=PaymentStatus.PENDING)
        _make_payment(order, status=PaymentStatus.CONFIRMED)
        _make_payment(order, status=PaymentStatus.REJECTED)
        qs = selectors.get_pending_payments()
        assert qs.count() == 1

    def test_excluye_eliminados(self, customer):
        order = _make_order(customer)
        _make_payment(order, status=PaymentStatus.PENDING, is_deleted=True)
        qs = selectors.get_pending_payments()
        assert qs.count() == 0


@pytest.mark.django_db
class TestGetAllPayments:
    def test_retorna_todos_sin_filtros(self, customer):
        order = _make_order(customer)
        _make_payment(order, status=PaymentStatus.PENDING)
        _make_payment(order, status=PaymentStatus.CONFIRMED, ptype=PaymentType.FULL_PAYMENT)
        qs = selectors.get_all_payments()
        assert qs.count() == 2

    def test_filtra_por_payment_type(self, customer):
        order = _make_order(customer)
        _make_payment(order, ptype=PaymentType.DEPOSIT)
        _make_payment(order, ptype=PaymentType.FULL_PAYMENT)
        qs = selectors.get_all_payments(payment_type=PaymentType.DEPOSIT)
        assert qs.count() == 1

    def test_filtra_por_payment_status(self, customer):
        order = _make_order(customer)
        _make_payment(order, status=PaymentStatus.PENDING)
        _make_payment(order, status=PaymentStatus.CONFIRMED)
        qs = selectors.get_all_payments(payment_status=PaymentStatus.CONFIRMED)
        assert qs.count() == 1

    def test_filtra_por_order_id(self, customer):
        order1 = _make_order(customer)
        order2 = _make_order(customer)
        _make_payment(order1)
        _make_payment(order2)
        qs = selectors.get_all_payments(order_id=str(order1.id))
        assert qs.count() == 1

    def test_excluye_eliminados(self, customer):
        order = _make_order(customer)
        _make_payment(order, is_deleted=True)
        qs = selectors.get_all_payments()
        assert qs.count() == 0
