"""
Tests de los endpoints de la app shipping.

Endpoints cubiertos:
  GET/POST /api/v1/shipping-addresses/
  GET/PUT/DELETE /api/v1/shipping-addresses/{address_id}/
  GET /api/v1/shipments/{shipment_id}/
  POST /api/v1/admin/orders/{order_id}/shipment/
  PUT /api/v1/admin/shipments/{shipment_id}/delivered/
"""
import pytest
from decimal import Decimal

from apps.authentication.models import User
from apps.orders.models import Order, OrderPaymentStatus, OrderStatus, RequestType
from apps.shipping.models import Shipment, ShippingAddress


# --- URL helpers ---

def addresses_url():
    return "/api/v1/shipping-addresses/"

def address_detail_url(address_id):
    return f"/api/v1/shipping-addresses/{address_id}/"

def shipment_url(shipment_id):
    return f"/api/v1/shipments/{shipment_id}/"

def admin_create_shipment_url(order_id):
    return f"/api/v1/admin/orders/{order_id}/shipment/"

def admin_delivered_url(shipment_id):
    return f"/api/v1/admin/shipments/{shipment_id}/delivered/"


# --- Helpers de datos ---

def _valid_address_data(**kwargs) -> dict:
    base = {
        "address_name": "Casa",
        "street": "Av. Central",
        "external_number": "100",
        "neighborhood": "Centro",
        "postal_code": "29000",
        "city": "Tuxtla Gutiérrez",
        "state": "Chiapas",
    }
    base.update(kwargs)
    return base


def _make_address(user, is_default=False) -> ShippingAddress:
    return ShippingAddress.objects.create(
        user=user,
        address_name="Casa",
        street="Calle 1",
        external_number="1",
        neighborhood="Centro",
        postal_code="29000",
        city="Tuxtla",
        state="Chiapas",
        is_default=is_default,
    )


def _make_order(customer, status=OrderStatus.RECEIVED, payment_status=None) -> Order:
    order = Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido Envío",
        description="Test",
        quantity=1,
        priority="NORMAL",
        status=status,
    )
    if payment_status:
        order.payment_status = payment_status
        order.save(update_fields=["payment_status", "updated_at"])
    return order


# --- GET/POST /api/v1/shipping-addresses/ ---

@pytest.mark.django_db
class TestShippingAddressListCreateView:
    def test_sin_token_devuelve_401(self, api_client):
        resp = api_client.get(addresses_url())
        assert resp.status_code == 401

    def test_cliente_ve_sus_direcciones(self, auth_client, customer):
        _make_address(customer)
        resp = auth_client.get(addresses_url())
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_no_ve_direcciones_de_otros(self, auth_client):
        otro = User.objects.create_user(phone="+529611099851", first_name="Otro")
        _make_address(otro)
        resp = auth_client.get(addresses_url())
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 0

    def test_crea_direccion_valida(self, auth_client):
        resp = auth_client.post(addresses_url(), _valid_address_data(), format="json")
        assert resp.status_code == 201
        assert "id" in resp.data["data"]

    def test_crea_sin_campo_requerido_devuelve_400(self, auth_client):
        data = _valid_address_data()
        del data["street"]
        resp = auth_client.post(addresses_url(), data, format="json")
        assert resp.status_code == 400

    def test_sin_token_post_devuelve_401(self, api_client):
        resp = api_client.post(addresses_url(), _valid_address_data(), format="json")
        assert resp.status_code == 401


# --- GET/PUT/DELETE /api/v1/shipping-addresses/{address_id}/ ---

@pytest.mark.django_db
class TestShippingAddressDetailView:
    def test_sin_token_devuelve_401(self, api_client, customer):
        addr = _make_address(customer)
        resp = api_client.get(address_detail_url(addr.id))
        assert resp.status_code == 401

    def test_propietario_ve_detalle(self, auth_client, customer):
        addr = _make_address(customer)
        resp = auth_client.get(address_detail_url(addr.id))
        assert resp.status_code == 200
        assert str(addr.id) in str(resp.data["data"]["id"])

    def test_usuario_ajeno_recibe_403(self, api_client, customer):
        otro = User.objects.create_user(phone="+529611099852", first_name="Otro")
        addr = _make_address(otro)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(address_detail_url(addr.id))
        assert resp.status_code == 403

    def test_direccion_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(address_detail_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_admin_ve_direccion_de_cualquier_usuario(self, admin_client, customer):
        addr = _make_address(customer)
        resp = admin_client.get(address_detail_url(addr.id))
        assert resp.status_code == 200

    def test_propietario_actualiza_direccion(self, auth_client, customer):
        addr = _make_address(customer)
        data = _valid_address_data(address_name="Trabajo")
        resp = auth_client.put(address_detail_url(addr.id), data, format="json")
        assert resp.status_code == 200
        addr.refresh_from_db()
        assert addr.address_name == "Trabajo"

    def test_actualizacion_campo_invalido_devuelve_400(self, auth_client, customer):
        addr = _make_address(customer)
        # Falta street (campo requerido)
        data = {"address_name": "x"}
        resp = auth_client.put(address_detail_url(addr.id), data, format="json")
        assert resp.status_code == 400

    def test_propietario_elimina_direccion(self, auth_client, customer):
        addr = _make_address(customer)
        resp = auth_client.delete(address_detail_url(addr.id))
        assert resp.status_code == 200
        assert not ShippingAddress.objects.filter(id=addr.id).exists()

    def test_usuario_ajeno_no_puede_eliminar(self, api_client, customer):
        otro = User.objects.create_user(phone="+529611099853", first_name="Otro")
        addr = _make_address(otro)
        api_client.force_authenticate(user=customer)
        resp = api_client.delete(address_detail_url(addr.id))
        assert resp.status_code == 403


# --- GET /api/v1/shipments/{shipment_id}/ ---

@pytest.mark.django_db
class TestShipmentDetailView:
    def test_sin_token_devuelve_401(self, api_client, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order)
        resp = api_client.get(shipment_url(shipment.id))
        assert resp.status_code == 401

    def test_propietario_ve_su_envio(self, auth_client, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order)
        resp = auth_client.get(shipment_url(shipment.id))
        assert resp.status_code == 200
        assert str(shipment.id) in str(resp.data["data"]["id"])

    def test_usuario_ajeno_recibe_403(self, api_client, customer):
        otro = User.objects.create_user(phone="+529611099854", first_name="Otro")
        order = _make_order(otro)
        shipment = Shipment.objects.create(order=order)
        api_client.force_authenticate(user=customer)
        resp = api_client.get(shipment_url(shipment.id))
        assert resp.status_code == 403

    def test_shipment_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(shipment_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_admin_ve_cualquier_envio(self, admin_client, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order)
        resp = admin_client.get(shipment_url(shipment.id))
        assert resp.status_code == 200


# --- POST /api/v1/admin/orders/{order_id}/shipment/ ---

@pytest.mark.django_db
class TestAdminCreateShipmentView:
    def test_sin_token_devuelve_401(self, api_client, customer):
        order = _make_order(customer)
        resp = api_client.post(admin_create_shipment_url(order.id), {})
        assert resp.status_code == 401

    def test_cliente_devuelve_403(self, auth_client, customer):
        order = _make_order(customer)
        resp = auth_client.post(admin_create_shipment_url(order.id), {}, format="json")
        assert resp.status_code == 403

    def test_pedido_inexistente_devuelve_404(self, admin_client):
        import uuid
        resp = admin_client.post(
            admin_create_shipment_url(uuid.uuid4()),
            {"carrier_name": "DHL"},
            format="json",
        )
        assert resp.status_code == 404

    def test_admin_crea_shipment_exitosamente(self, admin_client, customer):
        order = _make_order(customer)
        resp = admin_client.post(
            admin_create_shipment_url(order.id),
            {
                "carrier_name": "DHL",
                "tracking_number": "9876543210",
                "shipping_cost": "50.00",
            },
            format="json",
        )
        assert resp.status_code == 201
        assert Shipment.objects.filter(order=order).exists()

    def test_shipment_duplicado_devuelve_400(self, admin_client, customer):
        order = _make_order(customer)
        Shipment.objects.create(order=order)
        resp = admin_client.post(
            admin_create_shipment_url(order.id),
            {"carrier_name": "DHL"},
            format="json",
        )
        assert resp.status_code == 400

    def test_todos_los_campos_son_opcionales(self, admin_client, customer):
        order = _make_order(customer)
        resp = admin_client.post(admin_create_shipment_url(order.id), {}, format="json")
        assert resp.status_code == 201


# --- PUT /api/v1/admin/shipments/{shipment_id}/delivered/ ---

@pytest.mark.django_db
class TestAdminMarkShipmentDeliveredView:
    def _setup(self, customer, admin_user):
        from apps.shipping.services import ShipmentService
        order = _make_order(
            customer,
            status=OrderStatus.FULLY_PAID,
            payment_status=OrderPaymentStatus.FULLY_PAID,
        )
        shipment = ShipmentService.create_shipment(
            order=order,
            carrier_name="DHL",
            tracking_number="123",
            shipping_cost=Decimal("0"),
            shipping_notes="",
            created_by=admin_user,
        )
        return order, shipment

    def test_sin_token_devuelve_401(self, api_client, customer, admin_user):
        _, shipment = self._setup(customer, admin_user)
        resp = api_client.put(admin_delivered_url(shipment.id))
        assert resp.status_code == 401

    def test_cliente_devuelve_403(self, auth_client, customer, admin_user):
        _, shipment = self._setup(customer, admin_user)
        resp = auth_client.put(admin_delivered_url(shipment.id), {}, format="json")
        assert resp.status_code == 403

    def test_shipment_inexistente_devuelve_404(self, admin_client):
        import uuid
        resp = admin_client.put(admin_delivered_url(uuid.uuid4()), {}, format="json")
        assert resp.status_code == 404

    def test_admin_marca_entregado_exitosamente(self, admin_client, customer, admin_user):
        _, shipment = self._setup(customer, admin_user)
        resp = admin_client.put(admin_delivered_url(shipment.id), {}, format="json")
        assert resp.status_code == 200
        shipment.refresh_from_db()
        assert shipment.delivered_at is not None

    def test_ya_entregado_devuelve_400(self, admin_client, customer, admin_user):
        _, shipment = self._setup(customer, admin_user)
        admin_client.put(admin_delivered_url(shipment.id), {}, format="json")
        shipment.refresh_from_db()
        resp = admin_client.put(admin_delivered_url(shipment.id), {}, format="json")
        assert resp.status_code == 400
