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
    def test_unauthenticated_returns_401(self, api_client):
        # Caso 58
        resp = api_client.get(ORDERS_URL)
        assert resp.status_code == 401

    def test_get_returns_customer_orders(self, auth_client, customer):
        _make_order_via_service(customer)
        resp = auth_client.get(ORDERS_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_get_excludes_other_customers_orders(self, auth_client, customer, admin_user):
        _make_order_via_service(admin_user)
        resp = auth_client.get(ORDERS_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 0

    def test_post_reference_creates_received_order(self, auth_client):
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

    def test_post_printable_file_creates_pending_analysis_order(self, auth_client):
        # Caso 9
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "PRINTABLE_FILE",
            "title": "Pieza mecánica",
            "description": "Archivo STL adjunto",
            "quantity": 2,
        })
        assert resp.status_code == 201
        assert resp.data["data"]["status"] == OrderStatus.PENDING_ANALYSIS

    def test_post_web_model_creates_pending_analysis_order(self, auth_client):
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "WEB_MODEL",
            "title": "Yoda de MakerWorld",
            "description": "Enlace al modelo",
            "quantity": 1,
        })
        assert resp.status_code == 201
        assert resp.data["data"]["status"] == OrderStatus.PENDING_ANALYSIS

    def test_post_invalid_quantity_returns_400(self, auth_client):
        # Caso 10: quantity = 0
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Test",
            "quantity": 0,
        })
        assert resp.status_code == 400

    def test_post_invalid_priority_returns_400(self, auth_client):
        # Caso 11: prioridad inexistente
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Test",
            "quantity": 1,
            "priority": "SUPER_URGENTE",
        })
        assert resp.status_code == 400

    def test_post_missing_title_returns_400(self, auth_client):
        resp = auth_client.post(ORDERS_URL, {
            "request_type": "REFERENCE",
            "description": "Sin título",
            "quantity": 1,
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestOrderDetail:
    def test_get_own_order(self, auth_client, customer):
        # Caso 12: consultar pedido
        order = _make_order_via_service(customer)
        resp = auth_client.get(order_url(order.id))
        assert resp.status_code == 200
        assert str(resp.data["data"]["id"]) == str(order.id)

    def test_get_foreign_order_returns_403(self, auth_client, admin_user):
        # Caso 60: cliente accede a pedido ajeno → 403
        foreign_order = _make_order_via_service(admin_user)
        resp = auth_client.get(order_url(foreign_order.id))
        assert resp.status_code == 403

    def test_get_nonexistent_order_returns_404(self, auth_client):
        import uuid
        resp = auth_client.get(order_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_admin_can_view_any_order(self, admin_client, customer):
        order = _make_order_via_service(customer)
        resp = admin_client.get(order_url(order.id))
        assert resp.status_code == 200

    def test_unauthenticated_returns_401(self, api_client, customer):
        order = _make_order_via_service(customer)
        resp = api_client.get(order_url(order.id))
        assert resp.status_code == 401


@pytest.mark.django_db
class TestCancelOrder:
    @patch("apps.notifications.services.NotificationService.notify_order_cancelled")
    def test_cancel_own_order_in_cancelable_state(self, mock_notify, auth_client, customer):
        # Caso 13: cliente cancela pedido
        order = _make_order_via_service(customer)
        resp = auth_client.put(cancel_url(order.id), {"reason": "Ya no lo necesito"})
        assert resp.status_code == 200
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        assert order.cancellation_reason == "Ya no lo necesito"

    @patch("apps.notifications.services.NotificationService.notify_order_cancelled")
    def test_cancel_foreign_order_returns_403(self, mock_notify, auth_client, admin_user):
        foreign_order = _make_order_via_service(admin_user)
        resp = auth_client.put(cancel_url(foreign_order.id), {"reason": "Motivo"})
        assert resp.status_code == 403

    @patch("apps.notifications.services.NotificationService.notify_order_cancelled")
    def test_cancel_order_in_non_cancelable_state_returns_400(self, mock_notify, auth_client, customer):
        order = _make_order_via_service(customer)
        # Forzar un estado no cancelable
        order.status = OrderStatus.PRINTING
        order.save()
        resp = auth_client.put(cancel_url(order.id), {"reason": "Cambié de opinión"})
        assert resp.status_code == 400

    @patch("apps.notifications.services.NotificationService.notify_order_cancelled")
    def test_missing_reason_returns_400(self, mock_notify, auth_client, customer):
        order = _make_order_via_service(customer)
        resp = auth_client.put(cancel_url(order.id), {})
        assert resp.status_code == 400


@pytest.mark.django_db
class TestOrderFileListUpload:
    def test_list_files_own_order(self, auth_client, customer):
        order = _make_order_via_service(customer)
        resp = auth_client.get(files_url(order.id))
        assert resp.status_code == 200

    def test_list_files_foreign_order_returns_403(self, auth_client, admin_user):
        foreign_order = _make_order_via_service(admin_user)
        resp = auth_client.get(files_url(foreign_order.id))
        assert resp.status_code == 403

    def test_upload_valid_file(self, auth_client, customer):
        order = _make_order_via_service(customer)
        resp = auth_client.post(files_url(order.id), {
            "file_url": "https://cdn.test/modelo.stl",
            "file_type": "STL",
            "original_filename": "pieza.stl",
            "mime_type": "model/stl",
            "file_size_bytes": 204800,
        })
        assert resp.status_code == 201

    def test_upload_web_model_link(self, auth_client, customer):
        order = _make_order_via_service(customer, request_type=RequestType.WEB_MODEL)
        resp = auth_client.post(files_url(order.id), {
            "file_url": "https://makerworld.com/models/12345",
            "file_type": "WEB_MODEL",
            "original_filename": "Yoda Mini",
        })
        assert resp.status_code == 201

    def test_upload_file_to_foreign_order_returns_403(self, auth_client, admin_user):
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
    def test_admin_sees_all_orders(self, admin_client, customer):
        # Caso 61 inverso: admin SÍ puede
        _make_order_via_service(customer)
        _make_order_via_service(customer)
        resp = admin_client.get(ADMIN_ORDERS_URL)
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 2

    def test_customer_at_admin_endpoint_returns_403(self, auth_client):
        # Caso 61: cliente accede a admin → 403
        resp = auth_client.get(ADMIN_ORDERS_URL)
        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, api_client):
        resp = api_client.get(ADMIN_ORDERS_URL)
        assert resp.status_code == 401

    def test_status_filter_works(self, admin_client, customer):
        _make_order_via_service(customer)
        Order.objects.filter(customer=customer).update(status=OrderStatus.PRINTING)
        resp = admin_client.get(f"{ADMIN_ORDERS_URL}?status=PRINTING")
        assert resp.data["data"]["count"] == 1


@pytest.mark.django_db
class TestAdminOrderListPaginacion:
    def test_respuesta_incluye_num_pages(self, admin_client, customer):
        _make_order_via_service(customer)
        resp = admin_client.get(ADMIN_ORDERS_URL)
        assert resp.status_code == 200
        assert "num_pages" in resp.data["data"]

    def test_page_size_limita_resultados(self, admin_client, customer):
        _make_order_via_service(customer)
        _make_order_via_service(customer)
        resp = admin_client.get(ADMIN_ORDERS_URL + "?page_size=1")
        assert resp.status_code == 200
        assert len(resp.data["data"]["results"]) == 1
        assert resp.data["data"]["num_pages"] >= 2

    def test_page_size_invalido_devuelve_400(self, admin_client):
        resp = admin_client.get(ADMIN_ORDERS_URL + "?page_size=abc")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestAdminOrderDetailActiveQuote:
    def test_detalle_incluye_active_quote_cuando_existe(self, admin_client, customer, admin_user):
        from decimal import Decimal
        from apps.quotes.models import Quote

        order = _make_order_via_service(customer)
        Quote.objects.create(
            order=order,
            created_by=admin_user,
            weight_grams=Decimal("200"),
            print_time_hours=Decimal("5"),
            material_cost=Decimal("50"),
            energy_cost=Decimal("10"),
            labor_cost=Decimal("30"),
            post_processing_cost=Decimal("0"),
            packaging_cost=Decimal("5"),
            risk_cost=Decimal("5"),
            shipping_cost=Decimal("0"),
            subtotal=Decimal("100"),
            profit_amount=Decimal("20"),
            discount_amount=Decimal("0"),
            total_price=Decimal("120"),
        )
        resp = admin_client.get(f"{ADMIN_ORDERS_URL}{order.id}/")
        assert resp.status_code == 200
        assert resp.data["data"]["active_quote"] is not None
        assert "total_price" in resp.data["data"]["active_quote"]
        assert "quote_status" in resp.data["data"]["active_quote"]

    def test_detalle_active_quote_es_none_sin_cotizacion(self, admin_client, customer):
        order = _make_order_via_service(customer)
        resp = admin_client.get(f"{ADMIN_ORDERS_URL}{order.id}/")
        assert resp.status_code == 200
        assert resp.data["data"]["active_quote"] is None

    def test_cliente_no_accede_a_detalle_admin(self, auth_client, customer):
        order = _make_order_via_service(customer)
        resp = auth_client.get(f"{ADMIN_ORDERS_URL}{order.id}/")
        assert resp.status_code == 403


@pytest.mark.django_db
class TestAdminDashboard:
    def test_admin_gets_metrics(self, admin_client):
        resp = admin_client.get(DASHBOARD_URL)
        assert resp.status_code == 200
        data = resp.data["data"]
        assert "pending_orders" in data
        assert "quoted_orders" in data
        assert "printing_orders" in data
        assert "ready_orders" in data
        assert "pending_payments" in data
        assert "monthly_revenue" in data

    def test_customer_at_dashboard_returns_403(self, auth_client):
        resp = auth_client.get(DASHBOARD_URL)
        assert resp.status_code == 403
