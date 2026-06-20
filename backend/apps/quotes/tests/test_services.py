"""
Tests de servicios de la app quotes.
Casos del plan: 19-27, 30, 31, 54.

QuoteCalculatorService: cobertura 100% requerida.
QuoteService: create, accept, reject, expire.
"""

from decimal import Decimal

import pytest

from apps.configuration.models import BusinessConfig, Printer
from apps.orders.models import EventType, Order, OrderEvent, OrderStatus, RequestType
from apps.payments.models import Payment, PaymentType
from apps.quotes.models import Quote, QuoteSnapshot, QuoteStatus
from apps.quotes.services import QuoteCalculatorService, QuoteService

# --- Helpers de fixtures ---


def _make_config(**kwargs) -> BusinessConfig:
    """
    Crea BusinessConfig con valores del documento 05-cost-calculator.md.
    electricity_rate_kwh=2.0 MXN/kWh (tarifa CFE inicial).
    """
    defaults = dict(
        material_cost_per_kg=Decimal("25.00"),
        electricity_rate_kwh=Decimal("2.0000"),
        labor_cost_per_hour=Decimal("15.00"),
        post_processing_cost_per_gram=Decimal("0.05"),
        packaging_cost=Decimal("2.00"),
        failure_percentage=Decimal("10.00"),
        profit_margin_percentage=Decimal("30.00"),
        urgent_multiplier=Decimal("1.30"),
        express_multiplier=Decimal("1.50"),
        full_payment_discount_percentage=Decimal("5.00"),
        deposit_deadline_hours=48,
        balance_deadline_days=7,
    )
    defaults.update(kwargs)
    return BusinessConfig.objects.create(**defaults)


def _make_printer(power_watts: int = 250, **kwargs) -> Printer:
    """
    Crea una impresora en el catálogo.
    250W reproduce el ejemplo oficial: (250/1000) × 12.5h × 2.0 MXN/kWh = 6.25 MXN.
    """
    kwargs.setdefault("name", "Prueba")
    kwargs.setdefault("brand", "Test")
    return Printer.objects.create(
        power_watts=power_watts,
        **kwargs,
    )


def _make_order(customer, status=OrderStatus.RECEIVED, priority="NORMAL") -> Order:
    return Order.objects.create(
        customer=customer,
        request_type=RequestType.REFERENCE,
        title="Casco Mandaloriano",
        description="Escala 1:1",
        quantity=1,
        priority=priority,
        status=status,
    )


def _make_quote_direct(order, admin_user, status=QuoteStatus.PENDING) -> Quote:
    """Crea un Quote directamente sin usar el servicio (para aislar pruebas)."""
    return Quote.objects.create(
        order=order,
        created_by=admin_user,
        weight_grams=Decimal("250.00"),
        print_time_hours=Decimal("12.50"),
        material_cost=Decimal("6.25"),
        energy_cost=Decimal("6.25"),
        labor_cost=Decimal("187.50"),
        post_processing_cost=Decimal("12.50"),
        packaging_cost=Decimal("2.00"),
        risk_cost=Decimal("1.25"),
        shipping_cost=Decimal("120.00"),
        subtotal=Decimal("335.75"),
        profit_amount=Decimal("100.73"),
        discount_amount=Decimal("0.00"),
        total_price=Decimal("436.48"),
        quote_status=status,
    )


# --- QuoteCalculatorService ---


@pytest.mark.django_db
class TestQuoteCalculatorService:
    """Cobertura 100% requerida por el plan de pruebas."""

    def test_calculo_normal_coincide_con_ejemplo_oficial(self, db):
        """
        Caso 24: ejemplo del documento 05-cost-calculator.md.
        weight=250g, time=12.5h, NORMAL, shipping=120, full_payment=False.
        Impresora 250W + tarifa 2.0 MXN/kWh → energy = (250/1000)×12.5×2.0 = 6.25 MXN.
        """
        config = _make_config()
        printer = _make_printer(power_watts=250)
        result = QuoteCalculatorService.calculate(
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            priority="NORMAL",
            shipping_cost=Decimal("120.00"),
            full_payment_selected=False,
            printer=printer,
            config=config,
        )
        assert result["material_cost"] == Decimal("6.25")
        assert result["energy_cost"] == Decimal("6.25")
        assert result["labor_cost"] == Decimal("187.50")
        assert result["post_processing_cost"] == Decimal("12.50")
        assert result["packaging_cost"] == Decimal("2.00")
        assert result["risk_cost"] == Decimal("1.25")
        assert result["subtotal"] == Decimal("335.75")
        assert result["profit_amount"] == Decimal("100.73")
        assert result["discount_amount"] == Decimal("0.00")
        assert result["tax_amount"] == Decimal("69.84")
        assert result["total_price"] == Decimal("506.31")

    def test_calculo_urgente_aplica_multiplicador(self, db):
        """Caso 25: prioridad URGENT aplica urgent_multiplier = 1.30."""
        config = _make_config()
        printer = _make_printer()
        normal = QuoteCalculatorService.calculate(
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            printer=printer,
            config=config,
        )
        urgent = QuoteCalculatorService.calculate(
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            priority="URGENT",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            printer=printer,
            config=config,
        )
        assert urgent["priority_multiplier"] == Decimal("1.30")
        assert urgent["total_price"] > normal["total_price"]

    def test_calculo_express_aplica_multiplicador(self, db):
        """Caso 26: prioridad EXPRESS aplica express_multiplier = 1.50."""
        config = _make_config()
        printer = _make_printer()
        normal = QuoteCalculatorService.calculate(
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            printer=printer,
            config=config,
        )
        express = QuoteCalculatorService.calculate(
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            priority="EXPRESS",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            printer=printer,
            config=config,
        )
        assert express["priority_multiplier"] == Decimal("1.50")
        assert express["total_price"] > normal["total_price"]

    def test_descuento_pago_completo_es_cinco_porciento(self, db):
        """Caso 27: descuento de pago completo = 5% sobre total antes de descuento."""
        config = _make_config()
        printer = _make_printer(power_watts=250)
        result = QuoteCalculatorService.calculate(
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            priority="NORMAL",
            shipping_cost=Decimal("120.00"),
            full_payment_selected=True,
            printer=printer,
            config=config,
        )
        # El documento muestra 414.66, pero usa total_before_discount redondeado (436.48).
        # El código opera con el valor exacto (436.475), por eso el total real es 414.65.
        assert result["discount_amount"] == Decimal("21.82")
        assert result["tax_amount"] == Decimal("66.34")
        assert result["total_price"] == Decimal("481.00")

    def test_sin_pago_completo_no_hay_descuento(self, db):
        config = _make_config()
        result = QuoteCalculatorService.calculate(
            weight_grams=Decimal("100.00"),
            print_time_hours=Decimal("5.00"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            config=config,
        )
        assert result["discount_amount"] == Decimal("0.00")

    def test_sin_envio_shipping_cost_es_cero(self, db):
        config = _make_config()
        result = QuoteCalculatorService.calculate(
            weight_grams=Decimal("100.00"),
            print_time_hours=Decimal("5.00"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            config=config,
        )
        assert result["shipping_cost"] == Decimal("0.00")

    def test_con_envio_incluye_en_subtotal(self, db):
        config = _make_config()
        sin_envio = QuoteCalculatorService.calculate(
            weight_grams=Decimal("100.00"),
            print_time_hours=Decimal("5.00"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            config=config,
        )
        con_envio = QuoteCalculatorService.calculate(
            weight_grams=Decimal("100.00"),
            print_time_hours=Decimal("5.00"),
            priority="NORMAL",
            shipping_cost=Decimal("100.00"),
            full_payment_selected=False,
            config=config,
        )
        assert con_envio["subtotal"] > sin_envio["subtotal"]
        assert con_envio["total_price"] > sin_envio["total_price"]

    def test_sin_impresora_energy_cost_es_cero(self, db):
        """Sin impresora no se puede calcular energía → energy_cost = 0.00."""
        config = _make_config()
        result = QuoteCalculatorService.calculate(
            weight_grams=Decimal("200.00"),
            print_time_hours=Decimal("8.00"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            config=config,
        )
        assert result["energy_cost"] == Decimal("0.00")

    def test_impresora_mas_potente_genera_mayor_energy_cost(self, db):
        """Impresora de 400W consume más que una de 150W al mismo tiempo."""
        config = _make_config()
        low = _make_printer(power_watts=150, name="Low", brand="A")
        high = _make_printer(power_watts=400, name="High", brand="B")
        r_low = QuoteCalculatorService.calculate(
            weight_grams=Decimal("100.00"),
            print_time_hours=Decimal("5.00"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            printer=low,
            config=config,
        )
        r_high = QuoteCalculatorService.calculate(
            weight_grams=Decimal("100.00"),
            print_time_hours=Decimal("5.00"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            printer=high,
            config=config,
        )
        assert r_high["energy_cost"] > r_low["energy_cost"]

    def test_prioridad_invalida_lanza_value_error(self, db):
        config = _make_config()
        with pytest.raises(ValueError, match="Prioridad inválida"):
            QuoteCalculatorService.calculate(
                weight_grams=Decimal("100.00"),
                print_time_hours=Decimal("5.00"),
                priority="SUPER",
                shipping_cost=Decimal("0.00"),
                full_payment_selected=False,
                config=config,
            )

    def test_sin_config_activa_lanza_value_error(self, db):
        # No hay BusinessConfig en la DB → debe lanzar error
        with pytest.raises(ValueError, match="No existe configuración"):
            QuoteCalculatorService.calculate(
                weight_grams=Decimal("100.00"),
                print_time_hours=Decimal("5.00"),
                priority="NORMAL",
                shipping_cost=Decimal("0.00"),
                full_payment_selected=False,
            )

    def test_todos_los_montos_son_decimal(self, db):
        """Caso 31: verificar que no se usan floats en resultados."""
        config = _make_config()
        printer = _make_printer()
        result = QuoteCalculatorService.calculate(
            weight_grams=Decimal("100.00"),
            print_time_hours=Decimal("5.00"),
            priority="NORMAL",
            shipping_cost=Decimal("50.00"),
            full_payment_selected=False,
            printer=printer,
            config=config,
        )
        campos_monetarios = [
            "material_cost",
            "energy_cost",
            "labor_cost",
            "post_processing_cost",
            "packaging_cost",
            "risk_cost",
            "shipping_cost",
            "subtotal",
            "profit_amount",
            "discount_amount",
            "total_price",
        ]
        for campo in campos_monetarios:
            assert isinstance(result[campo], Decimal), f"{campo} no es Decimal"

    def test_redondeo_a_dos_decimales(self, db):
        """Caso 30: todos los montos tienen exactamente 2 decimales."""
        config = _make_config()
        printer = _make_printer()
        result = QuoteCalculatorService.calculate(
            weight_grams=Decimal("333.33"),
            print_time_hours=Decimal("7.77"),
            priority="URGENT",
            shipping_cost=Decimal("85.00"),
            full_payment_selected=True,
            printer=printer,
            config=config,
        )
        campos_monetarios = [
            "material_cost",
            "energy_cost",
            "labor_cost",
            "post_processing_cost",
            "packaging_cost",
            "risk_cost",
            "subtotal",
            "profit_amount",
            "discount_amount",
            "total_price",
        ]
        for campo in campos_monetarios:
            valor = result[campo]
            # Verifica que el valor ya está redondeado a 2 decimales
            assert valor == valor.quantize(Decimal("0.01")), f"{campo}={valor} no está redondeado a 2 decimales"

    def test_config_recibida_externamente(self, db):
        """Cuando se pasa config, no debe ir a la DB a buscarla."""
        config = _make_config()
        result = QuoteCalculatorService.calculate(
            weight_grams=Decimal("100.00"),
            print_time_hours=Decimal("5.00"),
            priority="NORMAL",
            shipping_cost=Decimal("0.00"),
            full_payment_selected=False,
            config=config,
        )
        assert result["config"] == config


# --- QuoteService ---


@pytest.mark.django_db
class TestCreateQuote:
    def test_crea_cotizacion_para_el_pedido(self, customer, admin_user):
        """Caso 19: admin genera cotización."""
        _make_config()
        order = _make_order(customer)
        quote = QuoteService.create_quote(
            order=order,
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            shipping_cost=Decimal("120.00"),
            created_by=admin_user,
        )
        assert quote.id is not None
        assert quote.quote_status == QuoteStatus.PENDING
        assert quote.order == order
        assert quote.created_by == admin_user

    def test_crea_snapshot(self, customer, admin_user):
        """Caso 20: snapshot de configuración creado."""
        _make_config()
        order = _make_order(customer)
        quote = QuoteService.create_quote(
            order=order,
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            shipping_cost=Decimal("0.00"),
            created_by=admin_user,
        )
        assert QuoteSnapshot.objects.filter(quote=quote).exists()

    def test_crea_evento_quote_created(self, customer, admin_user):
        """Casos 21, 54: evento QUOTE_CREATED generado."""
        _make_config()
        order = _make_order(customer)
        quote = QuoteService.create_quote(
            order=order,
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            shipping_cost=Decimal("0.00"),
            created_by=admin_user,
        )
        evento = OrderEvent.objects.filter(
            order=order,
            event_type=EventType.QUOTE_CREATED,
        ).first()
        assert evento is not None
        assert str(quote.id) in evento.metadata["quote_id"]

    def test_invalida_cotizaciones_pending_previas(self, customer, admin_user):
        """Solo puede existir una PENDING activa por pedido."""
        _make_config()
        order = _make_order(customer)
        QuoteService.create_quote(
            order=order,
            weight_grams=Decimal("200.00"),
            print_time_hours=Decimal("10.00"),
            shipping_cost=Decimal("0.00"),
            created_by=admin_user,
        )
        # La primera cotización queda QUOTED después de la transición;
        # la segunda debe invalidar cualquier PENDING del mismo pedido
        # Ponemos la primera de vuelta a PENDING manualmente para simular el caso
        Quote.objects.filter(order=order).update(quote_status=QuoteStatus.PENDING)
        order.status = OrderStatus.RECEIVED
        order.save()
        QuoteService.create_quote(
            order=order,
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            shipping_cost=Decimal("0.00"),
            created_by=admin_user,
        )
        pendientes = Quote.objects.filter(
            order=order,
            quote_status=QuoteStatus.PENDING,
        ).count()
        assert pendientes == 1

    def test_transiciona_pedido_a_quoted(self, customer, admin_user):
        _make_config()
        order = _make_order(customer)
        QuoteService.create_quote(
            order=order,
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            shipping_cost=Decimal("0.00"),
            created_by=admin_user,
        )
        order.refresh_from_db()
        assert order.status == OrderStatus.QUOTED


@pytest.mark.django_db
class TestAcceptQuote:
    def _setup(self, customer, admin_user):
        """Crea un pedido en QUOTED con una cotización PENDING."""
        _make_config()
        order = _make_order(customer)
        QuoteService.create_quote(
            order=order,
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            shipping_cost=Decimal("120.00"),
            created_by=admin_user,
        )
        order.refresh_from_db()
        quote = Quote.objects.get(order=order, quote_status=QuoteStatus.PENDING)
        return order, quote

    def test_acepta_cotizacion_pending_con_deposito(self, customer, admin_user):
        """Caso 22: cliente acepta con DEPOSIT."""
        order, quote = self._setup(customer, admin_user)
        QuoteService.accept_quote(quote=quote, payment_option="DEPOSIT", user=customer)
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.ACCEPTED
        assert quote.accepted_at is not None

    def test_deposito_crea_pago_por_la_mitad(self, customer, admin_user):
        """Caso 22: DEPOSIT → monto = total / 2."""
        order, quote = self._setup(customer, admin_user)
        total_original = quote.total_price
        QuoteService.accept_quote(quote=quote, payment_option="DEPOSIT", user=customer)
        pago = Payment.objects.filter(order=order, payment_type=PaymentType.DEPOSIT).first()
        assert pago is not None
        from decimal import ROUND_HALF_UP

        expected = (total_original / Decimal("2")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        assert pago.amount == expected

    def test_pago_completo_aplica_descuento(self, customer, admin_user):
        """Caso 22 + 27: FULL_PAYMENT aplica descuento del snapshot."""
        order, quote = self._setup(customer, admin_user)
        total_sin_descuento = quote.total_price
        QuoteService.accept_quote(quote=quote, payment_option="FULL_PAYMENT", user=customer)
        quote.refresh_from_db()
        assert quote.discount_amount > Decimal("0.00")
        assert quote.total_price < total_sin_descuento

    def test_lanza_error_si_no_es_pending(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user, status=QuoteStatus.ACCEPTED)
        with pytest.raises(ValueError, match="PENDING"):
            QuoteService.accept_quote(quote=quote, payment_option="DEPOSIT", user=customer)

    def test_lanza_error_si_no_es_el_propietario(self, customer, admin_user):
        order, quote = self._setup(customer, admin_user)
        with pytest.raises(ValueError, match="propietario"):
            QuoteService.accept_quote(quote=quote, payment_option="DEPOSIT", user=admin_user)

    def test_crea_evento_quote_accepted(self, customer, admin_user):
        order, quote = self._setup(customer, admin_user)
        QuoteService.accept_quote(quote=quote, payment_option="DEPOSIT", user=customer)
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.QUOTE_ACCEPTED,
        ).exists()


@pytest.mark.django_db
class TestRejectQuote:
    def _setup(self, customer, admin_user):
        _make_config()
        order = _make_order(customer)
        QuoteService.create_quote(
            order=order,
            weight_grams=Decimal("250.00"),
            print_time_hours=Decimal("12.50"),
            shipping_cost=Decimal("0.00"),
            created_by=admin_user,
        )
        order.refresh_from_db()
        quote = Quote.objects.get(order=order, quote_status=QuoteStatus.PENDING)
        return order, quote

    def test_rechaza_cotizacion_pending(self, customer, admin_user):
        """Caso 23: cliente rechaza cotización."""
        order, quote = self._setup(customer, admin_user)
        QuoteService.reject_quote(quote=quote, user=customer, reason="Muy caro")
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.REJECTED
        assert quote.rejected_at is not None

    def test_lanza_error_si_no_es_pending(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user, status=QuoteStatus.EXPIRED)
        with pytest.raises(ValueError, match="PENDING"):
            QuoteService.reject_quote(quote=quote, user=customer)

    def test_lanza_error_si_no_es_el_propietario(self, customer, admin_user):
        order, quote = self._setup(customer, admin_user)
        with pytest.raises(ValueError, match="propietario"):
            QuoteService.reject_quote(quote=quote, user=admin_user)

    def test_crea_evento_quote_rejected(self, customer, admin_user):
        order, quote = self._setup(customer, admin_user)
        QuoteService.reject_quote(quote=quote, user=customer, reason="No me gusta el precio")
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.QUOTE_REJECTED,
        ).exists()


@pytest.mark.django_db
class TestExpireQuote:
    def test_expira_cotizacion_pending(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user, status=QuoteStatus.PENDING)
        QuoteService.expire_quote(quote=quote, admin=admin_user)
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.EXPIRED

    def test_lanza_error_si_no_es_pending(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user, status=QuoteStatus.ACCEPTED)
        with pytest.raises(ValueError, match="PENDING"):
            QuoteService.expire_quote(quote=quote, admin=admin_user)

    def test_crea_evento_status_changed(self, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user, status=QuoteStatus.PENDING)
        QuoteService.expire_quote(quote=quote, admin=admin_user)
        assert OrderEvent.objects.filter(
            order=order,
            event_type=EventType.STATUS_CHANGED,
        ).exists()
