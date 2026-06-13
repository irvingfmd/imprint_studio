"""
Tests de los endpoints de orders.
Casos del plan: 8-13, 58, 60, 61.
"""
import pytest
from unittest.mock import patch

from apps.orders.models import Order, OrderStatus, RequestType
from apps.orders.services import OrderService


ORDERS_URL = "/api/v1/orders/"
ADMIN_ORDERS_URL = "/api/v1/admin/orders/"
DASHBOARD_URL = "/api/v1/admin/dashboard/"


def order_url(order_id):
    return f"/api/v1/orders/{order_id}/"


def cancel_url(order_id):
    return f"/api/v1/orders/{order_id}/cancel/"


def files_url(order_id):
    return f"/api/v1/orders/{order_id}/files/"


def _make_order_via_service(customer, request_type=RequestType.REFERENCE, **kwargs) -> Order:
    data = dict(
        request_type=request_type,
        title="Yoda",
        description="Escala pequeña",
        quantity=1,
    )
    data.update(kwargs)
    return OrderService.create_order(customer, data)


@pytest.mark.django_db
class TestOrderListCreate:
    def test_sin_token_devuelve_401(self, api_client):
        # Caso 58
        resp = api_client.get(ORDERS_URL)
        assert resp.status_code == 401

    def test_get_retorna_pedidos_del_cliente(self, auth_client, customer):
        _make_order_via_service(customer)
        resp = auth_client.get(ORDERS_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_get_no_retorna_pedidos_de_otros_clientes(self, auth_client, customer, admin_user):
        _make_order_via_service(admin_user)
        resp = auth_client.get(ORDERS_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 0

    def test_post_reference_crea_pedido_received(self, auth_client):
        # Caso 8
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "REFERENCE",
            "title": "Busto Iron Man",
            "description": "Con detalle de pintura",
            "quantity": 1,
            "priority": "NORMAL",
        })
        assert resp.status_code == 201
        assert resp.data["data"]["status"] == OrderStatus.RECEIVED

    def test_post_printable_file_crea_pedido_pending_analysis(self, auth_client):
        # Caso 9
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "PRINTABLE_FILE",
            "title": "Pieza mecánica",
            "description": "Archivo STL adjunto",
            "quantity": 2,
        })
        assert resp.status_code == 201
        assert resp.data["data"]["status"] == OrderStatus.PENDING_ANALYSIS

    def test_post_cantidad_invalida_devuelve_400(self, auth_client):
        # Caso 10: quantity = 0
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Test",
            "quantity": 0,
        })
        assert resp.status_code == 400

    def test_post_prioridad_invalida_devuelve_400(self, auth_client):
        # Caso 11: prioridad inexistente
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Test",
            "quantity": 1,
            "priority": "SUPER_URGENTE",
        })
        assert resp.status_code == 400

    def test_post_sin_title_devuelve_400(self, auth_client):
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "REFERENCE",
            "description": "Sin título",
            "quantity": 1,
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestOrderDetail:
    def test_get_pedido_propio(self, auth_client, customer):
        # Caso 12: consultar pedido
        order = _make_order_via_service(customer)
        resp = auth_client.get(order_url(order.id))
        assert resp.status_code == 200
        assert str(resp.data["data"]["id"]) == str(order.id)

    def test_get_pedido_ajeno_devuelve_403(self, auth_client, admin_user):
        # Caso 60: cliente accede a pedido ajeno → 403
        foreign_order = _make_order_via_service(admin_user)
        resp = auth_client.get(order_url(foreign_order.id))
        assert resp.status_code == 403

    def test_get_pedido_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(order_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_admin_puede_ver_cualquier_pedido(self, admin_client, customer):
        order = _make_order_via_service(customer)
        resp = admin_client.get(order_url(order.id))
        assert resp.status_code == 200

    def test_sin_token_devuelve_401(self, api_client, customer):
        order = _make_order_via_service(customer)
        resp = api_client.get(order_url(order.id))
        assert resp.status_code == 401


@pytest.mark.django_db
class TestCancelOrder:
    @patch("apps.notifications.services.NotificationService.notify_order_cancelled")
    def test_cancela_pedido_propio_en_estado_cancelable(self, mock_notify, auth_client, customer):
        # Caso 13: cliente cancela pedido
        order = _make_order_via_service(customer)
        resp = auth_client.put(cancel_url(order.id), {"reason": "Ya no lo necesito"})
        assert resp.status_code == 200
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        assert order.cancellation_reason == "Ya no lo necesito"

    @patch("apps.notifications.services.NotificationService.notify_order_cancelled")
    def test_cancela_pedido_ajeno_devuelve_403(self, mock_notify, auth_client, admin_user):
        foreign_order = _make_order_via_service(admin_user)
        resp = auth_client.put(cancel_url(foreign_order.id), {"reason": "Motivo"})
        assert resp.status_code == 403

    @patch("apps.notifications.services.NotificationService.notify_order_cancelled")
    def test_cancela_pedido_en_estado_no_cancelable_devuelve_400(self, mock_notify, auth_client, customer):
        order = _make_order_via_service(customer)
        # Forzar un estado no cancelable
        order.status = OrderStatus.PRINTING
        order.save()
        resp = auth_client.put(cancel_url(order.id), {"reason": "Cambié de opinión"})
        assert resp.status_code == 400

    @patch("apps.notifications.services.NotificationService.notify_order_cancelled")
    def test_sin_razon_devuelve_400(self, mock_notify, auth_client, customer):
        order = _make_order_via_service(customer)
        resp = auth_client.put(cancel_url(order.id), {})
        assert resp.status_code == 400


@pytest.mark.django_db
class TestOrderFileListUpload:
    def test_listar_archivos_pedido_propio(self, auth_client, customer):
        order = _make_order_via_service(customer)
        resp = auth_client.get(files_url(order.id))
        assert resp.status_code == 200

    def test_listar_archivos_pedido_ajeno_devuelve_403(self, auth_client, admin_user):
        foreign_order = _make_order_via_service(admin_user)
        resp = auth_client.get(files_url(foreign_order.id))
        assert resp.status_code == 403

    def test_subir_archivo_valido(self, auth_client, customer):
        order = _make_order_via_service(customer)
        resp = auth_client.post(files_url(order.id), {
            "file_url": "https://cdn.test/modelo.stl",
            "file_type": "STL",
            "original_filename": "pieza.stl",
            "mime_type": "model/stl",
            "file_size_bytes": 204800,
        })
        assert resp.status_code == 201

    def test_subir_archivo_pedido_ajeno_devuelve_403(self, auth_client, admin_user):
        foreign_order = _make_order_via_service(admin_user)
        resp = auth_client.post(files_url(foreign_order.id), {
            "file_url": "https://cdn.test/a.jpg",
            "file_type": "IMAGE",
            "original_filename": "img.jpg",
            "mime_type": "image/jpeg",
            "file_size_bytes": 1024,
        })
        assert resp.status_code == 403


@pytest.mark.django_db
class TestAdminOrderList:
    def test_admin_ve_todos_los_pedidos(self, admin_client, customer):
        # Caso 61 inverso: admin SÍ puede
        _make_order_via_service(customer)
        _make_order_via_service(customer)
        resp = admin_client.get(ADMIN_ORDERS_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 2

    def test_cliente_en_endpoint_admin_devuelve_403(self, auth_client):
        # Caso 61: cliente accede a admin → 403
        resp = auth_client.get(ADMIN_ORDERS_URL)
        assert resp.status_code == 403

    def test_sin_token_devuelve_401(self, api_client):
        resp = api_client.get(ADMIN_ORDERS_URL)
        assert resp.status_code == 401

    def test_filtro_por_status_funciona(self, admin_client, customer):
        _make_order_via_service(customer)
        Order.objects.filter(customer=customer).update(status=OrderStatus.PRINTING)
        resp = admin_client.get(f"{ADMIN_ORDERS_URL}?status=PRINTING")
        assert resp.data["data"]["count"] == 1


@pytest.mark.django_db
class TestAdminDashboard:
    def test_admin_obtiene_metricas(self, admin_client):
        resp = admin_client.get(DASHBOARD_URL)
        assert resp.status_code == 200
        data = resp.data["data"]
        assert "pending_orders" in data
        assert "quoted_orders" in data
        assert "printing_orders" in data
        assert "ready_orders" in data
        assert "pending_payments" in data
        assert "monthly_revenue" in data

    def test_cliente_en_dashboard_devuelve_403(self, auth_client):
        resp = auth_client.get(DASHBOARD_URL)
        assert resp.status_code == 403
