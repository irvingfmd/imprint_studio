"""
Tests de servicios de la app production.
Casos del plan: 43 (PRINTING), 44 (POST_PROCESSING), 45 (READY),
                46 (DELIVERED), 47 (historial), 52-57 (eventos de estado).

Cubre la matriz completa de VALID_TRANSITIONS de OrderStatusTransitionService
y las reglas especiales del status-flow.md.
"""
import pytest

from apps.orders.models import (
    EventType,
    Order,
    OrderEvent,
    OrderPaymentStatus,
    OrderStatus,
    RequestType,
)
from apps.production.models import ProductionHistory
from apps.production.services import OrderStatusTransitionService


def _make_order(customer, status=OrderStatus.RECEIVED, payment_status=OrderPaymentStatus.NO_PAYMENT) -> Order:
    order = Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido Producción",
        description="Test de transiciones",
        quantity=1,
        priority="NORMAL",
        status=status,
    )
    if payment_status != OrderPaymentStatus.NO_PAYMENT:
        order.payment_status = payment_status
        order.save(update_fields=["payment_status", "updated_at"])
    return order


# --- Transiciones válidas individuales ---

@pytest.mark.django_db
class TestValidTransitions:
    def test_received_a_quoted(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        OrderStatusTransitionService.transition(order, OrderStatus.QUOTED, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.QUOTED

    def test_pending_analysis_a_quoted(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.PENDING_ANALYSIS)
        OrderStatusTransitionService.transition(order, OrderStatus.QUOTED, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.QUOTED

    def test_quoted_a_approved_guarda_approved_at(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        OrderStatusTransitionService.transition(order, OrderStatus.APPROVED, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.APPROVED
        assert order.approved_at is not None

    def test_approved_a_pending_deposit(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.APPROVED)
        OrderStatusTransitionService.transition(order, OrderStatus.PENDING_DEPOSIT, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_DEPOSIT

    def test_approved_a_fully_paid(self, customer, admin_user):
        # Flujo pago completo: APPROVED → FULLY_PAID
        order = _make_order(customer, status=OrderStatus.APPROVED)
        OrderStatusTransitionService.transition(order, OrderStatus.FULLY_PAID, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.FULLY_PAID

    def test_pending_deposit_a_deposit_paid(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.PENDING_DEPOSIT)
        OrderStatusTransitionService.transition(order, OrderStatus.DEPOSIT_PAID, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.DEPOSIT_PAID

    def test_deposit_paid_a_printing(self, customer, admin_user):
        """Caso 43: PRINTING."""
        order = _make_order(customer, status=OrderStatus.DEPOSIT_PAID)
        OrderStatusTransitionService.transition(order, OrderStatus.PRINTING, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.PRINTING

    def test_printing_a_post_processing(self, customer, admin_user):
        """Caso 44: POST_PROCESSING."""
        order = _make_order(customer, status=OrderStatus.PRINTING)
        OrderStatusTransitionService.transition(order, OrderStatus.POST_PROCESSING, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.POST_PROCESSING

    def test_post_processing_a_ready_guarda_ready_at(self, customer, admin_user):
        """Caso 45: READY."""
        order = _make_order(customer, status=OrderStatus.POST_PROCESSING)
        OrderStatusTransitionService.transition(order, OrderStatus.READY, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.READY
        assert order.ready_at is not None

    def test_ready_a_pending_balance(self, customer, admin_user):
        order = _make_order(
            customer,
            status=OrderStatus.READY,
            payment_status=OrderPaymentStatus.DEPOSIT_PAID,
        )
        OrderStatusTransitionService.transition(order, OrderStatus.PENDING_BALANCE, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING_BALANCE

    def test_pending_balance_a_fully_paid(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.PENDING_BALANCE)
        OrderStatusTransitionService.transition(order, OrderStatus.FULLY_PAID, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.FULLY_PAID

    def test_fully_paid_a_delivered_guarda_delivered_at(self, customer, admin_user):
        """Caso 46: DELIVERED — requiere payment_status = FULLY_PAID."""
        order = _make_order(
            customer,
            status=OrderStatus.FULLY_PAID,
            payment_status=OrderPaymentStatus.FULLY_PAID,
        )
        OrderStatusTransitionService.transition(order, OrderStatus.DELIVERED, admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.DELIVERED
        assert order.delivered_at is not None


# --- Registros de auditoría ---

@pytest.mark.django_db
class TestTransitionAuditRecords:
    def test_crea_production_history(self, customer, admin_user):
        """Caso 47: registro en production_history."""
        order = _make_order(customer, status=OrderStatus.DEPOSIT_PAID)
        OrderStatusTransitionService.transition(order, OrderStatus.PRINTING, admin_user)
        history = ProductionHistory.objects.filter(order=order, new_status=OrderStatus.PRINTING)
        assert history.exists()

    def test_history_almacena_previous_status(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        OrderStatusTransitionService.transition(order, OrderStatus.QUOTED, admin_user)
        history = ProductionHistory.objects.get(order=order, new_status=OrderStatus.QUOTED)
        assert history.previous_status == OrderStatus.RECEIVED

    def test_history_almacena_changed_by(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        OrderStatusTransitionService.transition(order, OrderStatus.QUOTED, admin_user)
        history = ProductionHistory.objects.get(order=order, new_status=OrderStatus.QUOTED)
        assert history.changed_by == admin_user

    def test_history_almacena_notes(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        OrderStatusTransitionService.transition(
            order, OrderStatus.QUOTED, admin_user, notes="Revisado"
        )
        history = ProductionHistory.objects.get(order=order, new_status=OrderStatus.QUOTED)
        assert history.notes == "Revisado"

    def test_crea_evento_status_changed(self, customer, admin_user):
        """Caso 52+: evento STATUS_CHANGED generado."""
        order = _make_order(customer, status=OrderStatus.PRINTING)
        OrderStatusTransitionService.transition(order, OrderStatus.POST_PROCESSING, admin_user)
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.STATUS_CHANGED,
        ).exists()

    def test_evento_contiene_previous_y_new_status(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        OrderStatusTransitionService.transition(order, OrderStatus.QUOTED, admin_user)
        event = OrderEvent.objects.filter(
            order=order,
            event_type=EventType.STATUS_CHANGED,
        ).latest("created_at")
        assert event.metadata["previous_status"] == OrderStatus.RECEIVED
        assert event.metadata["new_status"] == OrderStatus.QUOTED


# --- Transiciones inválidas ---

@pytest.mark.django_db
class TestInvalidTransitions:
    def test_received_a_printing_lanza_error(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        with pytest.raises(ValueError, match="Transición inválida"):
            OrderStatusTransitionService.transition(order, OrderStatus.PRINTING, admin_user)

    def test_quoted_a_pending_deposit_sin_approved_lanza_error(self, customer, admin_user):
        # QUOTED → PENDING_DEPOSIT está prohibido; debe pasar por APPROVED
        order = _make_order(customer, status=OrderStatus.QUOTED)
        with pytest.raises(ValueError, match="Transición inválida"):
            OrderStatusTransitionService.transition(order, OrderStatus.PENDING_DEPOSIT, admin_user)

    def test_delivered_a_cualquier_estado_lanza_error(self, customer, admin_user):
        # DELIVERED es estado final
        order = _make_order(
            customer,
            status=OrderStatus.DELIVERED,
            payment_status=OrderPaymentStatus.FULLY_PAID,
        )
        with pytest.raises(ValueError, match="Transición inválida"):
            OrderStatusTransitionService.transition(order, OrderStatus.PRINTING, admin_user)

    def test_cancelled_a_cualquier_estado_lanza_error(self, customer, admin_user):
        # CANCELLED es estado final
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        with pytest.raises(ValueError, match="Transición inválida"):
            OrderStatusTransitionService.transition(order, OrderStatus.RECEIVED, admin_user)

    def test_ready_a_delivered_sin_pago_completo_lanza_error(self, customer, admin_user):
        # READY → DELIVERED solo si payment_status = FULLY_PAID
        order = _make_order(
            customer,
            status=OrderStatus.READY,
            payment_status=OrderPaymentStatus.DEPOSIT_PAID,
        )
        with pytest.raises(ValueError, match="completamente pagado"):
            OrderStatusTransitionService.transition(order, OrderStatus.DELIVERED, admin_user)

    def test_deposit_paid_a_delivered_lanza_error(self, customer, admin_user):
        order = _make_order(
            customer,
            status=OrderStatus.DEPOSIT_PAID,
            payment_status=OrderPaymentStatus.FULLY_PAID,
        )
        with pytest.raises(ValueError, match="Transición inválida"):
            OrderStatusTransitionService.transition(order, OrderStatus.DELIVERED, admin_user)

    def test_printing_a_fully_paid_lanza_error(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.PRINTING)
        with pytest.raises(ValueError, match="Transición inválida"):
            OrderStatusTransitionService.transition(order, OrderStatus.FULLY_PAID, admin_user)


# --- Cancelaciones ---

@pytest.mark.django_db
class TestCancelOrder:
    def test_cancela_desde_received(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="Desistió")
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED

    def test_cancela_desde_pending_analysis(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.PENDING_ANALYSIS)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="STL inválido")
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED

    def test_cancela_desde_quoted(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="Sin respuesta")
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED

    def test_cancela_desde_approved(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.APPROVED)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="Cliente canceló")
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED

    def test_cancela_desde_pending_deposit(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.PENDING_DEPOSIT)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="Vencimiento de plazo")
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED

    def test_no_cancela_desde_deposit_paid(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.DEPOSIT_PAID)
        with pytest.raises(ValueError, match="No se puede cancelar"):
            OrderStatusTransitionService.cancel_order(order, admin_user, reason="x")

    def test_no_cancela_desde_printing(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.PRINTING)
        with pytest.raises(ValueError, match="No se puede cancelar"):
            OrderStatusTransitionService.cancel_order(order, admin_user, reason="x")

    def test_no_cancela_desde_delivered(self, customer, admin_user):
        order = _make_order(
            customer,
            status=OrderStatus.DELIVERED,
            payment_status=OrderPaymentStatus.FULLY_PAID,
        )
        with pytest.raises(ValueError, match="No se puede cancelar"):
            OrderStatusTransitionService.cancel_order(order, admin_user, reason="x")

    def test_guarda_cancelled_at(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="Razón")
        order.refresh_from_db()
        assert order.cancelled_at is not None

    def test_guarda_cancellation_reason(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="Cliente cambió de opinión")
        order.refresh_from_db()
        assert order.cancellation_reason == "Cliente cambió de opinión"

    def test_crea_production_history(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="Cancelado")
        assert ProductionHistory.objects.filter(
            order=order,
            new_status=OrderStatus.CANCELLED,
        ).exists()

    def test_crea_evento_order_cancelled(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        OrderStatusTransitionService.cancel_order(order, admin_user, reason="Cancelado")
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.ORDER_CANCELLED,
        ).exists()
