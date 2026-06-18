"""
Vistas para la app production.

Las rutas viven bajo /api/v1/orders/{order_id}/... y se registran en orders/urls.py
y orders/admin_urls.py porque siguen la jerarquía REST del recurso Order.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.orders.selectors import get_order_by_id
from core.permissions import IsAdmin
from core.responses import error_response, success_response

from . import selectors, services
from .serializers import (
    CancelOrderSerializer,
    OrderEventSerializer,
    ProductionHistorySerializer,
    UpdateOrderStatusSerializer,
)

# --- Vistas para clientes y admins (lectura) ---


class ProductionHistoryListView(APIView):
    """Lista el historial de cambios de estado de un pedido."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)
        history = selectors.get_production_history_for_order(str(order_id))
        serializer = ProductionHistorySerializer(history, many=True)
        return success_response(
            data={"count": history.count(), "results": serializer.data},
            message="Production history retrieved",
        )


class OrderEventListView(APIView):
    """Lista todos los eventos de auditoría de un pedido."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)
        events = selectors.get_events_for_order(str(order_id))
        serializer = OrderEventSerializer(events, many=True)
        return success_response(
            data={"count": events.count(), "results": serializer.data},
            message="Order events retrieved",
        )


class OrderEventDetailView(APIView):
    """Detalle de un evento específico de un pedido."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id, event_id):
        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)
        event = selectors.get_event_by_id(str(event_id), str(order_id))
        if not event:
            return error_response("Event not found", status_code=status.HTTP_404_NOT_FOUND)
        serializer = OrderEventSerializer(event)
        return success_response(data=serializer.data, message="Event retrieved")


# --- Vistas administrativas ---


class AdminUpdateOrderStatusView(APIView):
    """
    Actualiza el estado de un pedido.
    Usa OrderStatusTransitionService para validar la transición.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, order_id):
        serializer = UpdateOrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        try:
            services.OrderStatusTransitionService.transition(
                order=order,
                new_status=serializer.validated_data["status"],
                changed_by=request.user,
                notes=serializer.validated_data.get("notes", ""),
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Order status updated")


class AdminCancelOrderView(APIView):
    """
    Cancela un pedido.
    Solo permitido desde: RECEIVED, PENDING_ANALYSIS, QUOTED, APPROVED, PENDING_DEPOSIT.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, order_id):
        serializer = CancelOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        try:
            services.OrderStatusTransitionService.cancel_order(
                order=order,
                cancelled_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Order cancelled")
