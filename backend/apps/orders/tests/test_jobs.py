"""
Tests del scheduler de cancelación automática de anticipos vencidos.
Fuente: docs/appendices/status-flow.md — Cancelación Automática por Vencimiento de Anticipo.
"""
from decimal import Decimal

import pytest
from datetime import timedelta

from django.utils import timezone

from apps.configuration.models import BusinessConfig
from apps.orders.jobs import cancel_expired_deposits
from apps.orders.models import Order, OrderStatus, RequestType
from apps.production.models import ProductionHistory


@pytest.fixture(autouse=True)
def business_config(db):
    """BusinessConfig mínima necesaria para que el job funcione."""
    return BusinessConfig.objects.create(
        material_cost_per_kg=Decimal("250.00"),
        energy_cost_per_hour=Decimal("10.00"),
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
    ph = ProductionHistory.objects.create(
        order=order,
        previous_status=OrderStatus.APPROVED,
        new_status=OrderStatus.PENDING_DEPOSIT,
        changed_by=admin_user,
    )
    ProductionHistory.objects.filter(pk=ph.pk).update(
        changed_at=timezone.now() - timedelta(hours=hours_ago)
    )


@pytest.mark.django_db
class TestCancelExpiredDeposits:
    def test_cancela_pedido_vencido(self, customer, admin_user):
        """Pedido en PENDING_DEPOSIT >72h debe ser cancelado automáticamente."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=73)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        assert "automática" in order.cancellation_reason

    def test_cancellation_reason_menciona_horas(self, customer, admin_user):
        """La razón de cancelación menciona el plazo en horas."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=73)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert "72" in order.cancellation_reason

    def test_no_cancela_pedido_dentro_del_plazo(self, customer, admin_user):
        """Pedido en PENDING_DEPOSIT <72h NO debe ser cancelado."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=24)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT

    def test_no_cancela_pedido_justo_en_el_limite(self, customer, admin_user):
        """71h 59m no supera el plazo de 72h."""
        order = _make_pending_deposit_order(customer)
        # 71 horas y 59 minutos — menor que el deadline de 72h
        ph = ProductionHistory.objects.create(
            order=order,
            previous_status=OrderStatus.APPROVED,
            new_status=OrderStatus.PENDING_DEPOSIT,
            changed_by=admin_user,
        )
        ProductionHistory.objects.filter(pk=ph.pk).update(
            changed_at=timezone.now() - timedelta(hours=71, minutes=59)
        )

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT

    def test_ignora_pedidos_en_otros_estados(self, customer, admin_user):
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

    def test_cancela_multiples_pedidos_vencidos(self, customer, admin_user):
        """Cancela múltiples pedidos vencidos en una sola ejecución."""
        order1 = _make_pending_deposit_order(customer)
        order2 = _make_pending_deposit_order(customer)
        _register_transition(order1, admin_user, hours_ago=80)
        _register_transition(order2, admin_user, hours_ago=100)

        cancel_expired_deposits()

        order1.refresh_from_db()
        order2.refresh_from_db()
        assert order1.status == OrderStatus.CANCELLED
        assert order2.status == OrderStatus.CANCELLED

    def test_cancela_vencido_respeta_vigente(self, customer, admin_user):
        """Solo cancela los vencidos, no los que están dentro del plazo."""
        vencido = _make_pending_deposit_order(customer)
        vigente = _make_pending_deposit_order(customer)
        _register_transition(vencido, admin_user, hours_ago=80)
        _register_transition(vigente, admin_user, hours_ago=10)

        cancel_expired_deposits()

        vencido.refresh_from_db()
        vigente.refresh_from_db()
        assert vencido.status == OrderStatus.CANCELLED
        assert vigente.status == OrderStatus.PENDING_DEPOSIT

    def test_usa_deposit_deadline_hours_de_config(self, customer, admin_user, business_config):
        """Respeta el valor configurable de BusinessConfig.deposit_deadline_hours."""
        business_config.deposit_deadline_hours = 24
        business_config.save()

        vencido = _make_pending_deposit_order(customer)
        vigente = _make_pending_deposit_order(customer)
        _register_transition(vencido, admin_user, hours_ago=25)
        _register_transition(vigente, admin_user, hours_ago=23)

        cancel_expired_deposits()

        vencido.refresh_from_db()
        vigente.refresh_from_db()
        assert vencido.status == OrderStatus.CANCELLED
        assert vigente.status == OrderStatus.PENDING_DEPOSIT

    def test_crea_production_history_con_changed_by_none(self, customer, admin_user):
        """La cancelación automática registra ProductionHistory con changed_by=None."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=73)

        cancel_expired_deposits()

        history = ProductionHistory.objects.get(
            order=order,
            new_status=OrderStatus.CANCELLED,
        )
        assert history.changed_by is None

    def test_no_cancela_pedido_eliminado(self, customer, admin_user):
        """No toca pedidos con is_deleted=True."""
        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=80)
        Order.objects.filter(pk=order.pk).update(is_deleted=True)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT

    def test_sin_config_activa_no_cancela(self, customer, admin_user, business_config):
        """Si no hay BusinessConfig activa, el job no cancela nada."""
        business_config.is_active = False
        business_config.save()

        order = _make_pending_deposit_order(customer)
        _register_transition(order, admin_user, hours_ago=80)

        cancel_expired_deposits()

        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT
