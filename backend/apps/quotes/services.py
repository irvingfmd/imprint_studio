"""
Servicios para la app quotes.

QuoteCalculatorService: calcula precios según docs/business/05-cost-calculator.md.
QuoteService: crea, acepta, rechaza y expira cotizaciones.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from apps.configuration.models import BusinessConfig, Printer
from apps.notifications.services import NotificationService
from apps.orders.models import EventType, Order, OrderEvent, OrderPaymentStatus, OrderStatus

from .models import Quote, QuoteSnapshot, QuoteStatus


def _round_money(value: Decimal) -> Decimal:
    """Redondea importes monetarios a dos decimales con ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class QuoteCalculatorService:
    """
    Calcula el precio de una cotización.
    Fórmula oficial: docs/business/05-cost-calculator.md.
    Usa exclusivamente Decimal para toda operación financiera.
    """

    @staticmethod
    def calculate(
        weight_grams: Decimal,
        print_time_hours: Decimal,
        priority: str,
        shipping_cost: Decimal,
        full_payment_selected: bool,
        printer: "Printer | None" = None,
        config: BusinessConfig | None = None,
        include_post_processing: bool = True,
    ) -> dict:
        """
        Calcula el desglose de costos.
        Si no se pasa config, obtiene el registro activo de BusinessConfig.
        energy_cost = (printer.power_watts / 1000) × horas × tarifa_kwh
        """
        if config is None:
            config = BusinessConfig.objects.filter(is_active=True).first()
            if config is None:
                raise ValueError("No existe configuración de negocio activa.")

        material_cost = (weight_grams / Decimal("1000")) * config.material_cost_per_kg

        if printer is not None:
            energy_cost = (
                (Decimal(printer.power_watts) / Decimal("1000")) * print_time_hours * config.electricity_rate_kwh
            )
        else:
            # Fallback: sin impresora usa solo la tarifa por hora equivalente a 0W
            energy_cost = Decimal("0.00")

        labor_cost = print_time_hours * config.labor_cost_per_hour
        post_processing_cost = (weight_grams * config.post_processing_cost_per_gram) if include_post_processing else Decimal("0.00")
        packaging_cost = config.packaging_cost
        risk_cost = (material_cost + energy_cost) * (config.failure_percentage / Decimal("100"))

        base_cost = material_cost + energy_cost + labor_cost + post_processing_cost + packaging_cost + risk_cost

        if priority == "NORMAL":
            priority_multiplier = Decimal("1.00")
        elif priority == "URGENT":
            priority_multiplier = config.urgent_multiplier
        elif priority == "EXPRESS":
            priority_multiplier = config.express_multiplier
        else:
            raise ValueError(f"Prioridad inválida: {priority}")

        priority_cost = base_cost * priority_multiplier
        subtotal = priority_cost + shipping_cost
        profit_amount = subtotal * (config.profit_margin_percentage / Decimal("100"))
        total_before_discount = subtotal + profit_amount

        discount_amount = Decimal("0.00")
        if full_payment_selected:
            discount_amount = total_before_discount * (config.full_payment_discount_percentage / Decimal("100"))

        price_before_tax = total_before_discount - discount_amount
        tax_amount = price_before_tax * (config.tax_percentage / Decimal("100"))
        total_price = price_before_tax + tax_amount

        return {
            "material_cost": _round_money(material_cost),
            "energy_cost": _round_money(energy_cost),
            "labor_cost": _round_money(labor_cost),
            "post_processing_cost": _round_money(post_processing_cost),
            "packaging_cost": _round_money(packaging_cost),
            "risk_cost": _round_money(risk_cost),
            "base_cost": _round_money(base_cost),
            "priority_multiplier": priority_multiplier,
            "priority_cost": _round_money(priority_cost),
            "shipping_cost": _round_money(shipping_cost),
            "subtotal": _round_money(subtotal),
            "profit_amount": _round_money(profit_amount),
            "discount_amount": _round_money(discount_amount),
            "tax_amount": _round_money(tax_amount),
            "total_price": _round_money(total_price),
            "config": config,
            "printer": printer,
        }


class QuoteService:
    @staticmethod
    @transaction.atomic
    def create_quote(
        order: Order,
        weight_grams: Decimal,
        print_time_hours: Decimal,
        shipping_cost: Decimal,
        created_by,
        printer_id: str | None = None,
        include_post_processing: bool = True,
    ) -> Quote:
        """
        Crea una cotización para el pedido con datos reales de Bambu Studio.
        Invalida cotizaciones PENDING previas del mismo pedido.
        Crea el QuoteSnapshot y el evento QUOTE_CREATED.
        Notifica al cliente.
        """
        printer: Printer | None = None
        if printer_id:
            try:
                printer = Printer.objects.get(id=printer_id, is_active=True)
            except Printer.DoesNotExist:
                raise ValueError("Impresora no encontrada o inactiva.")

        # Invalida cotizaciones PENDING previas
        Quote.objects.filter(
            order=order,
            quote_status=QuoteStatus.PENDING,
            is_deleted=False,
        ).update(quote_status=QuoteStatus.EXPIRED)

        result = QuoteCalculatorService.calculate(
            weight_grams=weight_grams,
            print_time_hours=print_time_hours,
            priority=order.priority,
            shipping_cost=shipping_cost,
            full_payment_selected=False,
            printer=printer,
            include_post_processing=include_post_processing,
        )
        config: BusinessConfig = result["config"]

        # Las cotizaciones vencen a los 7 días si el cliente no responde.
        quote_expires_at = timezone.now() + timezone.timedelta(days=7)

        quote = Quote.objects.create(
            order=order,
            created_by=created_by,
            printer=printer,
            weight_grams=weight_grams,
            print_time_hours=print_time_hours,
            material_cost=result["material_cost"],
            energy_cost=result["energy_cost"],
            labor_cost=result["labor_cost"],
            post_processing_cost=result["post_processing_cost"],
            packaging_cost=result["packaging_cost"],
            risk_cost=result["risk_cost"],
            shipping_cost=result["shipping_cost"],
            subtotal=result["subtotal"],
            profit_amount=result["profit_amount"],
            discount_amount=Decimal("0.00"),
            tax_amount=result["tax_amount"],
            total_price=result["total_price"],
            quote_status=QuoteStatus.PENDING,
            expires_at=quote_expires_at,
        )

        QuoteSnapshot.objects.create(
            quote=quote,
            material_cost_per_kg=config.material_cost_per_kg,
            electricity_rate_kwh=config.electricity_rate_kwh,
            labor_cost_per_hour=config.labor_cost_per_hour,
            post_processing_cost_per_gram=config.post_processing_cost_per_gram,
            packaging_cost=config.packaging_cost,
            failure_percentage=config.failure_percentage,
            profit_margin_percentage=config.profit_margin_percentage,
            urgent_multiplier=config.urgent_multiplier,
            express_multiplier=config.express_multiplier,
            full_payment_discount_percentage=config.full_payment_discount_percentage,
            tax_percentage=config.tax_percentage,
            printer_name=str(printer) if printer else "",
            printer_power_watts=printer.power_watts if printer else None,
        )

        # Transición de estado: RECEIVED/PENDING_ANALYSIS → QUOTED
        from apps.production.services import OrderStatusTransitionService

        OrderStatusTransitionService.transition(
            order=order,
            new_status=OrderStatus.QUOTED,
            changed_by=created_by,
            notes=f"Cotización #{quote.id} generada. Total: ${quote.total_price}",
        )

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.QUOTE_CREATED,
            event_description=f"Cotización creada. Total: ${quote.total_price} MXN.",
            metadata={"quote_id": str(quote.id), "total_price": str(quote.total_price)},
            created_by=created_by,
        )

        NotificationService.notify_quote_ready(order)

        return quote

    @staticmethod
    @transaction.atomic
    def accept_quote(quote: Quote, payment_option: str, user) -> Quote:
        """
        El cliente acepta la cotización.
        Transiciona el pedido a APPROVED → PENDING_DEPOSIT.
        Crea un Payment PENDING con el monto correspondiente.
        """
        if quote.quote_status != QuoteStatus.PENDING:
            raise ValueError(
                f"Solo se puede aceptar una cotización en estado PENDING. Estado actual: {quote.quote_status}"
            )
        if quote.order.customer_id != user.id:
            raise ValueError("Solo el propietario del pedido puede aceptar la cotización.")

        order = quote.order
        now = timezone.now()

        # Aplica descuento para pago completo
        discount_amount = Decimal("0.00")
        tax_amount = quote.tax_amount
        if payment_option == "FULL_PAYMENT":
            try:
                snapshot = quote.snapshot
                price_before_tax = quote.total_price - quote.tax_amount
                discount_amount = _round_money(
                    price_before_tax * (snapshot.full_payment_discount_percentage / Decimal("100"))
                )
                new_base = price_before_tax - discount_amount
                tax_amount = _round_money(new_base * (snapshot.tax_percentage / Decimal("100")))
            except Quote.snapshot.RelatedObjectDoesNotExist:
                pass

        final_total = quote.total_price - quote.tax_amount - discount_amount + tax_amount
        quote.discount_amount = discount_amount
        quote.tax_amount = tax_amount
        quote.total_price = final_total
        quote.quote_status = QuoteStatus.ACCEPTED
        quote.accepted_at = now
        quote.save(update_fields=["discount_amount", "tax_amount", "total_price", "quote_status", "accepted_at", "updated_at"])

        # Monto del pago según modalidad
        from apps.payments.models import Payment, PaymentMethod, PaymentStatus, PaymentType

        if payment_option == "DEPOSIT":
            payment_type = PaymentType.DEPOSIT
            payment_amount = _round_money(final_total / Decimal("2"))
        else:
            payment_type = PaymentType.FULL_PAYMENT
            payment_amount = final_total

        Payment.objects.create(
            order=order,
            amount=payment_amount,
            payment_type=payment_type,
            payment_method=PaymentMethod.BANK_TRANSFER,
            payment_status=PaymentStatus.PENDING,
        )

        # payment_status del pedido → DEPOSIT_PENDING
        order.payment_status = OrderPaymentStatus.DEPOSIT_PENDING
        order.save(update_fields=["payment_status", "updated_at"])

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.QUOTE_ACCEPTED,
            event_description=f"Cotización aceptada. Opción de pago: {payment_option}.",
            metadata={
                "quote_id": str(quote.id),
                "payment_option": payment_option,
                "amount": str(payment_amount),
            },
            created_by=user,
        )

        # Transición de estado: QUOTED → APPROVED → PENDING_DEPOSIT
        from apps.production.services import OrderStatusTransitionService

        OrderStatusTransitionService.transition(
            order=order,
            new_status=OrderStatus.APPROVED,
            changed_by=user,
            notes=f"Cotización aceptada por el cliente. Opción: {payment_option}.",
        )
        OrderStatusTransitionService.transition(
            order=order,
            new_status=OrderStatus.PENDING_DEPOSIT,
            changed_by=user,
            notes="Esperando anticipo.",
        )

        return quote

    @staticmethod
    @transaction.atomic
    def reject_quote(quote: Quote, user, reason: str = "") -> Quote:
        """El cliente rechaza la cotización."""
        if quote.quote_status != QuoteStatus.PENDING:
            raise ValueError(
                f"Solo se puede rechazar una cotización en estado PENDING. Estado actual: {quote.quote_status}"
            )
        if quote.order.customer_id != user.id:
            raise ValueError("Solo el propietario del pedido puede rechazar la cotización.")

        quote.quote_status = QuoteStatus.REJECTED
        quote.rejected_at = timezone.now()
        quote.save(update_fields=["quote_status", "rejected_at", "updated_at"])

        OrderEvent.objects.create(
            order=quote.order,
            event_type=EventType.QUOTE_REJECTED,
            event_description=f"Cotización rechazada. Razón: {reason or 'Sin especificar.'}",
            metadata={"quote_id": str(quote.id), "reason": reason},
            created_by=user,
        )

        return quote

    @staticmethod
    @transaction.atomic
    def expire_quote(quote: Quote, admin) -> Quote:
        """El administrador marca una cotización como expirada."""
        if quote.quote_status != QuoteStatus.PENDING:
            raise ValueError(
                f"Solo se puede expirar una cotización en estado PENDING. Estado actual: {quote.quote_status}"
            )

        quote.quote_status = QuoteStatus.EXPIRED
        quote.save(update_fields=["quote_status", "updated_at"])

        OrderEvent.objects.create(
            order=quote.order,
            event_type=EventType.STATUS_CHANGED,
            event_description=f"Cotización {quote.id} marcada como expirada.",
            metadata={"quote_id": str(quote.id)},
            created_by=admin,
        )

        return quote
