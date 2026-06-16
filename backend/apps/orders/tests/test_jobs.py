"""
Tests del scheduler de cancelación automática de anticipos vencidos.
Fuente: docs/appendices/status-flow.md — Cancelación Automática por Vencimiento de Anticipo.
"""
from decimal import Decimal

import pytest
from datetime import timedelta

from django.utils import timezone

from apps.configuration.models import BusinessConfig
from apps.orders.jobs import cancel_expired_deposits, expire_pending_quotes
from apps.orders.models import Order, OrderStatus, RequestType
from apps.production.models import ProductionHistory


@pytest.fixture(autouse=True)
def business_config(db):
    """BusinessConfig mínima necesaria para que el job funcione."""
    return BusinessConfig.objects.create(
        material_cost_per_kg=Decimal("250.00"),
        electricity_rate_kwh=Decimal("2.0000"),
        labor_cost_per_hour=Decimal("80.00"),
        post_processing_cost_per_gram=Decimal("0.50"),
        packaging_cost=Decimal("15.00"),
        failure_percentage=Decimal("5.00"),
        profit_margin_percentage=Decimal("30.00"),
        urgent_multiplier=Decimal("1.25"),
        express_multiplier=Decimal("1.50"),
        full_payment_discount_percentage=Decimal("5.00"),
        deposit_deadline_hours=72,
        balance_deadline_days=7,
        is_active=True,
    )


def _make_pending_deposit_order(customer) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido anticipo",
        description="Test scheduler",
        quantity=1,
        priority="NORMAL",
        status=OrderStatus.PENDING_DEPOSIT,
    )


def _register_transition(order, admin_user, hours_ago: int) -> None:
    """Crea un registro de ProductionHistory con fecha configurable en el pasado."""
    entry = ProductionHistory.objects.create(
        order=order,
        previous_status=OrderStatus.APPROVED,
        new_status=OrderStatus.PENDING_DEPOSIT,
        changed_by=admin_user,
    )
    ProductionHistory.objects.filter(pk=entry.pk).update(
        changed_at=timezone.now() - timedelta(hours=hours_ago)
    )


@pytest.mark.django_db
class TestCancelExpiredDeposits:
    def test_cancels_expired_order(self, customer, admin_user):
        """Pedido en PENDING_DEPOSIT >72h debe ser cancelado automáticamente."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=73)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        assert "automática" in order.cancellation_reason

    def test_cancellation_reason_includes_hours(self, customer, admin_user):
        """La razón de cancelación menciona el plazo en horas."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=73)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert "72" in order.cancellation_reason

    def test_does_not_cancel_order_within_deadline(self, customer, admin_user):
        """Pedido en PENDING_DEPOSIT <72h NO debe ser cancelado."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=24)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT

    def test_does_not_cancel_order_at_deadline_boundary(self, customer, admin_user):
        """71h 59m no supera el plazo de 72h."""
        order = _make_pending_deposit_order(customer)
        entry = ProductionHistory.objects.create(
            order=order,
            previous_status=OrderStatus.APPROVED,
            new_status=OrderStatus.PENDING_DEPOSIT,
            changed_by=admin_user,
        )
        ProductionHistory.objects.filter(pk=entry.pk).update(
            changed_at=timezone.now() - timedelta(hours=71, minutes=59)
        )

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT

    def test_ignores_orders_in_other_statuses(self, customer, admin_user):
        """No toca pedidos que no están en PENDING_DEPOSIT."""
        order = Order.objects.create(
            customer=customer,
            request_type=RequestType.REFERENCE,
            title="Pedido PRINTING",
            description="Test",
            quantity=1,
            priority="NORMAL",
            status=OrderStatus.PRINTING,
        )

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PRINTING

    def test_cancels_multiple_expired_orders(self, customer, admin_user):
        """Cancela múltiples pedidos vencidos en una sola ejecución."""
        order_a = _make_pending_deposit_order(customer)
        order_b = _make_pending_deposit_order(customer)
        _register_transition(order_a, admin_user, hours_ago=80)
        _register_transition(order_b, admin_user, hours_ago=100)

        cancel_expired_deposits()

        order_a.refresh_from_db()
        order_b.refresh_from_db()
        assert order_a.status == OrderStatus.CANCELLED
        assert order_b.status == OrderStatus.CANCELLED

    def test_cancels_expired_but_not_active_orders(self, customer, admin_user):
        """Solo cancela los vencidos, no los que están dentro del plazo."""
        expired_order = _make_pending_deposit_order(customer)
        active_order = _make_pending_deposit_order(customer)
        _register_transition(expired_order, admin_user, hours_ago=80)
        _register_transition(active_order, admin_user, hours_ago=10)

        cancel_expired_deposits()

        expired_order.refresh_from_db()
        active_order.refresh_from_db()
        assert expired_order.status == OrderStatus.CANCELLED
        assert active_order.status == OrderStatus.PENDING_DEPOSIT

    def test_uses_config_deposit_deadline_hours(self, customer, admin_user, business_config):
        """Respeta el valor configurable de BusinessConfig.deposit_deadline_hours."""
        business_config.deposit_deadline_hours = 24
        business_config.save()

        expired_order = _make_pending_deposit_order(customer)
        active_order = _make_pending_deposit_order(customer)
        _register_transition(expired_order, admin_user, hours_ago=25)
        _register_transition(active_order, admin_user, hours_ago=23)

        cancel_expired_deposits()

        expired_order.refresh_from_db()
        active_order.refresh_from_db()
        assert expired_order.status == OrderStatus.CANCELLED
        assert active_order.status == OrderStatus.PENDING_DEPOSIT

    def test_creates_production_history_with_null_changed_by(self, customer, admin_user):
        """La cancelación automática registra ProductionHistory con changed_by=None."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=73)

        cancel_expired_deposits()

        history = ProductionHistory.objects.get(
            order=order,
            new_status=OrderStatus.CANCELLED,
        )
        assert history.changed_by is None

    def test_does_not_cancel_soft_deleted_order(self, customer, admin_user):
        """No toca pedidos con is_deleted=True."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=80)
        Order.objects.filter(pk=order.pk).update(is_deleted=True)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT

    def test_does_nothing_without_active_config(self, customer, admin_user, business_config):
        """Si no hay BusinessConfig activa, el job no cancela nada."""
        business_config.is_active = False
        business_config.save()

        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=80)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT


@pytest.mark.django_db
class TestExpirePendingQuotes:
    def _make_quote(self, customer, admin_user, expires_delta_days: int):
        from decimal import Decimal
        from apps.quotes.models import Quote, QuoteStatus
        order = Order.objects.create(
            customer=customer,
            request_type=RequestType.REFERENCE,
            title="Pedido cotización",
            description="Test",
            quantity=1,
            priority="NORMAL",
            status=OrderStatus.QUOTED,
        )
        quote = Quote.objects.create(
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
            shipping_cost=Decimal("0.00"),
            subtotal=Decimal("87.50"),
            profit_amount=Decimal("26.25"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("113.75"),
            quote_status=QuoteStatus.PENDING,
            expires_at=timezone.now() + timedelta(days=expires_delta_days),
        )
        return quote

    def test_expira_cotizacion_vencida(self, customer, admin_user):
        from apps.quotes.models import QuoteStatus
        quote = self._make_quote(customer, admin_user, expires_delta_days=-1)
        expire_pending_quotes()
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.EXPIRED

    def test_no_expira_cotizacion_vigente(self, customer, admin_user):
        from apps.quotes.models import QuoteStatus
        quote = self._make_quote(customer, admin_user, expires_delta_days=3)
        expire_pending_quotes()
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.PENDING

    def test_expira_multiples_cotizaciones(self, customer, admin_user):
        from apps.quotes.models import QuoteStatus
        q1 = self._make_quote(customer, admin_user, expires_delta_days=-2)
        q2 = self._make_quote(customer, admin_user, expires_delta_days=-1)
        expire_pending_quotes()
        q1.refresh_from_db()
        q2.refresh_from_db()
        assert q1.quote_status == QuoteStatus.EXPIRED
        assert q2.quote_status == QuoteStatus.EXPIRED

    def test_no_toca_cotizaciones_ya_aceptadas(self, customer, admin_user):
        from apps.quotes.models import Quote, QuoteStatus
        quote = self._make_quote(customer, admin_user, expires_delta_days=-1)
        quote.quote_status = QuoteStatus.ACCEPTED
        quote.save(update_fields=["quote_status"])
        expire_pending_quotes()
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.ACCEPTED


@pytest.mark.django_db
class TestQuoteExpiresAt:
    def test_create_quote_fija_expires_at(self, customer, admin_user):
        from apps.quotes.models import QuoteStatus
        from apps.quotes.services import QuoteService
        order = Order.objects.create(
            customer=customer,
            request_type=RequestType.REFERENCE,
            title="Test expires_at",
            description="",
            quantity=1,
            priority="NORMAL",
            status=OrderStatus.RECEIVED,
        )
        quote = QuoteService.create_quote(
            order=order,
            weight_grams=__import__("decimal").Decimal("100.00"),
            print_time_hours=__import__("decimal").Decimal("5.00"),
            shipping_cost=__import__("decimal").Decimal("0.00"),
            created_by=admin_user,
        )
        assert quote.expires_at is not None
        diff = quote.expires_at - timezone.now()
        # Debe expirar en ~7 días (tolerancia de 5 minutos)
        assert timedelta(days=6, hours=23, minutes=55) < diff < timedelta(days=7, minutes=1)
