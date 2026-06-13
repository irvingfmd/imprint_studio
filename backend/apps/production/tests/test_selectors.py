"""
Tests de selectores de la app production.
Cubre: get_production_history_for_order, get_events_for_order, get_event_by_id.
"""
import pytest

from apps.orders.models import EventType, Order, OrderEvent, OrderStatus, RequestType
from apps.production.models import ProductionHistory
from apps.production import selectors


def _make_order(customer) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Selector Test",
        description="Para selector",
        quantity=1,
        priority="NORMAL",
        status=OrderStatus.RECEIVED,
    )


def _make_history(order, admin_user, new_status=OrderStatus.QUOTED) -> ProductionHistory:
    return ProductionHistory.objects.create(
        order=order,
        previous_status=OrderStatus.RECEIVED,
        new_status=new_status,
        changed_by=admin_user,
    )


def _make_event(order, customer, event_type=EventType.ORDER_CREATED) -> OrderEvent:
    return OrderEvent.objects.create(
        order=order,
        event_type=event_type,
        event_description="Evento de prueba",
        created_by=customer,
    )


@pytest.mark.django_db
class TestGetProductionHistoryForOrder:
    def test_retorna_historial_del_pedido(self, customer, admin_user):
        order = _make_order(customer)
        _make_history(order, admin_user)
        qs = selectors.get_production_history_for_order(str(order.id))
        assert qs.count() == 1

    def test_excluye_historial_de_otro_pedido(self, customer, admin_user):
        order1 = _make_order(customer)
        order2 = _make_order(customer)
        _make_history(order1, admin_user)
        _make_history(order2, admin_user)
        qs = selectors.get_production_history_for_order(str(order1.id))
        assert qs.count() == 1
        assert all(h.order_id == order1.id for h in qs)

    def test_ordenado_por_changed_at_ascendente(self, customer, admin_user):
        order = _make_order(customer)
        _make_history(order, admin_user, new_status=OrderStatus.QUOTED)
        _make_history(order, admin_user, new_status=OrderStatus.APPROVED)
        qs = list(selectors.get_production_history_for_order(str(order.id)))
        assert qs[0].changed_at <= qs[-1].changed_at

    def test_retorna_queryset_vacio_si_no_hay_historial(self, customer):
        order = _make_order(customer)
        qs = selectors.get_production_history_for_order(str(order.id))
        assert qs.count() == 0


@pytest.mark.django_db
class TestGetEventsForOrder:
    def test_retorna_eventos_del_pedido(self, customer):
        order = _make_order(customer)
        _make_event(order, customer)
        _make_event(order, customer, event_type=EventType.STATUS_CHANGED)
        qs = selectors.get_events_for_order(str(order.id))
        assert qs.count() == 2

    def test_excluye_eventos_de_otro_pedido(self, customer):
        order1 = _make_order(customer)
        order2 = _make_order(customer)
        _make_event(order1, customer)
        _make_event(order2, customer)
        qs = selectors.get_events_for_order(str(order1.id))
        assert qs.count() == 1
        assert all(e.order_id == order1.id for e in qs)

    def test_ordenado_por_created_at_ascendente(self, customer):
        order = _make_order(customer)
        _make_event(order, customer, event_type=EventType.ORDER_CREATED)
        _make_event(order, customer, event_type=EventType.STATUS_CHANGED)
        qs = list(selectors.get_events_for_order(str(order.id)))
        assert qs[0].created_at <= qs[-1].created_at

    def test_retorna_vacio_si_no_hay_eventos(self, customer):
        order = _make_order(customer)
        qs = selectors.get_events_for_order(str(order.id))
        assert qs.count() == 0


@pytest.mark.django_db
class TestGetEventById:
    def test_retorna_evento_existente(self, customer):
        order = _make_order(customer)
        event = _make_event(order, customer)
        result = selectors.get_event_by_id(str(event.id), str(order.id))
        assert result is not None
        assert result.id == event.id

    def test_retorna_none_cuando_no_existe(self, customer):
        import uuid
        order = _make_order(customer)
        result = selectors.get_event_by_id(str(uuid.uuid4()), str(order.id))
        assert result is None

    def test_retorna_none_cuando_es_de_otro_pedido(self, customer):
        order1 = _make_order(customer)
        order2 = _make_order(customer)
        event = _make_event(order1, customer)
        # Buscar el evento de order1 con el id de order2 → None
        result = selectors.get_event_by_id(str(event.id), str(order2.id))
        assert result is None
