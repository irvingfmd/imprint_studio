"""
Vistas para la app configuration.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import (
    BusinessConfigSerializer,
    BusinessHoursSerializer,
    CreateHolidaySerializer,
    CreateUpdatePrinterSerializer,
    HolidaySerializer,
    PaymentInstructionsSerializer,
    PrinterSerializer,
    UpdateBusinessHoursSerializer,
)

# --- Vista pública ---


class PublicPaymentInstructionsView(APIView):
    """Instrucciones de pago para clientes autenticados."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        instructions = selectors.get_active_payment_instructions()
        if not instructions:
            return error_response("Payment instructions not found", status_code=status.HTTP_404_NOT_FOUND)
        serializer = PaymentInstructionsSerializer(instructions)
        return success_response(data=serializer.data, message="Payment instructions retrieved")


# --- Vistas administrativas ---


class AdminBusinessConfigView(APIView):
    """Configuración del negocio. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        config = selectors.get_active_business_config()
        if not config:
            return error_response("Business config not found", status_code=status.HTTP_404_NOT_FOUND)
        serializer = BusinessConfigSerializer(config)
        return success_response(data=serializer.data, message="Business config retrieved")

    def put(self, request):
        config = selectors.get_active_business_config()
        if not config:
            return error_response("Business config not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = BusinessConfigSerializer(config, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        try:
            updated = services.ConfigurationService.update_business_config(serializer.validated_data)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(
            data=BusinessConfigSerializer(updated).data,
            message="Business config updated",
        )


class AdminBusinessHoursListView(APIView):
    """Lista todos los horarios de atención. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        hours = selectors.get_all_business_hours()
        serializer = BusinessHoursSerializer(hours, many=True)
        return success_response(
            data={"count": hours.count(), "results": serializer.data},
            message="Business hours retrieved",
        )

    def put(self, request):
        serializer = UpdateBusinessHoursSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        weekday = serializer.validated_data.pop("weekday")
        try:
            updated = services.ConfigurationService.update_business_hours(weekday, serializer.validated_data)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(
            data=BusinessHoursSerializer(updated).data,
            message="Business hours updated",
        )


class AdminHolidayListCreateView(APIView):
    """Lista y crea días festivos. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        holidays = selectors.get_all_holidays()
        serializer = HolidaySerializer(holidays, many=True)
        return success_response(
            data={"count": holidays.count(), "results": serializer.data},
            message="Holidays retrieved",
        )

    def post(self, request):
        serializer = CreateHolidaySerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        try:
            holiday = services.ConfigurationService.create_holiday(serializer.validated_data)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_409_CONFLICT)

        return created_response(
            data=HolidaySerializer(holiday).data,
            message="Holiday created",
        )


class AdminHolidayDeleteView(APIView):
    """Elimina un día festivo. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, holiday_id):
        try:
            services.ConfigurationService.delete_holiday(str(holiday_id))
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)

        return success_response(data={}, message="Holiday deleted")


class AdminPrinterListCreateView(APIView):
    """Lista todas las impresoras y crea nuevas. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        printers = selectors.get_all_printers()
        serializer = PrinterSerializer(printers, many=True)
        return success_response(
            data={"count": printers.count(), "results": serializer.data},
            message="Printers retrieved",
        )

    def post(self, request):
        serializer = CreateUpdatePrinterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        printer = services.ConfigurationService.create_printer(serializer.validated_data)
        return created_response(data=PrinterSerializer(printer).data, message="Printer created")


class AdminPrinterDetailView(APIView):
    """Obtiene, actualiza o elimina una impresora. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, printer_id):
        printer = selectors.get_printer_by_id(str(printer_id))
        if not printer:
            return error_response("Printer not found", status_code=status.HTTP_404_NOT_FOUND)
        return success_response(data=PrinterSerializer(printer).data, message="Printer retrieved")

    def put(self, request, printer_id):
        printer = selectors.get_printer_by_id(str(printer_id))
        if not printer:
            return error_response("Printer not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = CreateUpdatePrinterSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        try:
            updated = services.ConfigurationService.update_printer(str(printer_id), serializer.validated_data)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data=PrinterSerializer(updated).data, message="Printer updated")

    def delete(self, request, printer_id):
        try:
            services.ConfigurationService.delete_printer(str(printer_id))
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
        return success_response(data={}, message="Printer deleted")


class AdminPaymentInstructionsView(APIView):
    """Instrucciones de pago. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        instructions = selectors.get_active_payment_instructions()
        if not instructions:
            return error_response("Payment instructions not found", status_code=status.HTTP_404_NOT_FOUND)
        serializer = PaymentInstructionsSerializer(instructions)
        return success_response(data=serializer.data, message="Payment instructions retrieved")

    def put(self, request):
        instructions = selectors.get_active_payment_instructions()
        if not instructions:
            return error_response("Payment instructions not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = PaymentInstructionsSerializer(instructions, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        try:
            updated = services.ConfigurationService.update_payment_instructions(serializer.validated_data)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(
            data=PaymentInstructionsSerializer(updated).data,
            message="Payment instructions updated",
        )


class ElectricityRateLookupView(APIView):
    """Consulta la zona CFE y tarifa de referencia para un código postal mexicano."""

    permission_classes = [IsAdmin]

    def get(self, request):
        from .utils.cfe_rates import lookup_cfe

        postal_code = request.query_params.get("postal_code", "").strip()
        if not postal_code or not postal_code.isdigit() or len(postal_code) != 5:
            return error_response("Ingresa un código postal de 5 dígitos.")

        result = lookup_cfe(postal_code)
        if result is None:
            return error_response(
                f"No se encontró información CFE para el CP {postal_code}. Verifica tu tarifa en tu recibo o en cfe.mx"
            )

        return success_response(data=result, message="Tarifa CFE consultada")
