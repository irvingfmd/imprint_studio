"""
Tests de los selectores de orders.
Validan aislamiento por usuario y filtros correctos.
"""
import pytest

from apps.orders.models import Order, OrderStatus, RequestType
from apps.orders.selectors import (
    get_all_orders,
    get_files_for_order,
    get_order_by_id,
    get_orders_for_customer,
)
from apps.orders.services import OrderService


def make_order(customer, **kwargs) -> Order:
    defaults = dict(
        request_type=RequestType.REFERENCE,
        title="Pedido test",
        description="Desc",
        quantity=1,
        status=OrderStatus.RECEIVED,
    )
    defaults.update(kwargs)
    return Order.objects.create(customer=customer, **defaults)


@pytest.mark.django_db
class TestGetOrdersForCustomer:
    def test_returns_only_customer_orders(self, customer, admin_user):
        # Aislamiento: cliente solo ve sus pedidos
        make_order(customer, title="Pedido A")
        make_order(admin_user, title="Pedido B")
        results = get_orders_for_customer(customer.id)
        assert results.count() == 1
        assert results.first().title == "Pedido A"

    def test_excludes_deleted_orders(self, customer):
        make_order(customer, is_deleted=True)
        results = get_orders_for_customer(customer.id)
        assert results.count() == 0

    def test_returns_multiple_orders(self, customer):
        make_order(customer, title="Pedido 1")
        make_order(customer, title="Pedido 2")
        make_order(customer, title="Pedido 3")
        assert get_orders_for_customer(customer.id).count() == 3

    def test_ordered_by_created_at_desc(self, customer):
        o1 = make_order(customer, title="Primero")
        o2 = make_order(customer, title="Segundo")
        results = list(get_orders_for_customer(customer.id))
        # El más reciente primero
        assert results[0].id == o2.id
        assert results[1].id == o1.id


@pytest.mark.django_db
class TestGetOrderById:
    def test_returns_existing_order(self, customer):
        order = make_order(customer)
        found = get_order_by_id(str(order.id))
        assert found.id == order.id

    def test_returns_none_for_nonexistent(self):
        import uuid
        result = get_order_by_id(str(uuid.uuid4()))
        assert result is None

    def test_returns_none_for_deleted_order(self, customer):
        order = make_order(customer, is_deleted=True)
        result = get_order_by_id(str(order.id))
        assert result is None


@pytest.mark.django_db
class TestGetAllOrders:
    def test_returns_all_non_deleted_orders(self, customer, admin_user):
        make_order(customer)
        make_order(admin_user)
        make_order(customer, is_deleted=True)
        assert get_all_orders().count() == 2

    def test_filter_by_status(self, customer):
        make_order(customer, status=OrderStatus.RECEIVED)
        make_order(customer, status=OrderStatus.PRINTING)
        results = get_all_orders(status=OrderStatus.RECEIVED)
        assert results.count() == 1
        assert results.first().status == OrderStatus.RECEIVED

    def test_filter_by_request_type(self, customer):
        make_order(customer, request_type=RequestType.REFERENCE)
        make_order(customer, request_type=RequestType.PRINTABLE_FILE, status=OrderStatus.PENDING_ANALYSIS)
        results = get_all_orders(request_type=RequestType.PRINTABLE_FILE)
        assert results.count() == 1

    def test_filter_by_customer_id(self, customer, admin_user):
        make_order(customer)
        make_order(admin_user)
        results = get_all_orders(customer_id=str(customer.id))
        assert results.count() == 1
        assert results.first().customer == customer


@pytest.mark.django_db
class TestGetFilesForOrder:
    def test_returns_files_for_order(self, customer):
        order = OrderService.create_order(customer, {
            "request_type": RequestType.REFERENCE,
            "title": "Test",
            "description": "Desc",
            "quantity": 1,
        })
        OrderService.upload_file(
            order=order,
            file_url="https://cdn.test/a.jpg",
            file_type="IMAGE",
            original_filename="a.jpg",
            mime_type="image/jpeg",
            file_size_bytes=1024,
            user=customer,
        )
        files = get_files_for_order(str(order.id))
        assert files.count() == 1

    def test_does_not_return_files_from_other_order(self, customer):
        order1 = OrderService.create_order(customer, {
            "request_type": RequestType.REFERENCE,
            "title": "Pedido 1",
            "description": "Desc",
            "quantity": 1,
        })
        order2 = OrderService.create_order(customer, {
            "request_type": RequestType.REFERENCE,
            "title": "Pedido 2",
            "description": "Desc",
            "quantity": 1,
        })
        OrderService.upload_file(
            order=order2,
            file_url="https://cdn.test/b.jpg",
            file_type="IMAGE",
            original_filename="b.jpg",
            mime_type="image/jpeg",
            file_size_bytes=1024,
            user=customer,
        )
        assert get_files_for_order(str(order1.id)).count() == 0
