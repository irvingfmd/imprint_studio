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
    HolidaySerializer,
    PaymentInstructionsSerializer,
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
