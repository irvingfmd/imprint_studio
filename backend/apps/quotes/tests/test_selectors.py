"""
Tests de selectores de la app quotes.
Cubre: get_quote_by_id, get_quotes_for_order, get_active_quote_for_order.
Verifica aislamiento entre pedidos/usuarios.
"""
import pytest
from decimal import Decimal

from apps.orders.models import Order, OrderStatus, RequestType
from apps.quotes.models import Quote, QuoteStatus
from apps.quotes import selectors


def _make_order(customer) -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Figura Test",
        description="Para prueba",
        quantity=1,
        priority="NORMAL",
        status=OrderStatus.RECEIVED,
    )


def _make_quote(order, admin_user, status=QuoteStatus.PENDING, is_deleted=False) -> Quote:
    return Quote.objects.create(
        order=order,
        created_by=admin_user,
        weight_grams=Decimal("100.00"),
        print_time_hours=Decimal("5.00"),
        material_cost=Decimal("2.50"),
        energy_cost=Decimal("2.50"),
        labor_cost=Decimal("75.00"),
        post_processing_cost=Decimal("5.00"),
        packaging_cost=Decimal("2.00"),
        risk_cost=Decimal("0.50"),
        subtotal=Decimal("87.50"),
        profit_amount=Decimal("26.25"),
        total_price=Decimal("113.75"),
        quote_status=status,
        is_deleted=is_deleted,
    )


@pytest.mark.django_db
class TestGetQuoteById:
    def test_retorna_cotizacion_existente(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user)
        result = selectors.get_quote_by_id(str(quote.id))
        assert result is not None
        assert result.id == quote.id

    def test_retorna_none_cuando_no_existe(self):
        import uuid
        result = selectors.get_quote_by_id(str(uuid.uuid4()))
        assert result is None

    def test_retorna_none_cuando_eliminada(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user, is_deleted=True)
        result = selectors.get_quote_by_id(str(quote.id))
        assert result is None


@pytest.mark.django_db
class TestGetQuotesForOrder:
    def test_retorna_cotizaciones_del_pedido(self, customer, admin_user):
        order = _make_order(customer)
        _make_quote(order, admin_user)
        _make_quote(order, admin_user, status=QuoteStatus.EXPIRED)
        qs = selectors.get_quotes_for_order(str(order.id))
        assert qs.count() == 2

    def test_excluye_eliminadas(self, customer, admin_user):
        order = _make_order(customer)
        _make_quote(order, admin_user)
        _make_quote(order, admin_user, is_deleted=True)
        qs = selectors.get_quotes_for_order(str(order.id))
        assert qs.count() == 1

    def test_excluye_cotizaciones_de_otro_pedido(self, customer, admin_user):
        order1 = _make_order(customer)
        order2 = _make_order(customer)
        _make_quote(order1, admin_user)
        _make_quote(order2, admin_user)
        qs = selectors.get_quotes_for_order(str(order1.id))
        assert qs.count() == 1

    def test_ordenadas_por_created_at_desc(self, customer, admin_user):
        order = _make_order(customer)
        q1 = _make_quote(order, admin_user)
        q2 = _make_quote(order, admin_user, status=QuoteStatus.EXPIRED)
        qs = list(selectors.get_quotes_for_order(str(order.id)))
        # La más reciente primero
        assert qs[0].created_at >= qs[-1].created_at


@pytest.mark.django_db
class TestGetActiveQuoteForOrder:
    def test_retorna_cotizacion_pending(self, customer, admin_user):
        order = _make_order(customer)
        quote = _make_quote(order, admin_user, status=QuoteStatus.PENDING)
        result = selectors.get_active_quote_for_order(str(order.id))
        assert result is not None
        assert result.id == quote.id

    def test_retorna_none_si_no_hay_pending(self, customer, admin_user):
        order = _make_order(customer)
        _make_quote(order, admin_user, status=QuoteStatus.ACCEPTED)
        result = selectors.get_active_quote_for_order(str(order.id))
        assert result is None

    def test_excluye_eliminadas(self, customer, admin_user):
        order = _make_order(customer)
        _make_quote(order, admin_user, status=QuoteStatus.PENDING, is_deleted=True)
        result = selectors.get_active_quote_for_order(str(order.id))
        assert result is None

    def test_retorna_none_si_no_hay_cotizaciones(self, customer):
        order = _make_order(customer)
        result = selectors.get_active_quote_for_order(str(order.id))
        assert result is None
