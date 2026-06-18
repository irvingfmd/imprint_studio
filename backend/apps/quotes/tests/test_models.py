"""
Tests de modelos de la app quotes.
Casos cubiertos: campos y defaults de Quote y QuoteSnapshot.
"""

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.orders.models import Order, OrderStatus, RequestType
from apps.quotes.models import Quote, QuoteSnapshot, QuoteStatus


def _make_order(customer) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Figura Dragon",
        description="Escala 1:10",
        quantity=1,
        priority="NORMAL",
        status=OrderStatus.RECEIVED,
    )


def _make_quote(order, admin_user, **kwargs) -> Quote:
    defaults = dict(
        order=order,
        created_by=admin_user,
        weight_grams=Decimal("100.00"),
        print_time_hours=Decimal("5.00"),
        material_cost=Decimal("2.50"),
        energy_cost=Decimal("2.50"),
        labor_cost=Decimal("75.00"),
        post_processing_cost=Decimal("5.00"),
        packaging_cost=Decimal("2.00"),
        risk_cost=Decimal("0.50"),
        subtotal=Decimal("87.50"),
        profit_amount=Decimal("26.25"),
        total_price=Decimal("113.75"),
    )
    defaults.update(kwargs)
    return Quote.objects.create(**defaults)


def _make_snapshot(quote) -> QuoteSnapshot:
    return QuoteSnapshot.objects.create(
        quote=quote,
        material_cost_per_kg=Decimal("25.00"),
        electricity_rate_kwh=Decimal("2.0000"),
        labor_cost_per_hour=Decimal("15.00"),
        post_processing_cost_per_gram=Decimal("0.05"),
        packaging_cost=Decimal("2.00"),
        failure_percentage=Decimal("10.00"),
        profit_margin_percentage=Decimal("30.00"),
        urgent_multiplier=Decimal("1.30"),
        express_multiplier=Decimal("1.50"),
        full_payment_discount_percentage=Decimal("5.00"),
        printer_name="Bambu Lab X1C",
        printer_power_watts=350,
    )


@pytest.mark.django_db
class TestQuoteModel:
    def test_defaults_on_create(self, customer, admin_user):
        # Campos opcionales deben tener defaults correctos
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        assert quote.quote_status == QuoteStatus.PENDING
        assert quote.shipping_cost == Decimal("0.00")
        assert quote.discount_amount == Decimal("0.00")
        assert quote.is_deleted is False
        assert quote.accepted_at is None
        assert quote.rejected_at is None
        assert quote.expires_at is None
        assert quote.deleted_at is None

    def test_str_representation(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        s = str(quote)
        assert "PENDING" in s
        assert "113.75" in s

    def test_uuid_primary_key(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        assert quote.id is not None
        assert "-" in str(quote.id)

    def test_timestamps_set_on_create(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        assert quote.created_at is not None
        assert quote.updated_at is not None

    def test_soft_delete_fields_exist(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        assert hasattr(quote, "is_deleted")
        assert hasattr(quote, "deleted_at")

    def test_accepted_status_stores_timestamp(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        now = timezone.now()
        quote.quote_status = QuoteStatus.ACCEPTED
        quote.accepted_at = now
        quote.save()
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.ACCEPTED
        assert quote.accepted_at is not None

    def test_rejected_status_stores_timestamp(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        quote.quote_status = QuoteStatus.REJECTED
        quote.rejected_at = timezone.now()
        quote.save()
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.REJECTED
        assert quote.rejected_at is not None

    def test_order_reverse_relation(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        assert quote in order.quotes.all()


@pytest.mark.django_db
class TestQuoteSnapshotModel:
    def test_str_representation(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        snapshot = _make_snapshot(quote)
        assert str(quote.id) in str(snapshot)

    def test_created_at_set_on_create(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        snapshot = _make_snapshot(quote)
        assert snapshot.created_at is not None

    def test_no_updated_at_field(self, customer, admin_user):
        # Los snapshots son inmutables por diseño: no tienen updated_at
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        snapshot = _make_snapshot(quote)
        assert not hasattr(snapshot, "updated_at")

    def test_one_to_one_with_quote(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        snapshot = _make_snapshot(quote)
        assert quote.snapshot == snapshot
