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
    def test_sin_token_devuelve_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.get(history_url(order.id))
        assert resp.status_code == 401

    def test_cliente_ajeno_devuelve_403(self, api_client, customer):
        otro = User.objects.create_user(phone="+529611099901", first_name="Otro")
        order = _make_order(otro)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(history_url(order.id))
        assert resp.status_code == 403

    def test_pedido_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(history_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_propietario_ve_historial(self, auth_client, admin_user, customer):
        order = _make_order(customer)
        _make_history(order, admin_user)
        resp = auth_client.get(history_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_admin_ve_historial_de_cualquier_pedido(self, admin_client, admin_user, customer):
        order = _make_order(customer)
        _make_history(order, admin_user)
        resp = admin_client.get(history_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_historial_vacio_retorna_count_cero(self, auth_client, customer):
        order = _make_order(customer)
        resp = auth_client.get(history_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 0


# --- GET /api/v1/orders/{order_id}/events/ ---

@pytest.mark.django_db
class TestOrderEventListView:
    def test_sin_token_devuelve_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.get(events_url(order.id))
        assert resp.status_code == 401

    def test_cliente_ajeno_devuelve_403(self, api_client, customer):
        otro = User.objects.create_user(phone="+529611099902", first_name="Otro")
        order = _make_order(otro)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(events_url(order.id))
        assert resp.status_code == 403

    def test_pedido_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(events_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_propietario_ve_sus_eventos(self, auth_client, admin_user, customer):
        order = _make_order(customer)
        _make_event(order, admin_user)
        _make_event(order, admin_user)
        resp = auth_client.get(events_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 2

    def test_admin_ve_eventos_de_cualquier_pedido(self, admin_client, admin_user, customer):
        order = _make_order(customer)
        _make_event(order, admin_user)
        resp = admin_client.get(events_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1


# --- GET /api/v1/orders/{order_id}/events/{event_id}/ ---

@pytest.mark.django_db
class TestOrderEventDetailView:
    def test_sin_token_devuelve_401(self, api_client, customer, admin_user):
        order = _make_order(customer)
        event = _make_event(order, admin_user)
        resp = api_client.get(event_detail_url(order.id, event.id))
        assert resp.status_code == 401

    def test_cliente_ajeno_devuelve_403(self, api_client, customer, admin_user):
        otro = User.objects.create_user(phone="+529611099903", first_name="Otro")
        order = _make_order(otro)
        event = _make_event(order, admin_user)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(event_detail_url(order.id, event.id))
        assert resp.status_code == 403

    def test_evento_inexistente_devuelve_404(self, auth_client, customer):
        import uuid
        order = _make_order(customer)
        resp = auth_client.get(event_detail_url(order.id, uuid.uuid4()))
        assert resp.status_code == 404

    def test_pedido_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(event_detail_url(uuid.uuid4(), uuid.uuid4()))
        assert resp.status_code == 404

    def test_propietario_ve_evento(self, auth_client, admin_user, customer):
        order = _make_order(customer)
        event = _make_event(order, admin_user)
        resp = auth_client.get(event_detail_url(order.id, event.id))
        assert resp.status_code == 200
        assert str(event.id) in str(resp.data["data"]["id"])

    def test_admin_ve_evento_de_cualquier_pedido(self, admin_client, admin_user, customer):
        order = _make_order(customer)
        event = _make_event(order, admin_user)
        resp = admin_client.get(event_detail_url(order.id, event.id))
        assert resp.status_code == 200


# --- PUT /api/v1/admin/orders/{order_id}/status/ ---

@pytest.mark.django_db
class TestAdminUpdateOrderStatusView:
    def test_sin_token_devuelve_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.put(admin_status_url(order.id), {"status": "QUOTED"}, format="json")
        assert resp.status_code == 401

    def test_cliente_devuelve_403(self, auth_client, customer):
        order = _make_order(customer)
        resp = auth_client.put(admin_status_url(order.id), {"status": "QUOTED"}, format="json")
        assert resp.status_code == 403

    def test_sin_campo_status_devuelve_400(self, admin_client, customer):
        order = _make_order(customer)
        resp = admin_client.put(admin_status_url(order.id), {}, format="json")
        assert resp.status_code == 400

    def test_transicion_invalida_devuelve_400(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        resp = admin_client.put(
            admin_status_url(order.id),
            {"status": "PRINTING"},
            format="json",
        )
        assert resp.status_code == 400

    def test_pedido_inexistente_devuelve_404(self, admin_client):
        import uuid
        resp = admin_client.put(
            admin_status_url(uuid.uuid4()),
            {"status": "QUOTED"},
            format="json",
        )
        assert resp.status_code == 404

    def test_admin_actualiza_estado_exitosamente(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        resp = admin_client.put(
            admin_status_url(order.id),
            {"status": "QUOTED"},
            format="json",
        )
        assert resp.status_code == 200
        order.refresh_from_db()
        assert order.status == OrderStatus.QUOTED

    def test_admin_actualiza_estado_con_notes(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.RECEIVED)
        resp = admin_client.put(
            admin_status_url(order.id),
            {"status": "QUOTED", "notes": "Revisado manualmente"},
            format="json",
        )
        assert resp.status_code == 200
        history = ProductionHistory.objects.get(order=order, new_status=OrderStatus.QUOTED)
        assert history.notes == "Revisado manualmente"

    def test_delivered_sin_pago_completo_devuelve_400(self, admin_client, customer):
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
    def test_sin_token_devuelve_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.put(
            admin_cancel_url(order.id),
            {"reason": "x"},
            format="json",
        )
        assert resp.status_code == 401

    def test_cliente_devuelve_403(self, auth_client, customer):
        order = _make_order(customer)
        resp = auth_client.put(
            admin_cancel_url(order.id),
            {"reason": "x"},
            format="json",
        )
        assert resp.status_code == 403

    def test_sin_reason_devuelve_400(self, admin_client, customer):
        order = _make_order(customer)
        resp = admin_client.put(admin_cancel_url(order.id), {}, format="json")
        assert resp.status_code == 400

    def test_estado_no_cancelable_devuelve_400(self, admin_client, customer):
        order = _make_order(customer, status=OrderStatus.PRINTING)
        resp = admin_client.put(
            admin_cancel_url(order.id),
            {"reason": "No se puede"},
            format="json",
        )
        assert resp.status_code == 400

    def test_pedido_inexistente_devuelve_404(self, admin_client):
        import uuid
        resp = admin_client.put(
            admin_cancel_url(uuid.uuid4()),
            {"reason": "x"},
            format="json",
        )
        assert resp.status_code == 404

    def test_admin_cancela_exitosamente(self, admin_client, customer):
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
