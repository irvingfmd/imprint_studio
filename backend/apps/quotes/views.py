"""
Vistas para la app quotes.
"""
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from apps.orders.selectors import get_order_by_id

from . import selectors, services
from .pdf_service import QuotePDFService
from .serializers import (
    AcceptQuoteSerializer,
    CalculateSerializer,
    CreateQuoteSerializer,
    QuoteSerializer,
    QuoteSnapshotSerializer,
    RejectQuoteSerializer,
)


# --- Vistas para clientes ---

class QuoteDetailView(APIView):
    """Detalle de una cotización. Solo el propietario del pedido o admin."""

    permission_classes = [IsAuthenticated]

    def get(self, request, quote_id):
        quote = selectors.get_quote_by_id(str(quote_id))
        if not quote:
            return error_response("Quote not found", status_code=status.HTTP_404_NOT_FOUND)
        if quote.order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)
        serializer = QuoteSerializer(quote)
        return success_response(data=serializer.data, message="Quote retrieved")


class OrderQuoteListView(APIView):
    """Lista las cotizaciones de un pedido."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        quotes = selectors.get_quotes_for_order(str(order_id))
        serializer = QuoteSerializer(quotes, many=True)
        return success_response(
            data={"count": quotes.count(), "results": serializer.data},
            message="Quotes retrieved",
        )


class AcceptQuoteView(APIView):
    """El cliente acepta una cotización y elige modalidad de pago."""

    permission_classes = [IsAuthenticated]

    def put(self, request, quote_id):
        serializer = AcceptQuoteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        quote = selectors.get_quote_by_id(str(quote_id))
        if not quote:
            return error_response("Quote not found", status_code=status.HTTP_404_NOT_FOUND)
        if quote.order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        try:
            services.QuoteService.accept_quote(
                quote=quote,
                payment_option=serializer.validated_data["payment_option"],
                user=request.user,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Quote accepted")


class RejectQuoteView(APIView):
    """El cliente rechaza una cotización."""

    permission_classes = [IsAuthenticated]

    def put(self, request, quote_id):
        serializer = RejectQuoteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        quote = selectors.get_quote_by_id(str(quote_id))
        if not quote:
            return error_response("Quote not found", status_code=status.HTTP_404_NOT_FOUND)
        if quote.order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        try:
            services.QuoteService.reject_quote(
                quote=quote,
                user=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Quote rejected")


class QuotePDFView(APIView):
    """Descarga el PDF de una cotización. Propietario del pedido o admin."""

    permission_classes = [IsAuthenticated]

    def get(self, request, quote_id):
        quote = selectors.get_quote_by_id(str(quote_id))
        if not quote:
            return error_response("Quote not found", status_code=status.HTTP_404_NOT_FOUND)
        if quote.order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        pdf_bytes = QuotePDFService.generate(quote)
        short_id = str(quote.id)[:8]
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="cotizacion-{short_id}.pdf"'
        return response


class QuoteSnapshotView(APIView):
    """Snapshot de configuración usado al generar la cotización. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, quote_id):
        quote = selectors.get_quote_by_id(str(quote_id))
        if not quote:
            return error_response("Quote not found", status_code=status.HTTP_404_NOT_FOUND)
        try:
            snapshot = quote.snapshot
        except Exception:
            return error_response("Snapshot not found", status_code=status.HTTP_404_NOT_FOUND)
        serializer = QuoteSnapshotSerializer(snapshot)
        return success_response(data=serializer.data, message="Snapshot retrieved")


# --- Vistas administrativas ---

class AdminCreateQuoteView(APIView):
    """Crea una cotización para un pedido con datos de Bambu Studio. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, order_id):
        serializer = CreateQuoteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        try:
            quote = services.QuoteService.create_quote(
                order=order,
                weight_grams=serializer.validated_data["weight_grams"],
                print_time_hours=serializer.validated_data["print_time_hours"],
                shipping_cost=serializer.validated_data.get("shipping_cost", 0),
                created_by=request.user,
                printer_id=str(serializer.validated_data["printer_id"]) if serializer.validated_data.get("printer_id") else None,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return created_response(
            data={"quote_id": str(quote.id), "total_price": str(quote.total_price)},
            message="Quote created",
        )


class AdminExpireQuoteView(APIView):
    """Marca una cotización como expirada. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, quote_id):
        quote = selectors.get_quote_by_id(str(quote_id))
        if not quote:
            return error_response("Quote not found", status_code=status.HTTP_404_NOT_FOUND)

        try:
            services.QuoteService.expire_quote(quote=quote, admin=request.user)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Quote expired")


class CalculatorView(APIView):
    """Calcula el precio de una cotización sin guardarla. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = CalculateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        printer_id = serializer.validated_data.get("printer_id")
        printer = None
        if printer_id:
            from apps.configuration.models import Printer
            try:
                printer = Printer.objects.get(id=printer_id, is_active=True)
            except Printer.DoesNotExist:
                return error_response("Impresora no encontrada o inactiva.", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            result = services.QuoteCalculatorService.calculate(
                weight_grams=serializer.validated_data["weight_grams"],
                print_time_hours=serializer.validated_data["print_time_hours"],
                priority=serializer.validated_data["priority"],
                shipping_cost=serializer.validated_data.get("shipping_cost", 0),
                full_payment_selected=serializer.validated_data.get("full_payment_selected", False),
                printer=printer,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        result.pop("config", None)
        result.pop("printer", None)
        return success_response(data=result, message="Calculation completed")
