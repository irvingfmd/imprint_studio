"""
Vistas para la app payments.
"""

import os

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.orders.selectors import get_order_by_id
from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import (
    ConfirmPaymentSerializer,
    ManualConfirmationSerializer,
    PaymentSerializer,
    RefundSerializer,
    RejectPaymentSerializer,
)

# --- Vistas para clientes ---


class OrderPaymentListView(APIView):
    """Lista los pagos de un pedido. Accesible para el propietario o admin."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)
        payments = selectors.get_payments_for_order(order_id)
        serializer = PaymentSerializer(payments, many=True)
        return success_response(
            data={"count": payments.count(), "results": serializer.data},
            message="Payments retrieved",
        )


class PaymentDetailView(APIView):
    """Detalle de un pago específico."""

    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        payment = selectors.get_payment_by_id(payment_id)
        if not payment:
            return error_response("Payment not found", status_code=status.HTTP_404_NOT_FOUND)
        if payment.order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)
        serializer = PaymentSerializer(payment)
        return success_response(data=serializer.data, message="Payment retrieved")


class PaymentProofView(APIView):
    """
    Asocia un comprobante de pago.
    Acepta multipart/form-data con campo 'file' (imagen o PDF)
    o JSON con campo 'file_url' (URL de storage externo como Cloudinary).
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, payment_id):
        from django.conf import settings as django_settings
        from django.core.files.storage import default_storage

        payment = selectors.get_payment_by_id(str(payment_id))
        if not payment:
            return error_response("Payment not found", status_code=status.HTTP_404_NOT_FOUND)
        if payment.order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return error_response(
                "Se requiere un archivo de comprobante.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        ext = os.path.splitext(uploaded_file.name)[1].lower()
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
        if ext not in allowed_extensions:
            return error_response(
                "Formato no permitido. Usa JPG, PNG, WEBP o PDF.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        max_size = 10 * 1024 * 1024  # 10 MB
        if uploaded_file.size > max_size:
            return error_response(
                "El archivo no puede superar los 10 MB.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        save_path = default_storage.save(
            f"proofs/{payment_id}{ext}",
            uploaded_file,
        )
        file_url = request.build_absolute_uri(django_settings.MEDIA_URL + save_path)

        try:
            services.PaymentService.upload_proof(
                payment_id=str(payment_id),
                file_url=file_url,
                user=request.user,
            )
        except ValueError as e:
            default_storage.delete(save_path)
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={"file_url": file_url}, message="Payment proof uploaded")


# --- Vistas administrativas ---


class AdminPaymentListView(APIView):
    """Lista todos los pagos con filtros opcionales. Solo administradores."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        from django.core.paginator import Paginator

        try:
            page_size = max(1, min(int(request.query_params.get("page_size", 20)), 100))
        except (ValueError, TypeError):
            return error_response(
                "page_size debe ser un entero positivo.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        payments = selectors.get_all_payments(
            payment_type=request.query_params.get("payment_type"),
            payment_method=request.query_params.get("payment_method"),
            payment_status=request.query_params.get("payment_status"),
            order_id=request.query_params.get("order_id"),
            created_from=request.query_params.get("created_from"),
            created_to=request.query_params.get("created_to"),
        )
        paginator = Paginator(payments, page_size)
        page = paginator.get_page(request.query_params.get("page", 1))
        serializer = PaymentSerializer(page.object_list, many=True)
        return success_response(
            data={
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "results": serializer.data,
            },
            message="Payments retrieved",
        )


class AdminConfirmPaymentView(APIView):
    """Confirma un pago pendiente. Solo administradores."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, payment_id):
        serializer = ConfirmPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            services.PaymentService.confirm_payment(
                payment_id=str(payment_id),
                confirmed_by=request.user,
                notes=serializer.validated_data.get("notes", ""),
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Payment confirmed")


class AdminRejectPaymentView(APIView):
    """Rechaza un pago pendiente. Solo administradores."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, payment_id):
        serializer = RejectPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            services.PaymentService.reject_payment(
                payment_id=str(payment_id),
                confirmed_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Payment rejected")


class AdminManualConfirmationView(APIView):
    """Registra un pago confirmado manualmente para un pedido. Solo administradores."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, order_id):
        serializer = ManualConfirmationSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            services.PaymentService.create_manual_confirmation(
                order_id=str(order_id),
                payment_type=serializer.validated_data["payment_type"],
                payment_method=serializer.validated_data["payment_method"],
                amount=serializer.validated_data["amount"],
                notes=serializer.validated_data.get("notes", ""),
                confirmed_by=request.user,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return created_response(data={}, message="Manual payment registered")


class AdminRefundView(APIView):
    """Registra un reembolso para un pedido. Solo administradores."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, order_id):
        serializer = RefundSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            services.PaymentService.process_refund(
                order_id=str(order_id),
                amount=serializer.validated_data["amount"],
                reason=serializer.validated_data["reason"],
                confirmed_by=request.user,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return created_response(data={}, message="Refund registered")
