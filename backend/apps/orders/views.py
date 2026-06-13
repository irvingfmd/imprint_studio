"""
Vistas para la app orders.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import (
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
        serializer = RequestFileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        order = selectors.get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        file = services.OrderService.upload_file(
            order=order,
            file_url=serializer.validated_data["file_url"],
            file_type=serializer.validated_data["file_type"],
            original_filename=serializer.validated_data["original_filename"],
            mime_type=serializer.validated_data["mime_type"],
            file_size_bytes=serializer.validated_data["file_size_bytes"],
            user=request.user,
        )
        return created_response(
            data={"id": str(file.id), "file_type": file.file_type},
            message="File uploaded",
        )


# --- Vistas administrativas ---

class AdminOrderListView(APIView):
    """Lista todos los pedidos con filtros. Solo administradores."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        orders = selectors.get_all_orders(
            status=request.query_params.get("status"),
            priority=request.query_params.get("priority"),
            customer_id=request.query_params.get("customer_id"),
            request_type=request.query_params.get("request_type"),
            delivery_method=request.query_params.get("delivery_method"),
            created_from=request.query_params.get("created_from"),
            created_to=request.query_params.get("created_to"),
        )
        serializer = AdminOrderListSerializer(orders, many=True)
        return success_response(
            data={"count": orders.count(), "results": serializer.data},
            message="Orders retrieved",
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
        from django.db.models import Sum
        from apps.orders.models import Order, OrderStatus
        from apps.payments.models import Payment, PaymentStatus
        from django.utils import timezone

        now = timezone.now()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        pending_orders = Order.objects.filter(
            status=OrderStatus.RECEIVED, is_deleted=False
        ).count()
        quoted_orders = Order.objects.filter(
            status=OrderStatus.QUOTED, is_deleted=False
        ).count()
        printing_orders = Order.objects.filter(
            status=OrderStatus.PRINTING, is_deleted=False
        ).count()
        ready_orders = Order.objects.filter(
            status=OrderStatus.READY, is_deleted=False
        ).count()
        pending_payments = Payment.objects.filter(
            payment_status=PaymentStatus.PENDING, is_deleted=False
        ).count()

        monthly_revenue = (
            Payment.objects
            .filter(payment_status=PaymentStatus.CONFIRMED, created_at__gte=first_of_month)
            .exclude(payment_type="REFUND")
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        return success_response(
            data={
                "pending_orders": pending_orders,
                "quoted_orders": quoted_orders,
                "printing_orders": printing_orders,
                "ready_orders": ready_orders,
                "pending_payments": pending_payments,
                "monthly_revenue": str(monthly_revenue),
            },
            message="Dashboard metrics retrieved",
        )
