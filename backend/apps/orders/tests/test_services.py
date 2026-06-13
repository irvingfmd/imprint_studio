"""
Tests de OrderService.
Casos del plan: 8, 9, 52 (ORDER_CREATED), 53 (FILE_UPLOADED).
"""
import pytest
from unittest.mock import patch

from apps.orders.models import (
    EventType,
    Order,
    OrderEvent,
    OrderStatus,
    RequestFile,
    RequestType,
)
from apps.orders.services import OrderService


def _base_data(**kwargs) -> dict:
    """Datos mínimos válidos para crear un pedido."""
    defaults = dict(
        request_type=RequestType.REFERENCE,
        title="Casco Mandalorian",
        description="Escala 1:1",
        quantity=1,
        priority="NORMAL",
    )
    defaults.update(kwargs)
    return defaults


@pytest.mark.django_db
class TestOrderServiceCreate:
    def test_reference_order_starts_as_received(self, customer):
        # Caso 8: REFERENCE → RECEIVED
        order = OrderService.create_order(customer, _base_data(request_type=RequestType.REFERENCE))
        assert order.status == OrderStatus.RECEIVED
        assert order.customer == customer

    def test_printable_file_order_starts_as_pending_analysis(self, customer):
        # Caso 9: PRINTABLE_FILE → PENDING_ANALYSIS
        order = OrderService.create_order(customer, _base_data(request_type=RequestType.PRINTABLE_FILE))
        assert order.status == OrderStatus.PENDING_ANALYSIS

    def test_creates_order_created_event(self, customer):
        # Caso 52: evento ORDER_CREATED generado
        order = OrderService.create_order(customer, _base_data())
        event = OrderEvent.objects.filter(
            order=order,
            event_type=EventType.ORDER_CREATED,
        ).first()
        assert event is not None
        assert event.created_by == customer

    def test_order_created_event_has_metadata(self, customer):
        order = OrderService.create_order(customer, _base_data())
        event = OrderEvent.objects.get(order=order, event_type=EventType.ORDER_CREATED)
        assert "request_type" in event.metadata
        assert "priority" in event.metadata

    def test_optional_fields_stored(self, customer):
        data = _base_data(color="Rojo", dimensions_notes="15cm x 10cm")
        order = OrderService.create_order(customer, data)
        assert order.color == "Rojo"
        assert order.dimensions_notes == "15cm x 10cm"

    def test_default_delivery_method_is_pickup(self, customer):
        order = OrderService.create_order(customer, _base_data())
        assert order.delivery_method == "PICKUP"


@pytest.mark.django_db
class TestOrderServiceAssignShipping:
    def test_assigns_address_belonging_to_user(self, customer):
        from apps.shipping.models import ShippingAddress
        order = OrderService.create_order(customer, _base_data())
        address = ShippingAddress.objects.create(
            user=customer,
            address_name="Casa",
            street="Av. Central 123",
            city="Tuxtla Gutiérrez",
            state="Chiapas",
            postal_code="29000",
            country="México",
        )
        updated = OrderService.assign_shipping_address(order, str(address.id), customer)
        assert updated.shipping_address == address

    def test_raises_if_address_belongs_to_other_user(self, customer, admin_user):
        from apps.shipping.models import ShippingAddress
        order = OrderService.create_order(customer, _base_data())
        other_address = ShippingAddress.objects.create(
            user=admin_user,
            address_name="Oficina",
            street="Calle 5 de Febrero 99",
            city="Tuxtla Gutiérrez",
            state="Chiapas",
            postal_code="29001",
            country="México",
        )
        with pytest.raises(ValueError, match="no pertenece"):
            OrderService.assign_shipping_address(order, str(other_address.id), customer)

    def test_creates_shipping_address_event(self, customer):
        from apps.shipping.models import ShippingAddress
        order = OrderService.create_order(customer, _base_data())
        address = ShippingAddress.objects.create(
            user=customer,
            address_name="Depto",
            street="Blvd. Belisario 45",
            city="Tuxtla Gutiérrez",
            state="Chiapas",
            postal_code="29002",
            country="México",
        )
        OrderService.assign_shipping_address(order, str(address.id), customer)
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.SHIPPING_ADDRESS_UPDATED,
        ).exists()


@pytest.mark.django_db
class TestOrderServiceUploadFile:
    def test_upload_file_creates_request_file(self, customer):
        # Caso 14-16: archivos almacenados
        order = OrderService.create_order(customer, _base_data())
        rf = OrderService.upload_file(
            order=order,
            file_url="https://cdn.test/modelo.stl",
            file_type="STL",
            original_filename="batman.stl",
            mime_type="model/stl",
            file_size_bytes=204800,
            user=customer,
        )
        assert RequestFile.objects.filter(id=rf.id).exists()
        assert rf.file_type == "STL"
        assert rf.order == order

    def test_upload_file_creates_file_uploaded_event(self, customer):
        # Caso 53: evento FILE_UPLOADED generado
        order = OrderService.create_order(customer, _base_data())
        OrderService.upload_file(
            order=order,
            file_url="https://cdn.test/foto.jpg",
            file_type="IMAGE",
            original_filename="referencia.jpg",
            mime_type="image/jpeg",
            file_size_bytes=51200,
            user=customer,
        )
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.FILE_UPLOADED,
        ).exists()

    def test_file_event_metadata_has_filename(self, customer):
        order = OrderService.create_order(customer, _base_data())
        OrderService.upload_file(
            order=order,
            file_url="https://cdn.test/doc.pdf",
            file_type="IMAGE",
            original_filename="comprobante.pdf",
            mime_type="application/pdf",
            file_size_bytes=10240,
            user=customer,
        )
        event = OrderEvent.objects.get(order=order, event_type=EventType.FILE_UPLOADED)
        assert event.metadata["filename"] == "comprobante.pdf"
