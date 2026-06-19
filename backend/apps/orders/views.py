"""
Vistas para la app orders.
"""

import os
import uuid

from django.conf import settings as django_settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import (
    AdminOrderCreateSerializer,
    AdminOrderDetailSerializer,
    AdminOrderListSerializer,
    AssignShippingAddressSerializer,
    CancelOrderSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    RequestFileSerializer,
    RequestFileUploadSerializer,
)

# --- Vistas para clientes ---


class OrderListCreateView(APIView):
    """Lista los pedidos del cliente autenticado o crea uno nuevo."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = selectors.get_orders_for_customer(request.user.id)
        serializer = OrderListSerializer(orders, many=True)
        return success_response(
            data={"count": orders.count(), "results": serializer.data},
            message="Orders retrieved",
        )

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        order = services.OrderService.create_order(
            customer=request.user,
            data=serializer.validated_data,
        )
        return created_response(
            data={"id": str(order.id), "status": order.status},
            message="Order created",
        )


class OrderDetailView(APIView):
    """Detalle de un pedido. Accesible para el propietario o admin."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = selectors.get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        serializer = OrderDetailSerializer(order)
        return success_response(data=serializer.data, message="Order retrieved")


class CancelOrderView(APIView):
    """El cliente solicita la cancelación de su propio pedido."""

    permission_classes = [IsAuthenticated]

    def put(self, request, order_id):
        serializer = CancelOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        order = selectors.get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        from apps.production.services import OrderStatusTransitionService

        try:
            OrderStatusTransitionService.cancel_order(
                order=order,
                cancelled_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Order cancelled")


class AssignShippingAddressView(APIView):
    """Asigna una dirección de envío al pedido del cliente."""

    permission_classes = [IsAuthenticated]

    def put(self, request, order_id):
        serializer = AssignShippingAddressSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        order = selectors.get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        try:
            services.OrderService.assign_shipping_address(
                order=order,
                address_id=str(serializer.validated_data["shipping_address_id"]),
                user=request.user,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Shipping address assigned")


class OrderFileListUploadView(APIView):
    """Lista archivos de un pedido o sube un nuevo archivo."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = selectors.get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        files = selectors.get_files_for_order(str(order_id))
        serializer = RequestFileSerializer(files, many=True)
        return success_response(
            data={"results": serializer.data},
            message="Files retrieved",
        )

    def post(self, request, order_id):
        order = selectors.get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        uploaded_file = request.FILES.get("file")

        if uploaded_file:
            max_file_size = 20 * 1024 * 1024  # 20 MB
            if uploaded_file.size > max_file_size:
                return error_response(
                    "El archivo no puede superar los 20 MB.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            ext = os.path.splitext(uploaded_file.name)[1].lower()
            allowed_extensions = {".stl", ".obj", ".3mf", ".jpg", ".jpeg", ".png", ".webp"}
            if ext not in allowed_extensions:
                return error_response(
                    "Formato no permitido. Usa STL, OBJ, 3MF, JPG, PNG o WEBP.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            file_type = request.data.get("file_type", "REFERENCE")
            safe_name = f"{uuid.uuid4().hex}{ext}"
            dest_dir = os.path.join(django_settings.MEDIA_ROOT, "orders", str(order_id))
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, safe_name)
            with open(dest_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            file_url = f"{django_settings.MEDIA_URL}orders/{order_id}/{safe_name}"

            req_file = services.OrderService.upload_file(
                order=order,
                file_url=file_url,
                file_type=file_type,
                original_filename=uploaded_file.name,
                mime_type=uploaded_file.content_type or "application/octet-stream",
                file_size_bytes=uploaded_file.size,
                user=request.user,
            )

            auto_quote = _try_auto_quote(order, dest_path, request.user)
            response_data: dict = {"id": str(req_file.id), "file_type": req_file.file_type}
            if auto_quote:
                response_data["auto_quote"] = {
                    "quote_id": str(auto_quote.id),
                    "total_price": str(auto_quote.total_price),
                }
            return created_response(data=response_data, message="File uploaded")

        serializer = RequestFileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        req_file = services.OrderService.upload_file(
            order=order,
            file_url=serializer.validated_data["file_url"],
            file_type=serializer.validated_data["file_type"],
            original_filename=serializer.validated_data["original_filename"],
            mime_type=serializer.validated_data["mime_type"],
            file_size_bytes=serializer.validated_data["file_size_bytes"],
            user=request.user,
        )
        return created_response(
            data={"id": str(req_file.id), "file_type": req_file.file_type},
            message="File uploaded",
        )


# --- Vistas administrativas ---


class AdminOrderListView(APIView):
    """Lista todos los pedidos con filtros. Solo administradores."""

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

        orders = selectors.get_all_orders(
            status=request.query_params.get("status"),
            priority=request.query_params.get("priority"),
            customer_id=request.query_params.get("customer_id"),
            request_type=request.query_params.get("request_type"),
            delivery_method=request.query_params.get("delivery_method"),
            created_from=request.query_params.get("created_from"),
            created_to=request.query_params.get("created_to"),
        )
        paginator = Paginator(orders, page_size)
        page = paginator.get_page(request.query_params.get("page", 1))
        serializer = AdminOrderListSerializer(page.object_list, many=True)
        return success_response(
            data={
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "results": serializer.data,
            },
            message="Orders retrieved",
        )


class AdminOrderCreateView(APIView):
    """Crea un pedido a nombre de un cliente. Solo administradores."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = AdminOrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        from apps.authentication.models import User

        try:
            customer = User.objects.get(id=serializer.validated_data["customer_id"])
        except User.DoesNotExist:
            return error_response("Cliente no encontrado.", status_code=status.HTTP_404_NOT_FOUND)

        order = services.OrderService.create_order(
            customer=customer,
            data=serializer.validated_data,
        )
        return created_response(
            data={"id": str(order.id), "status": order.status},
            message="Order created by admin",
        )


class AdminOrderDetailView(APIView):
    """Detalle completo de cualquier pedido. Solo administradores."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, order_id):
        order = selectors.get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = AdminOrderDetailSerializer(order)
        return success_response(data=serializer.data, message="Order retrieved")


class AdminDashboardView(APIView):
    """Métricas del dashboard administrativo."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        from decimal import Decimal

        from django.db.models import Count, Sum
        from django.db.models.functions import TruncMonth
        from django.utils import timezone

        from apps.orders.models import Order, OrderStatus
        from apps.payments.models import Payment, PaymentStatus

        now = timezone.now()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Retroceder N meses sin dependencias externas
        def _months_back(dt, n: int):
            month = dt.month - n
            year = dt.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            return dt.replace(year=year, month=month, day=1)

        first_of_prev_month = _months_back(first_of_month, 1)
        six_months_ago = _months_back(first_of_month, 5)

        # --- Conteos existentes (backwards compatible) ---
        pending_orders = Order.objects.filter(status=OrderStatus.RECEIVED, is_deleted=False).count()
        quoted_orders = Order.objects.filter(status=OrderStatus.QUOTED, is_deleted=False).count()
        printing_orders = Order.objects.filter(status=OrderStatus.PRINTING, is_deleted=False).count()
        ready_orders = Order.objects.filter(status=OrderStatus.READY, is_deleted=False).count()
        pending_payments = Payment.objects.filter(payment_status=PaymentStatus.PENDING, is_deleted=False).count()

        monthly_revenue = Payment.objects.filter(
            payment_status=PaymentStatus.CONFIRMED, created_at__gte=first_of_month
        ).exclude(payment_type="REFUND").aggregate(total=Sum("amount"))["total"] or Decimal("0")

        # --- Ingresos por mes (últimos 6 meses) ---
        revenue_by_month_qs = (
            Payment.objects.filter(
                payment_status=PaymentStatus.CONFIRMED,
                created_at__gte=six_months_ago,
            )
            .exclude(payment_type="REFUND")
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(revenue=Sum("amount"))
            .order_by("month")
        )
        revenue_by_month = [
            {"month": r["month"].strftime("%Y-%m"), "revenue": str(r["revenue"])} for r in revenue_by_month_qs
        ]

        # --- Pedidos del mes actual vs anterior ---
        orders_this_month = Order.objects.filter(created_at__gte=first_of_month, is_deleted=False).count()
        orders_prev_month = Order.objects.filter(
            created_at__gte=first_of_prev_month,
            created_at__lt=first_of_month,
            is_deleted=False,
        ).count()

        # --- Tiempo promedio de entrega (días, pedidos entregados este mes) ---
        delivered_this_month = Order.objects.filter(
            status=OrderStatus.DELIVERED,
            delivered_at__gte=first_of_month,
            is_deleted=False,
        )
        delivery_times: list[float] = []
        for order in delivered_this_month:
            delivery_times.append((order.delivered_at - order.created_at).total_seconds() / 86400)
        avg_delivery_days = round(sum(delivery_times) / len(delivery_times), 1) if delivery_times else None

        # --- Tasa de cancelación del mes ---
        cancelled_this_month = Order.objects.filter(
            status=OrderStatus.CANCELLED,
            cancelled_at__gte=first_of_month,
            is_deleted=False,
        ).count()
        cancellation_rate = round(cancelled_this_month / orders_this_month * 100, 1) if orders_this_month > 0 else 0

        # --- Top tipos de solicitud del mes ---
        request_type_counts = list(
            Order.objects.filter(created_at__gte=first_of_month, is_deleted=False)
            .values("request_type")
            .annotate(count=Count("id"))
            .order_by("-count")[:3]
        )

        # --- Pedidos por prioridad del mes ---
        priority_counts = list(
            Order.objects.filter(created_at__gte=first_of_month, is_deleted=False)
            .values("priority")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return success_response(
            data={
                "pending_orders": pending_orders,
                "quoted_orders": quoted_orders,
                "printing_orders": printing_orders,
                "ready_orders": ready_orders,
                "pending_payments": pending_payments,
                "monthly_revenue": str(monthly_revenue),
                "revenue_by_month": revenue_by_month,
                "orders_this_month": orders_this_month,
                "orders_prev_month": orders_prev_month,
                "avg_delivery_days": avg_delivery_days,
                "cancellation_rate": cancellation_rate,
                "request_type_counts": request_type_counts,
                "priority_counts": priority_counts,
            },
            message="Dashboard metrics retrieved",
        )


def _try_auto_quote(order, file_path: str, user):  # noqa: F821
    """
    Si el archivo es STL y el pedido no tiene cotización activa, genera una auto-cotización.
    Errores de análisis se tragan — el admin puede cotizar manualmente.
    """
    if not file_path.lower().endswith(".stl"):
        return None

    from apps.quotes.models import Quote, QuoteStatus

    if Quote.objects.filter(order=order, quote_status=QuoteStatus.PENDING, is_deleted=False).exists():
        return None

    import logging

    logger = logging.getLogger(__name__)

    try:
        with open(file_path, "rb") as f:
            data = f.read()

        from decimal import Decimal

        from apps.quotes.services import QuoteService
        from apps.quotes.stl_service import estimate_from_stl

        estimate = estimate_from_stl(data)
        quote = QuoteService.create_quote(
            order=order,
            weight_grams=estimate["estimated_weight_grams"],
            print_time_hours=estimate["estimated_print_time_hours"],
            shipping_cost=Decimal("0.00"),
            created_by=user,
        )
        logger.info(
            "Auto-cotización %s generada para pedido %s (vol=%.1f cm³, peso=%.1fg, tiempo=%.1fh)",
            quote.id,
            order.id,
            estimate["volume_cm3"],
            estimate["estimated_weight_grams"],
            estimate["estimated_print_time_hours"],
        )
        return quote
    except Exception as exc:
        logger.warning("No se pudo generar auto-cotización para pedido %s: %s", order.id, exc)
        return None
