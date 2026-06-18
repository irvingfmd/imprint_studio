"""
Tests de servicios de la app shipping.
Cubre: ShippingAddressService, ShipmentService.
"""

from decimal import Decimal

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
from apps.shipping.models import Shipment, ShippingAddress
from apps.shipping.services import ShipmentService, ShippingAddressService


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
        description="Prueba",
        quantity=1,
        priority="NORMAL",
        status=status,
    )
    if payment_status:
        order.payment_status = payment_status
        order.save(update_fields=["payment_status", "updated_at"])
    return order


# --- ShippingAddressService ---


@pytest.mark.django_db
class TestShippingAddressServiceCreate:
    def test_crea_direccion_exitosamente(self, customer):
        addr = ShippingAddressService.create_address(
            customer,
            {
                "address_name": "Trabajo",
                "street": "Blvd. Belisario Domínguez",
                "external_number": "2000",
                "neighborhood": "Lomas",
                "postal_code": "29045",
                "city": "Tuxtla Gutiérrez",
                "state": "Chiapas",
            },
        )
        assert addr.id is not None
        assert addr.user == customer

    def test_nueva_default_limpia_anterior(self, customer):
        addr1 = _make_address(customer, is_default=True)
        ShippingAddressService.create_address(
            customer,
            {
                "address_name": "Nueva Default",
                "street": "Calle 2",
                "external_number": "5",
                "neighborhood": "Norte",
                "postal_code": "29001",
                "city": "Tuxtla",
                "state": "Chiapas",
                "is_default": True,
            },
        )
        addr1.refresh_from_db()
        assert addr1.is_default is False

    def test_sin_is_default_no_afecta_anteriores(self, customer):
        addr1 = _make_address(customer, is_default=True)
        ShippingAddressService.create_address(
            customer,
            {
                "address_name": "Extra",
                "street": "Calle 3",
                "external_number": "9",
                "neighborhood": "Sur",
                "postal_code": "29002",
                "city": "Tuxtla",
                "state": "Chiapas",
                "is_default": False,
            },
        )
        addr1.refresh_from_db()
        assert addr1.is_default is True


@pytest.mark.django_db
class TestShippingAddressServiceUpdate:
    def test_actualiza_campos(self, customer):
        addr = _make_address(customer)
        updated = ShippingAddressService.update_address(
            addr,
            customer,
            {
                "address_name": "Modificada",
                "street": "Nuevo Blvd",
                "external_number": "99",
                "neighborhood": "Norte",
                "postal_code": "29010",
                "city": "Tuxtla",
                "state": "Chiapas",
            },
        )
        assert updated.address_name == "Modificada"

    def test_usuario_ajeno_lanza_error(self, customer):
        otro = User.objects.create_user(phone="+529611099802", first_name="Otro")
        addr = _make_address(customer)
        with pytest.raises(ValueError, match="permiso"):
            ShippingAddressService.update_address(addr, otro, {"address_name": "Hack"})

    def test_set_default_limpia_anterior(self, customer):
        addr1 = _make_address(customer, is_default=True)
        addr2 = _make_address(customer, is_default=False)
        ShippingAddressService.update_address(addr2, customer, {"is_default": True})
        addr1.refresh_from_db()
        assert addr1.is_default is False


@pytest.mark.django_db
class TestShippingAddressServiceDelete:
    def test_elimina_exitosamente(self, customer):
        addr = _make_address(customer)
        addr_id = addr.id
        ShippingAddressService.delete_address(addr, customer)
        assert not ShippingAddress.objects.filter(id=addr_id).exists()

    def test_usuario_ajeno_lanza_error(self, customer):
        otro = User.objects.create_user(phone="+529611099803", first_name="Otro")
        addr = _make_address(customer)
        with pytest.raises(ValueError, match="permiso"):
            ShippingAddressService.delete_address(addr, otro)


# --- ShipmentService ---


@pytest.mark.django_db
class TestShipmentServiceCreate:
    def test_crea_shipment_exitosamente(self, customer, admin_user):
        order = _make_order(customer)
        shipment = ShipmentService.create_shipment(
            order=order,
            carrier_name="DHL",
            tracking_number="ABC123",
            shipping_cost=Decimal("50.00"),
            shipping_notes="Paquete frágil",
            created_by=admin_user,
        )
        assert shipment.id is not None
        assert shipment.carrier_name == "DHL"
        assert shipment.tracking_number == "ABC123"
        assert shipment.shipping_cost == Decimal("50.00")
        assert shipment.shipped_at is not None

    def test_pedido_duplicado_lanza_error(self, customer, admin_user):
        order = _make_order(customer)
        ShipmentService.create_shipment(
            order=order,
            carrier_name="DHL",
            tracking_number="001",
            shipping_cost=Decimal("0"),
            shipping_notes="",
            created_by=admin_user,
        )
        with pytest.raises(ValueError, match="ya tiene un envío"):
            ShipmentService.create_shipment(
                order=order,
                carrier_name="Fedex",
                tracking_number="002",
                shipping_cost=Decimal("0"),
                shipping_notes="",
                created_by=admin_user,
            )

    def test_crea_evento_shipment_created(self, customer, admin_user):
        order = _make_order(customer)
        ShipmentService.create_shipment(
            order=order,
            carrier_name="DHL",
            tracking_number="123",
            shipping_cost=Decimal("0"),
            shipping_notes="",
            created_by=admin_user,
        )
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.SHIPMENT_CREATED,
        ).exists()

    def test_carrier_y_tracking_opcionales(self, customer, admin_user):
        order = _make_order(customer)
        shipment = ShipmentService.create_shipment(
            order=order,
            carrier_name="",
            tracking_number="",
            shipping_cost=Decimal("0"),
            shipping_notes="",
            created_by=admin_user,
        )
        assert shipment.carrier_name == ""
        assert shipment.tracking_number == ""


@pytest.mark.django_db
class TestShipmentServiceMarkDelivered:
    def _setup_delivered_ready_order(self, customer, admin_user):
        order = _make_order(
            customer,
            status=OrderStatus.FULLY_PAID,
            payment_status=OrderPaymentStatus.FULLY_PAID,
        )
        shipment = ShipmentService.create_shipment(
            order=order,
            carrier_name="DHL",
            tracking_number="XYZ",
            shipping_cost=Decimal("0"),
            shipping_notes="",
            created_by=admin_user,
        )
        return order, shipment

    def test_marca_delivered_at(self, customer, admin_user):
        order, shipment = self._setup_delivered_ready_order(customer, admin_user)
        ShipmentService.mark_delivered(shipment=shipment, admin=admin_user)
        shipment.refresh_from_db()
        assert shipment.delivered_at is not None

    def test_ya_entregado_lanza_error(self, customer, admin_user):
        order, shipment = self._setup_delivered_ready_order(customer, admin_user)
        ShipmentService.mark_delivered(shipment=shipment, admin=admin_user)
        shipment.refresh_from_db()
        with pytest.raises(ValueError, match="ya fue marcado"):
            ShipmentService.mark_delivered(shipment=shipment, admin=admin_user)

    def test_crea_evento_order_delivered(self, customer, admin_user):
        order, shipment = self._setup_delivered_ready_order(customer, admin_user)
        ShipmentService.mark_delivered(shipment=shipment, admin=admin_user)
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.ORDER_DELIVERED,
        ).exists()

    def test_transiciona_pedido_a_delivered(self, customer, admin_user):
        order, shipment = self._setup_delivered_ready_order(customer, admin_user)
        ShipmentService.mark_delivered(shipment=shipment, admin=admin_user)
        order.refresh_from_db()
        assert order.status == OrderStatus.DELIVERED

    def test_pedido_sin_pago_completo_lanza_error(self, customer, admin_user):
        order = _make_order(
            customer,
            status=OrderStatus.FULLY_PAID,
            payment_status=OrderPaymentStatus.DEPOSIT_PAID,
        )
        shipment = Shipment.objects.create(order=order)
        with pytest.raises(ValueError):
            ShipmentService.mark_delivered(shipment=shipment, admin=admin_user)
