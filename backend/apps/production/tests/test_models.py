"""
Tests de modelos de la app production.
Cubre: ProductionHistory — campos, defaults, str, sin updated_at, inmutabilidad.
"""

import pytest

from apps.orders.models import Order, OrderStatus, RequestType
from apps.production.models import ProductionHistory


def _make_order(customer, status=OrderStatus.RECEIVED) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido Test",
        description="Para prueba",
        quantity=1,
        priority="NORMAL",
        status=status,
    )


def _make_history(order, admin_user, previous=None, new_status=OrderStatus.QUOTED) -> ProductionHistory:
    return ProductionHistory.objects.create(
        order=order,
        previous_status=previous,
        new_status=new_status,
        changed_by=admin_user,
    )


@pytest.mark.django_db
class TestProductionHistoryModel:
    def test_str_with_previous_status(self, customer, admin_user):
        order = _make_order(customer)
        history = _make_history(order, admin_user, previous=OrderStatus.RECEIVED, new_status=OrderStatus.QUOTED)
        s = str(history)
        assert "RECEIVED" in s
        assert "QUOTED" in s

    def test_str_without_previous_status(self, customer, admin_user):
        # El primer cambio no tiene previous_status
        order = _make_order(customer)
        history = _make_history(order, admin_user, previous=None, new_status=OrderStatus.RECEIVED)
        s = str(history)
        assert "—" in s
        assert "RECEIVED" in s

    def test_uuid_primary_key(self, customer, admin_user):
        order = _make_order(customer)
        history = _make_history(order, admin_user)
        assert history.id is not None
        assert "-" in str(history.id)

    def test_changed_at_set_on_create(self, customer, admin_user):
        order = _make_order(customer)
        history = _make_history(order, admin_user)
        assert history.changed_at is not None

    def test_no_updated_at_field(self, customer, admin_user):
        # ProductionHistory es inmutable por diseño: no tiene updated_at
        order = _make_order(customer)
        history = _make_history(order, admin_user)
        assert not hasattr(history, "updated_at")

    def test_notes_default_empty(self, customer, admin_user):
        order = _make_order(customer)
        history = _make_history(order, admin_user)
        assert history.notes == ""

    def test_notes_stored(self, customer, admin_user):
        order = _make_order(customer)
        history = ProductionHistory.objects.create(
            order=order,
            previous_status=OrderStatus.RECEIVED,
            new_status=OrderStatus.QUOTED,
            changed_by=admin_user,
            notes="Laminado revisado en Bambu Studio",
        )
        assert history.notes == "Laminado revisado en Bambu Studio"

    def test_previous_status_nullable(self, customer, admin_user):
        order = _make_order(customer)
        history = _make_history(order, admin_user, previous=None)
        assert history.previous_status is None

    def test_order_reverse_relation(self, customer, admin_user):
        order = _make_order(customer)
        history = _make_history(order, admin_user)
        assert history in order.production_history.all()

    def test_changed_by_stored(self, customer, admin_user):
        order = _make_order(customer)
        history = _make_history(order, admin_user)
        assert history.changed_by == admin_user
