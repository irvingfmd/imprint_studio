"""
Tests de los modelos Order, RequestFile y OrderEvent.
"""

import pytest

from apps.orders.models import (
    DeliveryMethod,
    EventType,
    Order,
    OrderEvent,
    OrderPaymentStatus,
    OrderPriority,
    OrderStatus,
    RequestFile,
    RequestType,
)


def make_order(customer, **kwargs) -> Order:
    """Helper: crea un pedido mínimo válido."""
    defaults = dict(
        request_type=RequestType.REFERENCE,
        title="Figura de prueba",
        description="Descripción de prueba",
        quantity=1,
        status=OrderStatus.RECEIVED,
    )
    defaults.update(kwargs)
    return Order.objects.create(customer=customer, **defaults)


@pytest.mark.django_db
class TestOrderModel:
    def test_defaults_on_create(self, customer):
        order = make_order(customer)
        assert order.priority == OrderPriority.NORMAL
        assert order.delivery_method == DeliveryMethod.PICKUP
        assert order.payment_status == OrderPaymentStatus.NO_PAYMENT
        assert order.is_deleted is False
        assert order.shipping_address is None

    def test_str_representation(self, customer):
        order = make_order(customer, title="Batman")
        assert "Batman" in str(order)
        assert order.status in str(order)

    def test_soft_delete_fields_exist(self, customer):
        order = make_order(customer)
        assert hasattr(order, "is_deleted")
        assert hasattr(order, "deleted_at")
        assert order.is_deleted is False
        assert order.deleted_at is None

    def test_reference_type_stored_correctly(self, customer):
        order = make_order(customer, request_type=RequestType.REFERENCE)
        assert order.request_type == RequestType.REFERENCE

    def test_printable_file_type_stored_correctly(self, customer):
        order = make_order(customer, request_type=RequestType.PRINTABLE_FILE)
        assert order.request_type == RequestType.PRINTABLE_FILE

    def test_optional_fields_default_to_empty(self, customer):
        order = make_order(customer)
        assert order.color == ""
        assert order.dimensions_notes == ""
        assert order.cancellation_reason == ""
        assert order.ai_analysis is None

    def test_timestamps_set_on_create(self, customer):
        order = make_order(customer)
        assert order.created_at is not None
        assert order.updated_at is not None


@pytest.mark.django_db
class TestOrderEventModel:
    def test_str_representation(self, customer):
        order = make_order(customer)
        event = OrderEvent.objects.create(
            order=order,
            event_type=EventType.ORDER_CREATED,
            created_by=customer,
        )
        assert EventType.ORDER_CREATED in str(event)

    def test_event_has_no_updated_at(self):
        # Por diseño: OrderEvent es inmutable, no tiene updated_at.
        assert not hasattr(OrderEvent, "updated_at")

    def test_metadata_stored_as_json(self, customer):
        order = make_order(customer)
        meta = {"priority": "NORMAL", "request_type": "REFERENCE"}
        event = OrderEvent.objects.create(
            order=order,
            event_type=EventType.ORDER_CREATED,
            metadata=meta,
            created_by=customer,
        )
        event.refresh_from_db()
        assert event.metadata["priority"] == "NORMAL"


@pytest.mark.django_db
class TestRequestFileModel:
    def test_str_representation(self, customer):
        order = make_order(customer)
        rf = RequestFile.objects.create(
            order=order,
            uploaded_by=customer,
            file_type="IMAGE",
            file_url="https://cdn.test/file.jpg",
            original_filename="figura.jpg",
            mime_type="image/jpeg",
            file_size_bytes=1024,
        )
        assert "IMAGE" in str(rf)
        assert "figura.jpg" in str(rf)
