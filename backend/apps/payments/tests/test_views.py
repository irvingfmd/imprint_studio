"""
Tests de los endpoints de la app payments.
Casos del plan: 32-42, 58, 60, 61.

Endpoints cubiertos:
  GET  /api/v1/orders/{order_id}/payments/
  GET  /api/v1/payments/{payment_id}/
  POST /api/v1/payments/{payment_id}/proof/
  GET  /api/v1/admin/payments/
  PUT  /api/v1/admin/payments/{payment_id}/confirm/
  PUT  /api/v1/admin/payments/{payment_id}/reject/
  POST /api/v1/admin/orders/{order_id}/payments/manual-confirmation/
  POST /api/v1/admin/orders/{order_id}/refund/
"""

from decimal import Decimal

import pytest

from apps.orders.models import Order, OrderStatus, RequestType
from apps.payments.models import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    PaymentType,
)

# --- URL helpers ---


def order_payments_url(order_id):
    return f"/api/v1/orders/{order_id}/payments/"


def payment_url(payment_id):
    return f"/api/v1/payments/{payment_id}/"


def proof_url(payment_id):
    return f"/api/v1/payments/{payment_id}/proof/"


def admin_payments_url():
    return "/api/v1/admin/payments/"


def admin_confirm_url(payment_id):
    return f"/api/v1/admin/payments/{payment_id}/confirm/"


def admin_reject_url(payment_id):
    return f"/api/v1/admin/payments/{payment_id}/reject/"


def admin_manual_url(order_id):
    return f"/api/v1/admin/orders/{order_id}/payments/manual-confirmation/"


def admin_refund_url(order_id):
    return f"/api/v1/admin/orders/{order_id}/refund/"


# --- Helpers de datos ---


def _make_order(customer, status=OrderStatus.PENDING_DEPOSIT) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido Test",
        description="Para views",
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


# --- Lista de pagos de un pedido ---


@pytest.mark.django_db
class TestOrderPaymentListView:
    def test_unauthenticated_returns_401(self, api_client, customer):
        # Caso 58
        order = _make_order(customer)
        resp = api_client.get(order_payments_url(order.id))
        assert resp.status_code == 401

    def test_customer_sees_own_order_payments(self, auth_client, customer):
        order = _make_order(customer)
        _make_payment(order)
        resp = auth_client.get(order_payments_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_customer_cannot_see_foreign_order_payments(self, auth_client):
        # Caso 60
        from apps.authentication.models import User

        other_user = User.objects.create_user(phone="+529611099910", first_name="Otro")
        order = _make_order(other_user)
        _make_payment(order)
        resp = auth_client.get(order_payments_url(order.id))
        assert resp.status_code == 403

    def test_nonexistent_order_returns_404(self, auth_client):
        import uuid

        resp = auth_client.get(order_payments_url(uuid.uuid4()))
        assert resp.status_code == 404


# --- Detalle de pago ---


@pytest.mark.django_db
class TestPaymentDetailView:
    def test_unauthenticated_returns_401(self, api_client, customer):
        # Caso 58
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = api_client.get(payment_url(payment.id))
        assert resp.status_code == 401

    def test_owner_sees_own_payment(self, auth_client, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = auth_client.get(payment_url(payment.id))
        assert resp.status_code == 200
        assert str(payment.id) in str(resp.data["data"]["id"])

    def test_foreign_user_receives_403(self, api_client, customer):
        # Caso 60
        from apps.authentication.models import User

        other_user = User.objects.create_user(phone="+529611099911", first_name="Otro")
        order = _make_order(other_user)
        payment = _make_payment(order)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(payment_url(payment.id))
        assert resp.status_code == 403

    def test_nonexistent_payment_returns_404(self, auth_client):
        import uuid

        resp = auth_client.get(payment_url(uuid.uuid4()))
        assert resp.status_code == 404


# --- Subir comprobante ---


@pytest.mark.django_db
class TestPaymentProofView:
    def test_unauthenticated_returns_401(self, api_client, customer):
        # Caso 58
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = api_client.post(proof_url(payment.id), {"file_url": "https://x.com/a.pdf"})
        assert resp.status_code == 401

    def test_uploads_valid_proof(self, auth_client, customer, tmp_path, settings):
        """Caso 32: comprobante almacenado via multipart."""
        import io

        settings.MEDIA_ROOT = tmp_path
        order = _make_order(customer)
        payment = _make_payment(order)
        fake_file = io.BytesIO(b"fake image content")
        fake_file.name = "comprobante.jpg"
        resp = auth_client.post(
            proof_url(payment.id),
            {"file": fake_file},
            format="multipart",
        )
        assert resp.status_code == 200
        payment.refresh_from_db()
        assert payment.proof_file_url != ""

    def test_missing_file_returns_400(self, auth_client, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = auth_client.post(proof_url(payment.id), {}, format="multipart")
        assert resp.status_code == 400

    def test_invalid_extension_returns_400(self, auth_client, customer):
        import io

        order = _make_order(customer)
        payment = _make_payment(order)
        fake_file = io.BytesIO(b"<script>alert(1)</script>")
        fake_file.name = "malware.exe"
        resp = auth_client.post(
            proof_url(payment.id),
            {"file": fake_file},
            format="multipart",
        )
        assert resp.status_code == 400

    def test_archivo_mayor_a_10mb_devuelve_400(self, auth_client, customer, tmp_path, settings):
        import io

        settings.MEDIA_ROOT = tmp_path
        order = _make_order(customer)
        payment = _make_payment(order)
        # Archivo de 11 MB > límite de 10 MB
        fake_file = io.BytesIO(b"x" * (11 * 1024 * 1024))
        fake_file.name = "grande.jpg"
        resp = auth_client.post(
            proof_url(payment.id),
            {"file": fake_file},
            format="multipart",
        )
        assert resp.status_code == 400
        assert "10 MB" in resp.data["message"]

    def test_foreign_user_receives_403(self, api_client, customer):
        # Caso 60
        import io

        from apps.authentication.models import User

        other_user = User.objects.create_user(phone="+529611099912", first_name="Otro")
        order = _make_order(other_user)
        payment = _make_payment(order)
        api_client.force_authenticate(user=customer)
        fake_file = io.BytesIO(b"data")
        fake_file.name = "a.jpg"
        resp = api_client.post(
            proof_url(payment.id),
            {"file": fake_file},
            format="multipart",
        )
        assert resp.status_code == 403


# --- Admin: lista de pagos ---


@pytest.mark.django_db
class TestAdminPaymentListView:
    def test_admin_sees_all_payments(self, admin_client, customer):
        order = _make_order(customer)
        _make_payment(order)
        _make_payment(order, pstatus=PaymentStatus.CONFIRMED)
        resp = admin_client.get(admin_payments_url())
        assert resp.status_code == 200
        assert resp.data["data"]["count"] >= 2

    def test_customer_at_admin_endpoint_returns_403(self, auth_client):
        # Caso 61
        resp = auth_client.get(admin_payments_url())
        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, api_client):
        # Caso 58
        resp = api_client.get(admin_payments_url())
        assert resp.status_code == 401

    def test_respuesta_incluye_num_pages(self, admin_client, customer):
        order = _make_order(customer)
        _make_payment(order)
        resp = admin_client.get(admin_payments_url())
        assert resp.status_code == 200
        assert "num_pages" in resp.data["data"]

    def test_page_size_limita_resultados(self, admin_client, customer):
        order = _make_order(customer)
        _make_payment(order)
        _make_payment(order)
        resp = admin_client.get(admin_payments_url() + "?page_size=1")
        assert resp.status_code == 200
        assert len(resp.data["data"]["results"]) == 1

    def test_page_size_invalido_devuelve_400(self, admin_client):
        resp = admin_client.get(admin_payments_url() + "?page_size=xyz")
        assert resp.status_code == 400

    def test_payment_status_filter(self, admin_client, customer):
        order = _make_order(customer)
        _make_payment(order, pstatus=PaymentStatus.PENDING)
        _make_payment(order, pstatus=PaymentStatus.CONFIRMED)
        resp = admin_client.get(admin_payments_url() + "?payment_status=PENDING")
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1


# --- Admin: confirmar pago ---


@pytest.mark.django_db
class TestAdminConfirmPaymentView:
    def test_admin_confirms_payment(self, admin_client, customer):
        """Caso 33: confirmar anticipo."""
        order = _make_order(customer)
        payment = _make_payment(order, ptype=PaymentType.DEPOSIT)
        resp = admin_client.put(
            admin_confirm_url(payment.id),
            {"notes": "Verificado"},
            format="json",
        )
        assert resp.status_code == 200
        payment.refresh_from_db()
        assert payment.payment_status == PaymentStatus.CONFIRMED

    def test_customer_at_admin_endpoint_returns_403(self, auth_client, customer):
        # Caso 61
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = auth_client.put(admin_confirm_url(payment.id), {}, format="json")
        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, api_client, customer):
        # Caso 58
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = api_client.put(admin_confirm_url(payment.id), {})
        assert resp.status_code == 401

    def test_already_confirmed_payment_returns_400(self, admin_client, customer):
        order = _make_order(customer)
        payment = _make_payment(order, pstatus=PaymentStatus.CONFIRMED)
        resp = admin_client.put(admin_confirm_url(payment.id), {}, format="json")
        assert resp.status_code == 400


# --- Admin: rechazar pago ---


@pytest.mark.django_db
class TestAdminRejectPaymentView:
    def test_admin_rejects_payment(self, admin_client, customer):
        """Caso 36: pago rechazado."""
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = admin_client.put(
            admin_reject_url(payment.id),
            {"reason": "Comprobante inválido"},
            format="json",
        )
        assert resp.status_code == 200
        payment.refresh_from_db()
        assert payment.payment_status == PaymentStatus.REJECTED

    def test_missing_reason_returns_400(self, admin_client, customer):
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = admin_client.put(admin_reject_url(payment.id), {}, format="json")
        assert resp.status_code == 400

    def test_customer_at_admin_endpoint_returns_403(self, auth_client, customer):
        # Caso 61
        order = _make_order(customer)
        payment = _make_payment(order)
        resp = auth_client.put(
            admin_reject_url(payment.id),
            {"reason": "x"},
            format="json",
        )
        assert resp.status_code == 403

    def test_nonexistent_payment_returns_400(self, admin_client):
        import uuid

        resp = admin_client.put(
            admin_reject_url(uuid.uuid4()),
            {"reason": "Prueba"},
            format="json",
        )
        assert resp.status_code == 400


# --- Admin: confirmación manual ---


@pytest.mark.django_db
class TestAdminManualConfirmationView:
    def test_admin_registers_manual_payment(self, admin_client, customer):
        """Caso 35: confirmación manual."""
        order = _make_order(customer)
        resp = admin_client.post(
            admin_manual_url(order.id),
            {
                "payment_type": "DEPOSIT",
                "payment_method": "BANK_TRANSFER",
                "amount": "218.24",
                "notes": "Cliente envió foto por WhatsApp",
            },
            format="json",
        )
        assert resp.status_code == 201
        payment = Payment.objects.filter(order=order, manual_confirmation=True).first()
        assert payment is not None
        assert payment.payment_status == PaymentStatus.CONFIRMED

    def test_invalid_fields_return_400(self, admin_client, customer):
        order = _make_order(customer)
        resp = admin_client.post(
            admin_manual_url(order.id),
            {"payment_type": "DEPOSIT", "payment_method": "BANK_TRANSFER", "amount": "0.00"},
            format="json",
        )
        assert resp.status_code == 400

    def test_customer_at_admin_endpoint_returns_403(self, auth_client, customer):
        # Caso 61
        order = _make_order(customer)
        resp = auth_client.post(
            admin_manual_url(order.id),
            {"payment_type": "DEPOSIT", "payment_method": "CASH", "amount": "100.00"},
            format="json",
        )
        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, api_client, customer):
        # Caso 58
        order = _make_order(customer)
        resp = api_client.post(admin_manual_url(order.id), {})
        assert resp.status_code == 401


# --- Admin: reembolso ---


@pytest.mark.django_db
class TestAdminRefundView:
    def test_admin_registers_refund(self, admin_client, customer):
        """Casos 38-42: registrar reembolso."""
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        _make_payment(order, ptype=PaymentType.DEPOSIT, pstatus=PaymentStatus.CONFIRMED)
        resp = admin_client.post(
            admin_refund_url(order.id),
            {"amount": "218.24", "reason": "Pedido cancelado antes de laminar"},
            format="json",
        )
        assert resp.status_code == 201
        payment = Payment.objects.filter(order=order, payment_type=PaymentType.REFUND).first()
        assert payment is not None

    def test_missing_reason_returns_400(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        resp = admin_client.post(
            admin_refund_url(order.id),
            {"amount": "100.00"},
            format="json",
        )
        assert resp.status_code == 400

    def test_zero_amount_returns_400(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        resp = admin_client.post(
            admin_refund_url(order.id),
            {"amount": "0.00", "reason": "x"},
            format="json",
        )
        assert resp.status_code == 400

    def test_customer_at_admin_endpoint_returns_403(self, auth_client, customer):
        # Caso 61
        order = _make_order(customer, status=OrderStatus.CANCELLED)
        resp = auth_client.post(
            admin_refund_url(order.id),
            {"amount": "100.00", "reason": "x"},
            format="json",
        )
        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, api_client, customer):
        # Caso 58
        order = _make_order(customer)
        resp = api_client.post(admin_refund_url(order.id), {})
        assert resp.status_code == 401
