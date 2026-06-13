"""
Tests de modelos de la app shipping.
Cubre: ShippingAddress, Shipment — campos, defaults, str, relaciones.
"""
import pytest
from decimal import Decimal

from apps.orders.models import Order, OrderStatus, RequestType
from apps.shipping.models import Shipment, ShippingAddress


def _make_address(user, is_default=False) -> ShippingAddress:
    return ShippingAddress.objects.create(
        user=user,
        address_name="Casa",
        street="Av. Central",
        external_number="100",
        neighborhood="Centro",
        postal_code="29000",
        city="Tuxtla Gutiérrez",
        state="Chiapas",
        is_default=is_default,
    )


def _make_order(customer) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Pedido Envío",
        description="Prueba",
        quantity=1,
        priority="NORMAL",
        status=OrderStatus.RECEIVED,
    )


@pytest.mark.django_db
class TestShippingAddressModel:
    def test_str(self, customer):
        addr = _make_address(customer)
        assert "Casa" in str(addr) or "Tuxtla" in str(addr)

    def test_uuid_primary_key(self, customer):
        addr = _make_address(customer)
        assert addr.id is not None
        assert "-" in str(addr.id)

    def test_defaults(self, customer):
        addr = _make_address(customer)
        assert addr.internal_number == ""
        assert addr.references == ""
        assert addr.country == "Mexico"
        assert addr.is_default is False

    def test_is_default_true(self, customer):
        addr = _make_address(customer, is_default=True)
        assert addr.is_default is True

    def test_reverse_relation(self, customer):
        addr = _make_address(customer)
        assert addr in customer.shipping_addresses.all()

    def test_created_at_set(self, customer):
        addr = _make_address(customer)
        assert addr.created_at is not None

    def test_updated_at_set(self, customer):
        addr = _make_address(customer)
        assert addr.updated_at is not None


@pytest.mark.django_db
class TestShipmentModel:
    def test_str(self, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order, carrier_name="DHL")
        assert "Shipment" in str(shipment)

    def test_uuid_primary_key(self, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order)
        assert "-" in str(shipment.id)

    def test_defaults(self, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order)
        assert shipment.carrier_name == ""
        assert shipment.tracking_number == ""
        assert shipment.shipping_cost == Decimal("0")
        assert shipment.shipped_at is None
        assert shipment.delivered_at is None
        assert shipment.shipping_notes == ""

    def test_one_to_one_con_order(self, customer):
        order = _make_order(customer)
        shipment = Shipment.objects.create(order=order)
        assert order.shipment == shipment

    def test_un_solo_shipment_por_orden(self, customer):
        from django.db import IntegrityError
        order = _make_order(customer)
        Shipment.objects.create(order=order)
        with pytest.raises(IntegrityError):
            Shipment.objects.create(order=order)
