"""
Tests de los endpoints de la app production.

Endpoints cubiertos:
  GET  /api/v1/orders/{order_id}/production-history/
  GET  /api/v1/orders/{order_id}/events/
  GET  /api/v1/orders/{order_id}/events/{event_id}/
  PUT  /api/v1/admin/orders/{order_id}/status/
  PUT  /api/v1/admin/orders/{order_id}/cancel/
"""
import pytest

from apps.authentication.models import User
from apps.orders.models import (
    EventType,
    Order,
    OrderEvent,
    OrderPaymentStatus,
    OrderStatus,
    RequestType,
)
from apps.production.models import ProductionHistory


# --- URL helpers ---

def history_url(order_id):
    return f"/api/v1/orders/{order_id}/production-history/"

def events_url(order_id):
    return f"/api/v1/orders/{order_id}/events/"

def event_detail_url(order_id, event_id):
    return f"/api/v1/orders/{order_id}/events/{event_id}/"

def admin_status_url(order_id):
    return f"/api/v1/admin/orders/{order_id}/status/"

def admin_cancel_url(order_id):
    return f"/api/v1/admin/orders/{order_id}/cancel/"


# --- Helpers de datos ---

def _make_order(customer, status=OrderStatus.RECEIVED) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido Vistas",
        description="Para views",
        quantity=1,
        priority="NORMAL",
        status=status,
    )


def _make_history(order, admin_user) -> ProductionHistory:
    return ProductionHistory.objects.create(
        order=order,
        previous_status=OrderStatus.RECEIVED,
        new_status=OrderStatus.QUOTED,
        changed_by=admin_user,
    )


def _make_event(order, user) -> OrderEvent:
    return OrderEvent.objects.create(
        order=order,
        event_type=EventType.STATUS_CHANGED,
        event_description="Evento de prueba",
        created_by=user,
    )


# --- GET /api/v1/orders/{order_id}/production-history/ ---

@pytest.mark.django_db
class TestProductionHistoryListView:
    def test_unauthenticated_returns_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.get(history_url(order.id))
        assert resp.status_code == 401

    def test_foreign_user_returns_403(self, api_client, customer):
        other_user = User.objects.create_user(phone="+529611099901", first_name="Otro")
        order = _make_order(other_user)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(history_url(order.id))
        assert resp.status_code == 403

    def test_nonexistent_order_returns_404(self, auth_client):
        import uuid
        resp = auth_client.get(history_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_owner_sees_history(self, auth_client, admin_user, customer):
        order = _make_order(customer)
        _make_history(order, admin_user)
        resp = auth_client.get(history_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_admin_sees_any_order_history(self, admin_client, admin_user, customer):
        order = _make_order(customer)
        _make_history(order, admin_user)
        resp = admin_client.get(history_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_empty_history_returns_zero_count(self, auth_client, customer):
        order = _make_order(customer)
        resp = auth_client.get(history_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 0


# --- GET /api/v1/orders/{order_id}/events/ ---

@pytest.mark.django_db
class TestOrderEventListView:
    def test_unauthenticated_returns_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.get(events_url(order.id))
        assert resp.status_code == 401

    def test_foreign_user_returns_403(self, api_client, customer):
        other_user = User.objects.create_user(phone="+529611099902", first_name="Otro")
        order = _make_order(other_user)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(events_url(order.id))
        assert resp.status_code == 403

    def test_nonexistent_order_returns_404(self, auth_client):
        import uuid
        resp = auth_client.get(events_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_owner_sees_own_events(self, auth_client, admin_user, customer):
        order = _make_order(customer)
        _make_event(order, admin_user)
        _make_event(order, admin_user)
        resp = auth_client.get(events_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 2

    def test_admin_sees_any_order_events(self, admin_client, admin_user, customer):
        order = _make_order(customer)
        _make_event(order, admin_user)
        resp = admin_client.get(events_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1


# --- GET /api/v1/orders/{order_id}/events/{event_id}/ ---

@pytest.mark.django_db
class TestOrderEventDetailView:
    def test_unauthenticated_returns_401(self, api_client, customer, admin_user):
        order = _make_order(customer)
        event = _make_event(order, admin_user)
        resp = api_client.get(event_detail_url(order.id, event.id))
        assert resp.status_code == 401

    def test_foreign_user_returns_403(self, api_client, customer, admin_user):
        other_user = User.objects.create_user(phone="+529611099903", first_name="Otro")
        order = _make_order(other_user)
        event = _make_event(order, admin_user)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(event_detail_url(order.id, event.id))
        assert resp.status_code == 403

    def test_nonexistent_event_returns_404(self, auth_client, customer):
        import uuid
        order = _make_order(customer)
        resp = auth_client.get(event_detail_url(order.id, uuid.uuid4()))
        assert resp.status_code == 404

    def test_nonexistent_order_returns_404(self, auth_client):
        import uuid
        resp = auth_client.get(event_detail_url(uuid.uuid4(), uuid.uuid4()))
        assert resp.status_code == 404

    def test_owner_sees_event(self, auth_client, admin_user, customer):
        order = _make_order(customer)
        event = _make_event(order, admin_user)
        resp = auth_client.get(event_detail_url(order.id, event.id))
        assert resp.status_code == 200
        assert str(event.id) in str(resp.data["data"]["id"])

    def test_admin_sees_any_order_event(self, admin_client, admin_user, customer):
        order = _make_order(customer)
        event = _make_event(order, admin_user)
        resp = admin_client.get(event_detail_url(order.id, event.id))
        assert resp.status_code == 200


# --- PUT /api/v1/admin/orders/{order_id}/status/ ---

@pytest.mark.django_db
class TestAdminUpdateOrderStatusView:
    def test_unauthenticated_returns_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.put(admin_status_url(order.id), {"status": "QUOTED"}, format="json")
        assert resp.status_code == 401

    def test_customer_returns_403(self, auth_client, customer):
        order = _make_order(customer)
        resp = auth_client.put(admin_status_url(order.id), {"status": "QUOTED"}, format="json")
        assert resp.status_code == 403

    def test_missing_status_field_returns_400(self, admin_client, customer):
        order = _make_order(customer)
        resp = admin_client.put(admin_status_url(order.id), {}, format="json")
        assert resp.status_code == 400

    def test_invalid_transition_returns_400(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        resp = admin_client.put(
            admin_status_url(order.id),
            {"status": "PRINTING"},
            format="json",
        )
        assert resp.status_code == 400

    def test_nonexistent_order_returns_404(self, admin_client):
        import uuid
        resp = admin_client.put(
            admin_status_url(uuid.uuid4()),
            {"status": "QUOTED"},
            format="json",
        )
        assert resp.status_code == 404

    def test_admin_updates_status_successfully(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        resp = admin_client.put(
            admin_status_url(order.id),
            {"status": "QUOTED"},
            format="json",
        )
        assert resp.status_code == 200
        order.refresh_from_db()
        assert order.status == OrderStatus.QUOTED

    def test_admin_updates_status_with_notes(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        resp = admin_client.put(
            admin_status_url(order.id),
            {"status": "QUOTED", "notes": "Revisado manualmente"},
            format="json",
        )
        assert resp.status_code == 200
        history = ProductionHistory.objects.get(order=order, new_status=OrderStatus.QUOTED)
        assert history.notes == "Revisado manualmente"

    def test_delivered_without_full_payment_returns_400(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.READY)
        resp = admin_client.put(
            admin_status_url(order.id),
            {"status": "DELIVERED"},
            format="json",
        )
        assert resp.status_code == 400


# --- PUT /api/v1/admin/orders/{order_id}/cancel/ ---

@pytest.mark.django_db
class TestAdminCancelOrderView:
    def test_unauthenticated_returns_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.put(
            admin_cancel_url(order.id),
            {"reason": "x"},
            format="json",
        )
        assert resp.status_code == 401

    def test_customer_returns_403(self, auth_client, customer):
        order = _make_order(customer)
        resp = auth_client.put(
            admin_cancel_url(order.id),
            {"reason": "x"},
            format="json",
        )
        assert resp.status_code == 403

    def test_missing_reason_returns_400(self, admin_client, customer):
        order = _make_order(customer)
        resp = admin_client.put(admin_cancel_url(order.id), {}, format="json")
        assert resp.status_code == 400

    def test_non_cancelable_state_returns_400(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.PRINTING)
        resp = admin_client.put(
            admin_cancel_url(order.id),
            {"reason": "No se puede"},
            format="json",
        )
        assert resp.status_code == 400

    def test_nonexistent_order_returns_404(self, admin_client):
        import uuid
        resp = admin_client.put(
            admin_cancel_url(uuid.uuid4()),
            {"reason": "x"},
            format="json",
        )
        assert resp.status_code == 404

    def test_admin_cancels_successfully(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        resp = admin_client.put(
            admin_cancel_url(order.id),
            {"reason": "Cliente desistió"},
            format="json",
        )
        assert resp.status_code == 200
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        assert order.cancellation_reason == "Cliente desistió"
