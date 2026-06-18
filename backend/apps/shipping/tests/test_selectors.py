"""
Tests de selectores de la app shipping.
Cubre: get_address_by_id, get_addresses_for_user, get_shipment_by_id, get_shipment_for_order.
"""

import pytest

from apps.orders.models import Order, OrderStatus, RequestType
from apps.shipping import selectors
from apps.shipping.models import Shipment, ShippingAddress


def _make_address(user) -> ShippingAddress:
    return ShippingAddress.objects.create(
        user=user,
        address_name="Casa",
        street="Calle 1",
        external_number="1",
        neighborhood="Centro",
        postal_code="29000",
        city="Tuxtla",
        state="Chiapas",
    )


def _make_order(customer) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido",
        description="Test",
        quantity=1,
        priority="NORMAL",
        status=OrderStatus.RECEIVED,
    )


@pytest.mark.django_db
class TestGetAddressById:
    def test_retorna_direccion_existente(self, customer):
        addr = _make_address(customer)
        result = selectors.get_address_by_id(str(addr.id))
        assert result is not None
        assert result.id == addr.id

    def test_retorna_none_si_no_existe(self, customer):
        import uuid

        result = selectors.get_address_by_id(str(uuid.uuid4()))
        assert result is None


@pytest.mark.django_db
class TestGetAddressesForUser:
    def test_retorna_direcciones_del_usuario(self, customer):
        _make_address(customer)
        _make_address(customer)
        qs = selectors.get_addresses_for_user(str(customer.id))
        assert qs.count() == 2

    def test_excluye_direcciones_de_otros_usuarios(self, customer):
        from apps.authentication.models import User

        otro = User.objects.create_user(phone="+529611099801", first_name="Otro")
        _make_address(customer)
        _make_address(otro)
        qs = selectors.get_addresses_for_user(str(customer.id))
        assert qs.count() == 1
        assert all(a.user_id == customer.id for a in qs)

    def test_retorna_vacio_si_no_hay_direcciones(self, customer):
        qs = selectors.get_addresses_for_user(str(customer.id))
        assert qs.count() == 0

    def test_ordenado_por_created_at_descendente(self, customer):
        addr1 = _make_address(customer)
        addr2 = _make_address(customer)
        qs = list(selectors.get_addresses_for_user(str(customer.id)))
        # La más reciente primero
        assert qs[0].created_at >= qs[-1].created_at


@pytest.mark.django_db
class TestGetShipmentById:
    def test_retorna_shipment_existente(self, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order, carrier_name="DHL")
        result = selectors.get_shipment_by_id(str(shipment.id))
        assert result is not None
        assert result.id == shipment.id

    def test_retorna_none_si_no_existe(self, customer):
        import uuid

        result = selectors.get_shipment_by_id(str(uuid.uuid4()))
        assert result is None


@pytest.mark.django_db
class TestGetShipmentForOrder:
    def test_retorna_shipment_del_pedido(self, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order)
        result = selectors.get_shipment_for_order(str(order.id))
        assert result is not None
        assert result.id == shipment.id

    def test_retorna_none_si_pedido_sin_shipment(self, customer):
        order = _make_order(customer)
        result = selectors.get_shipment_for_order(str(order.id))
        assert result is None
