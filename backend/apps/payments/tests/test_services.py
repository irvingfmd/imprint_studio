"""
Tests de servicios de la app payments.
Casos del plan: 32-42 (pagos, confirmación, rechazo, confirmación manual, reembolsos).
"""

from decimal import Decimal

import pytest

from apps.orders.models import (
    EventType,
    Order,
    OrderEvent,
    OrderPaymentStatus,
    OrderStatus,
    RequestType,
)
from apps.payments.models import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    PaymentType,
)
from apps.payments.services import PaymentService


def _make_order(customer, status=OrderStatus.PENDING_DEPOSIT) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Casco Mandaloriano",
        description="Escala 1:1",
        quantity=1,
        priority="NORMAL",
        status=status,
    )


def _make_payment(order, ptype=PaymentType.DEPOSIT, pstatus=PaymentStatus.PENDING) -> Payment:
    return Payment.objects.create(
        order=order,
        amount=Decimal("218.24"),
        payment_type=ptype,
        payment_method=PaymentMethod.BANK_TRANSFER,
        payment_status=pstatus,
    )


@pytest.mark.django_db
class TestUploadProof:
    def test_uploads_proof_to_pending_payment(self, customer):
        """Caso 32: comprobante almacenado."""
        order = _make_order(customer)
        payment = _make_payment(order)
        result = PaymentService.upload_proof(
            payment_id=str(payment.id),
            file_url="https://cdn.example.com/comprobante.pdf",
            user=customer,
        )
        result.refresh_from_db()
        assert result.proof_file_url == "https://cdn.example.com/comprobante.pdf"

    def test_creates_payment_proof_uploaded_event(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        PaymentService.upload_proof(
            payment_id=str(payment.id),
            file_url="https://cdn.example.com/comp.jpg",
            user=customer,
        )
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.PAYMENT_PROOF_UPLOADED,
        ).exists()

    def test_nonexistent_payment_raises_error(self):
        import uuid

        with pytest.raises(ValueError, match="no encontrado"):
            PaymentService.upload_proof(
                payment_id=str(uuid.uuid4()),
                file_url="https://cdn.example.com/x.pdf",
                user=None,
            )

    def test_already_confirmed_payment_raises_error(self, customer):
        order = _make_order(customer)
        payment = _make_payment(order, pstatus=PaymentStatus.CONFIRMED)
        with pytest.raises(ValueError, match="PENDING"):
            PaymentService.upload_proof(
                payment_id=str(payment.id),
                file_url="https://cdn.example.com/x.pdf",
                user=customer,
            )


@pytest.mark.django_db
class TestConfirmPayment:
    def test_confirms_deposit(self, customer, admin_user):
        """Caso 33: confirmar anticipo → DEPOSIT_PAID."""
        order = _make_order(customer)
        payment = _make_payment(order, ptype=PaymentType.DEPOSIT)
        PaymentService.confirm_payment(
            payment_id=str(payment.id),
            confirmed_by=admin_user,
        )
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.payment_status == PaymentStatus.CONFIRMED
        assert payment.confirmed_by == admin_user
        assert payment.confirmed_at is not None
        assert order.payment_status == OrderPaymentStatus.DEPOSIT_PAID

    def test_confirms_balance(self, customer, admin_user):
        """Caso 34: confirmar saldo → FULLY_PAID."""
        order = _make_order(customer, status=OrderStatus.PENDING_BALANCE)
        order.payment_status = OrderPaymentStatus.DEPOSIT_PAID
        order.save()
        payment = _make_payment(order, ptype=PaymentType.BALANCE)
        PaymentService.confirm_payment(
            payment_id=str(payment.id),
            confirmed_by=admin_user,
        )
        order.refresh_from_db()
        assert order.payment_status == OrderPaymentStatus.FULLY_PAID

    def test_confirms_full_payment(self, customer, admin_user):
        """Confirmar pago completo → FULLY_PAID."""
        order = _make_order(customer)
        payment = _make_payment(order, ptype=PaymentType.FULL_PAYMENT)
        PaymentService.confirm_payment(
            payment_id=str(payment.id),
            confirmed_by=admin_user,
        )
        order.refresh_from_db()
        assert order.payment_status == OrderPaymentStatus.FULLY_PAID

    def test_saves_notes_on_payment(self, customer, admin_user):
        order = _make_order(customer)
        payment = _make_payment(order)
        PaymentService.confirm_payment(
            payment_id=str(payment.id),
            confirmed_by=admin_user,
            notes="Verificado por transferencia SPEI",
        )
        payment.refresh_from_db()
        assert payment.notes == "Verificado por transferencia SPEI"

    def test_creates_deposit_confirmed_event(self, customer, admin_user):
        """Caso 37: evento de pago generado."""
        order = _make_order(customer)
        payment = _make_payment(order, ptype=PaymentType.DEPOSIT)
        PaymentService.confirm_payment(
            payment_id=str(payment.id),
            confirmed_by=admin_user,
        )
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.DEPOSIT_CONFIRMED,
        ).exists()

    def test_nonexistent_payment_raises_error(self, admin_user):
        import uuid

        with pytest.raises(ValueError, match="no encontrado"):
            PaymentService.confirm_payment(
                payment_id=str(uuid.uuid4()),
                confirmed_by=admin_user,
            )

    def test_already_confirmed_payment_raises_error(self, customer, admin_user):
        order = _make_order(customer)
        payment = _make_payment(order, pstatus=PaymentStatus.CONFIRMED)
        with pytest.raises(ValueError, match="PENDING"):
            PaymentService.confirm_payment(
                payment_id=str(payment.id),
                confirmed_by=admin_user,
            )


@pytest.mark.django_db
class TestRejectPayment:
    def test_rejects_pending_payment(self, customer, admin_user):
        """Caso 36: pago rechazado."""
        order = _make_order(customer)
        payment = _make_payment(order)
        PaymentService.reject_payment(
            payment_id=str(payment.id),
            confirmed_by=admin_user,
            reason="Comprobante ilegible",
        )
        payment.refresh_from_db()
        assert payment.payment_status == PaymentStatus.REJECTED
        assert payment.notes == "Comprobante ilegible"
        assert payment.confirmed_by == admin_user
        assert payment.confirmed_at is not None

    def test_creates_payment_rejected_event(self, customer, admin_user):
        order = _make_order(customer)
        payment = _make_payment(order)
        PaymentService.reject_payment(
            payment_id=str(payment.id),
            confirmed_by=admin_user,
            reason="Inválido",
        )
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.PAYMENT_REJECTED,
        ).exists()

    def test_nonexistent_payment_raises_error(self, admin_user):
        import uuid

        with pytest.raises(ValueError, match="no encontrado"):
            PaymentService.reject_payment(
                payment_id=str(uuid.uuid4()),
                confirmed_by=admin_user,
                reason="x",
            )

    def test_non_pending_payment_raises_error(self, customer, admin_user):
        order = _make_order(customer)
        payment = _make_payment(order, pstatus=PaymentStatus.REJECTED)
        with pytest.raises(ValueError, match="PENDING"):
            PaymentService.reject_payment(
                payment_id=str(payment.id),
                confirmed_by=admin_user,
                reason="Duplicado",
            )


@pytest.mark.django_db
class TestManualConfirmation:
    def test_creates_manually_confirmed_payment(self, customer, admin_user):
        """Caso 35: confirmación manual → manual_confirmation = True."""
        order = _make_order(customer)
        payment = PaymentService.create_manual_confirmation(
            order_id=str(order.id),
            payment_type=PaymentType.DEPOSIT,
            payment_method=PaymentMethod.BANK_TRANSFER,
            amount=Decimal("218.24"),
            notes="Cliente envió comprobante por WhatsApp",
            confirmed_by=admin_user,
        )
        assert payment.payment_status == PaymentStatus.CONFIRMED
        assert payment.manual_confirmation is True
        assert payment.confirmed_by == admin_user

    def test_updates_order_payment_status(self, customer, admin_user):
        order = _make_order(customer)
        PaymentService.create_manual_confirmation(
            order_id=str(order.id),
            payment_type=PaymentType.DEPOSIT,
            payment_method=PaymentMethod.BANK_TRANSFER,
            amount=Decimal("218.24"),
            notes="",
            confirmed_by=admin_user,
        )
        order.refresh_from_db()
        assert order.payment_status == OrderPaymentStatus.DEPOSIT_PAID

    def test_creates_payment_event(self, customer, admin_user):
        order = _make_order(customer)
        PaymentService.create_manual_confirmation(
            order_id=str(order.id),
            payment_type=PaymentType.DEPOSIT,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("100.00"),
            notes="",
            confirmed_by=admin_user,
        )
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.DEPOSIT_CONFIRMED,
        ).exists()

    def test_nonexistent_order_raises_error(self, admin_user):
        import uuid

        with pytest.raises(ValueError, match="no encontrado"):
            PaymentService.create_manual_confirmation(
                order_id=str(uuid.uuid4()),
                payment_type=PaymentType.DEPOSIT,
                payment_method=PaymentMethod.CASH,
                amount=Decimal("100.00"),
                notes="",
                confirmed_by=admin_user,
            )


@pytest.mark.django_db
class TestProcessRefund:
    def test_registers_refund(self, customer, admin_user):
        """Caso 41: crea registro de tipo REFUND."""
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        _make_payment(order, ptype=PaymentType.DEPOSIT, pstatus=PaymentStatus.CONFIRMED)
        payment = PaymentService.process_refund(
            order_id=str(order.id),
            amount=Decimal("218.24"),
            reason="Pedido cancelado antes de laminar",
            confirmed_by=admin_user,
        )
        assert payment.payment_type == PaymentType.REFUND
        assert payment.payment_status == PaymentStatus.CONFIRMED
        assert payment.manual_confirmation is True

    def test_updates_payment_status_to_refunded(self, customer, admin_user):
        """Caso 38-40: pedido queda en REFUNDED."""
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        _make_payment(order, ptype=PaymentType.DEPOSIT, pstatus=PaymentStatus.CONFIRMED)
        PaymentService.process_refund(
            order_id=str(order.id),
            amount=Decimal("150.00"),
            reason="Cancelación",
            confirmed_by=admin_user,
        )
        order.refresh_from_db()
        assert order.payment_status == OrderPaymentStatus.REFUNDED

    def test_creates_refund_processed_event(self, customer, admin_user):
        """Caso 42: evento REFUND_PROCESSED generado."""
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        _make_payment(order, ptype=PaymentType.DEPOSIT, pstatus=PaymentStatus.CONFIRMED)
        PaymentService.process_refund(
            order_id=str(order.id),
            amount=Decimal("218.24"),
            reason="Cancelación solicitada",
            confirmed_by=admin_user,
        )
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.REFUND_PROCESSED,
        ).exists()

    def test_metadata_includes_amount_and_reason(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        _make_payment(order, ptype=PaymentType.DEPOSIT, pstatus=PaymentStatus.CONFIRMED)
        PaymentService.process_refund(
            order_id=str(order.id),
            amount=Decimal("75.00"),
            reason="Falla de impresora",
            confirmed_by=admin_user,
        )
        event = OrderEvent.objects.get(order=order, event_type=EventType.REFUND_PROCESSED)
        assert event.metadata["amount"] == "75.00"
        assert "Falla de impresora" in event.metadata["reason"]

    def test_nonexistent_order_raises_error(self, admin_user):
        import uuid

        with pytest.raises(ValueError, match="no encontrado"):
            PaymentService.process_refund(
                order_id=str(uuid.uuid4()),
                amount=Decimal("100.00"),
                reason="x",
                confirmed_by=admin_user,
            )
