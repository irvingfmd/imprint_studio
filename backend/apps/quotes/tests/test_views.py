"""
Tests de los endpoints de la app quotes.
Casos del plan: 19-23, 24-27, 58, 60, 61.

Endpoints cubiertos:
  GET  /api/v1/quotes/{quote_id}/
  GET  /api/v1/orders/{order_id}/quotes/
  PUT  /api/v1/quotes/{quote_id}/accept/
  PUT  /api/v1/quotes/{quote_id}/reject/
  GET  /api/v1/quotes/{quote_id}/snapshot/  (admin)
  POST /api/v1/admin/orders/{order_id}/quote/
  PUT  /api/v1/admin/quotes/{quote_id}/expire/
  POST /api/v1/admin/calculator/calculate/
"""
import pytest
from decimal import Decimal

from apps.configuration.models import BusinessConfig, Printer
from apps.orders.models import Order, OrderStatus, RequestType
from apps.quotes.models import Quote, QuoteSnapshot, QuoteStatus
from apps.quotes.services import QuoteService


# --- URL helpers ---

def quote_url(quote_id):
    return f"/api/v1/quotes/{quote_id}/"


def order_quotes_url(order_id):
    return f"/api/v1/orders/{order_id}/quotes/"


def accept_url(quote_id):
    return f"/api/v1/quotes/{quote_id}/accept/"


def reject_url(quote_id):
    return f"/api/v1/quotes/{quote_id}/reject/"


def snapshot_url(quote_id):
    return f"/api/v1/quotes/{quote_id}/snapshot/"


def pdf_url(quote_id):
    return f"/api/v1/quotes/{quote_id}/pdf/"


def admin_create_quote_url(order_id):
    return f"/api/v1/admin/orders/{order_id}/quote/"


def admin_expire_url(quote_id):
    return f"/api/v1/admin/quotes/{quote_id}/expire/"


CALCULATOR_URL = "/api/v1/admin/calculator/calculate/"


# --- Helpers de datos ---

def _make_printer(power_watts: int = 250) -> Printer:
    return Printer.objects.create(name="Prueba", brand="Test", power_watts=power_watts)


def _make_config(**kwargs) -> BusinessConfig:
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


def _make_snapshot(quote) -> QuoteSnapshot:
    return QuoteSnapshot.objects.create(
        quote=quote,
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
    )


def _setup_quoted_order(customer, admin_user):
    """Crea pedido en estado QUOTED con una cotización PENDING y su snapshot."""
    config = _make_config()
    order = _make_order(customer)
    quote = QuoteService.create_quote(
        order=order,
        weight_grams=Decimal("250.00"),
        print_time_hours=Decimal("12.50"),
        shipping_cost=Decimal("120.00"),
        created_by=admin_user,
    )
    order.refresh_from_db()
    return order, quote


# --- Detalle de cotización ---

@pytest.mark.django_db
class TestQuoteDetailView:
    def test_sin_token_devuelve_401(self, api_client, customer, admin_user):
        # Caso 58
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        resp = api_client.get(quote_url(quote.id))
        assert resp.status_code == 401

    def test_propietario_puede_ver_cotizacion(self, auth_client, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        resp = auth_client.get(quote_url(quote.id))
        assert resp.status_code == 200
        assert str(quote.id) in str(resp.data["data"]["id"])

    def test_cliente_ajeno_recibe_403(self, api_client, admin_user):
        # Caso 60: cliente accede a recurso ajeno
        from apps.authentication.models import User
        otro = User.objects.create_user(phone="+529611099901", first_name="Otro")
        order = _make_order(otro, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        api_client.force_authenticate(user=admin_user)
        # admin puede verla; usamos un tercer cliente que no es dueño ni admin
        from apps.authentication.models import UserRole
        cliente2 = User.objects.create_user(phone="+529611099902", first_name="Cliente2")
        api_client.force_authenticate(user=cliente2)
        resp = api_client.get(quote_url(quote.id))
        assert resp.status_code == 403

    def test_cotizacion_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(quote_url(uuid.uuid4()))
        assert resp.status_code == 404


# --- Lista de cotizaciones de un pedido ---

@pytest.mark.django_db
class TestOrderQuoteListView:
    def test_sin_token_devuelve_401(self, api_client, customer, admin_user):
        # Caso 58
        order = _make_order(customer, status=OrderStatus.QUOTED)
        resp = api_client.get(order_quotes_url(order.id))
        assert resp.status_code == 401

    def test_cliente_ve_cotizaciones_de_su_pedido(self, auth_client, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        _make_quote_direct(order, admin_user)
        resp = auth_client.get(order_quotes_url(order.id))
        assert resp.status_code == 200
        assert resp.data["data"]["count"] == 1

    def test_cliente_no_ve_cotizaciones_de_pedido_ajeno(self, auth_client, admin_user):
        # Caso 60
        from apps.authentication.models import User
        otro = User.objects.create_user(phone="+529611099903", first_name="Otro")
        order_ajeno = _make_order(otro, status=OrderStatus.QUOTED)
        _make_quote_direct(order_ajeno, admin_user)
        resp = auth_client.get(order_quotes_url(order_ajeno.id))
        assert resp.status_code == 403

    def test_pedido_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(order_quotes_url(uuid.uuid4()))
        assert resp.status_code == 404


# --- Aceptar cotización ---

@pytest.mark.django_db
class TestAcceptQuoteView:
    def test_sin_token_devuelve_401(self, api_client, customer, admin_user):
        # Caso 58
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        resp = api_client.put(accept_url(quote.id), {"payment_option": "DEPOSIT"})
        assert resp.status_code == 401

    def test_acepta_cotizacion_con_deposito(self, auth_client, customer, admin_user):
        """Caso 22: cliente acepta con DEPOSIT."""
        _make_config()
        order, quote = _setup_quoted_order(customer, admin_user)
        resp = auth_client.put(
            accept_url(quote.id),
            {"payment_option": "DEPOSIT"},
            format="json",
        )
        assert resp.status_code == 200
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.ACCEPTED

    def test_acepta_cotizacion_con_pago_completo(self, auth_client, customer, admin_user):
        """Caso 22: cliente acepta con FULL_PAYMENT."""
        _make_config()
        order, quote = _setup_quoted_order(customer, admin_user)
        resp = auth_client.put(
            accept_url(quote.id),
            {"payment_option": "FULL_PAYMENT"},
            format="json",
        )
        assert resp.status_code == 200

    def test_opcion_invalida_devuelve_400(self, auth_client, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        resp = auth_client.put(
            accept_url(quote.id),
            {"payment_option": "EFECTIVO"},
            format="json",
        )
        assert resp.status_code == 400

    def test_cliente_ajeno_recibe_403(self, api_client, customer, admin_user):
        # Caso 60
        from apps.authentication.models import User
        otro = User.objects.create_user(phone="+529611099904", first_name="Otro")
        order = _make_order(otro, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        api_client.force_authenticate(user=customer)
        resp = api_client.put(
            accept_url(quote.id),
            {"payment_option": "DEPOSIT"},
            format="json",
        )
        assert resp.status_code == 403


# --- Rechazar cotización ---

@pytest.mark.django_db
class TestRejectQuoteView:
    def test_sin_token_devuelve_401(self, api_client, customer, admin_user):
        # Caso 58
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        resp = api_client.put(reject_url(quote.id), {})
        assert resp.status_code == 401

    def test_rechaza_cotizacion_pending(self, auth_client, customer, admin_user):
        """Caso 23: cliente rechaza cotización."""
        _make_config()
        order, quote = _setup_quoted_order(customer, admin_user)
        resp = auth_client.put(
            reject_url(quote.id),
            {"reason": "Precio muy alto"},
            format="json",
        )
        assert resp.status_code == 200
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.REJECTED

    def test_rechazar_cotizacion_ya_aceptada_devuelve_400(self, auth_client, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user, status=QuoteStatus.ACCEPTED)
        resp = auth_client.put(reject_url(quote.id), {}, format="json")
        assert resp.status_code == 400

    def test_cliente_ajeno_recibe_403(self, api_client, customer, admin_user):
        # Caso 60
        from apps.authentication.models import User
        otro = User.objects.create_user(phone="+529611099905", first_name="Otro")
        order = _make_order(otro, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        api_client.force_authenticate(user=customer)
        resp = api_client.put(reject_url(quote.id), {}, format="json")
        assert resp.status_code == 403


# --- Snapshot (solo admin) ---

@pytest.mark.django_db
class TestQuoteSnapshotView:
    def test_admin_obtiene_snapshot(self, admin_client, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        _make_snapshot(quote)
        resp = admin_client.get(snapshot_url(quote.id))
        assert resp.status_code == 200
        assert "material_cost_per_kg" in resp.data["data"]

    def test_cliente_en_snapshot_recibe_403(self, auth_client, customer, admin_user):
        # Caso 61: cliente accede a endpoint admin
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        _make_snapshot(quote)
        resp = auth_client.get(snapshot_url(quote.id))
        assert resp.status_code == 403

    def test_sin_token_devuelve_401(self, api_client, customer, admin_user):
        # Caso 58
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        resp = api_client.get(snapshot_url(quote.id))
        assert resp.status_code == 401


# --- Admin: crear cotización ---

@pytest.mark.django_db
class TestAdminCreateQuoteView:
    def test_admin_crea_cotizacion(self, admin_client, customer, admin_user):
        """Caso 19: admin genera cotización."""
        _make_config()
        order = _make_order(customer)
        resp = admin_client.post(
            admin_create_quote_url(order.id),
            {
                "weight_grams": "250.00",
                "print_time_hours": "12.50",
                "shipping_cost": "120.00",
            },
            format="json",
        )
        assert resp.status_code == 201
        assert "quote_id" in resp.data["data"]
        assert "total_price" in resp.data["data"]

    def test_cliente_en_endpoint_admin_recibe_403(self, auth_client, customer):
        # Caso 61
        order = _make_order(customer)
        resp = auth_client.post(
            admin_create_quote_url(order.id),
            {"weight_grams": "250.00", "print_time_hours": "12.50"},
            format="json",
        )
        assert resp.status_code == 403

    def test_sin_token_devuelve_401(self, api_client, customer):
        # Caso 58
        order = _make_order(customer)
        resp = api_client.post(
            admin_create_quote_url(order.id),
            {"weight_grams": "250.00", "print_time_hours": "12.50"},
            format="json",
        )
        assert resp.status_code == 401

    def test_pedido_inexistente_devuelve_404(self, admin_client):
        import uuid
        _make_config()
        resp = admin_client.post(
            admin_create_quote_url(uuid.uuid4()),
            {"weight_grams": "250.00", "print_time_hours": "12.50"},
            format="json",
        )
        assert resp.status_code == 404

    def test_campos_invalidos_devuelven_400(self, admin_client, customer):
        _make_config()
        order = _make_order(customer)
        resp = admin_client.post(
            admin_create_quote_url(order.id),
            {"weight_grams": "0.00", "print_time_hours": "12.50"},
            format="json",
        )
        assert resp.status_code == 400


# --- Admin: expirar cotización ---

@pytest.mark.django_db
class TestAdminExpireQuoteView:
    def test_admin_expira_cotizacion(self, admin_client, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user, status=QuoteStatus.PENDING)
        resp = admin_client.put(admin_expire_url(quote.id))
        assert resp.status_code == 200
        quote.refresh_from_db()
        assert quote.quote_status == QuoteStatus.EXPIRED

    def test_cliente_en_endpoint_admin_recibe_403(self, auth_client, customer, admin_user):
        # Caso 61
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user)
        resp = auth_client.put(admin_expire_url(quote.id))
        assert resp.status_code == 403

    def test_cotizacion_ya_aceptada_devuelve_400(self, admin_client, customer, admin_user):
        order = _make_order(customer, status=OrderStatus.QUOTED)
        quote = _make_quote_direct(order, admin_user, status=QuoteStatus.ACCEPTED)
        resp = admin_client.put(admin_expire_url(quote.id))
        assert resp.status_code == 400


# --- Calculadora ---

@pytest.mark.django_db
class TestCalculatorView:
    def test_admin_calcula_precio_normal(self, admin_client):
        """Caso 24: resultado con valores del ejemplo oficial (impresora 250W)."""
        _make_config()
        printer = _make_printer(power_watts=250)
        resp = admin_client.post(
            CALCULATOR_URL,
            {
                "weight_grams": "250.00",
                "print_time_hours": "12.50",
                "priority": "NORMAL",
                "shipping_cost": "120.00",
                "full_payment_selected": False,
                "printer_id": str(printer.id),
            },
            format="json",
        )
        assert resp.status_code == 200
        data = resp.data["data"]
        assert data["total_price"] == Decimal("436.48")
        assert data["discount_amount"] == Decimal("0.00")

    def test_calcula_con_pago_completo(self, admin_client):
        """Caso 27: descuento de 5% aplicado (impresora 250W)."""
        _make_config()
        printer = _make_printer(power_watts=250)
        resp = admin_client.post(
            CALCULATOR_URL,
            {
                "weight_grams": "250.00",
                "print_time_hours": "12.50",
                "priority": "NORMAL",
                "shipping_cost": "120.00",
                "full_payment_selected": True,
                "printer_id": str(printer.id),
            },
            format="json",
        )
        assert resp.status_code == 200
        data = resp.data["data"]
        # El cálculo usa intermedios exactos: total_price real = 414.65 (ver test_services)
        assert data["discount_amount"] == Decimal("21.82")
        assert data["total_price"] == Decimal("414.65")

    def test_cliente_en_endpoint_admin_recibe_403(self, auth_client):
        # Caso 61
        _make_config()
        resp = auth_client.post(
            CALCULATOR_URL,
            {"weight_grams": "100.00", "print_time_hours": "5.00", "priority": "NORMAL"},
            format="json",
        )
        assert resp.status_code == 403

    def test_sin_token_devuelve_401(self, api_client):
        # Caso 58
        resp = api_client.post(CALCULATOR_URL, {})
        assert resp.status_code == 401

    def test_campos_invalidos_devuelven_400(self, admin_client):
        _make_config()
        resp = admin_client.post(
            CALCULATOR_URL,
            {"weight_grams": "0.00", "print_time_hours": "5.00", "priority": "NORMAL"},
            format="json",
        )
        assert resp.status_code == 400


# --- PDF de cotización ---

@pytest.mark.django_db
class TestQuotePDFView:
    def test_propietario_descarga_pdf(self, auth_client, customer, admin_user):
        _make_config()
        order, quote = _setup_quoted_order(customer, admin_user)
        resp = auth_client.get(pdf_url(quote.id))
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"
        assert b"%PDF" in resp.content

    def test_admin_descarga_pdf_de_cualquier_pedido(self, admin_client, customer, admin_user):
        _make_config()
        order, quote = _setup_quoted_order(customer, admin_user)
        resp = admin_client.get(pdf_url(quote.id))
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"

    def test_pdf_incluye_header_de_descarga(self, auth_client, customer, admin_user):
        _make_config()
        order, quote = _setup_quoted_order(customer, admin_user)
        resp = auth_client.get(pdf_url(quote.id))
        assert "Content-Disposition" in resp
        assert "attachment" in resp["Content-Disposition"]
        assert "cotizacion-" in resp["Content-Disposition"]

    def test_cliente_ajeno_recibe_403(self, api_client, admin_user):
        from apps.authentication.models import User
        _make_config()
        otro = User.objects.create_user(phone="+529611099910", first_name="Otro")
        order = _make_order(otro)
        quote = _make_quote_direct(order, admin_user)
        cliente2 = User.objects.create_user(phone="+529611099911", first_name="Cliente2")
        api_client.force_authenticate(user=cliente2)
        resp = api_client.get(pdf_url(quote.id))
        assert resp.status_code == 403

    def test_cotizacion_inexistente_devuelve_404(self, auth_client):
        import uuid
        resp = auth_client.get(pdf_url(uuid.uuid4()))
        assert resp.status_code == 404

    def test_sin_token_devuelve_401(self, api_client, customer, admin_user):
        _make_config()
        order, quote = _setup_quoted_order(customer, admin_user)
        resp = api_client.get(pdf_url(quote.id))
        assert resp.status_code == 401
