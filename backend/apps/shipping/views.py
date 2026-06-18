"""
Vistas para la app shipping.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.orders.selectors import get_order_by_id
from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import (
    CreateShipmentSerializer,
    ShipmentSerializer,
    ShippingAddressCreateSerializer,
    ShippingAddressSerializer,
)

# --- Vistas de direcciones de envío (clientes) ---


class ShippingAddressListCreateView(APIView):
    """Lista las direcciones del cliente o crea una nueva."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = selectors.get_addresses_for_user(request.user.id)
        serializer = ShippingAddressSerializer(addresses, many=True)
        return success_response(
            data={"count": addresses.count(), "results": serializer.data},
            message="Addresses retrieved",
        )

    def post(self, request):
        serializer = ShippingAddressCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        address = services.ShippingAddressService.create_address(
            user=request.user,
            data=serializer.validated_data,
        )
        return created_response(
            data={"id": str(address.id)},
            message="Address created",
        )


class ShippingAddressDetailView(APIView):
    """Detalle, actualización o eliminación de una dirección."""

    permission_classes = [IsAuthenticated]

    def _get_address_or_404(self, address_id, user):
        address = selectors.get_address_by_id(str(address_id))
        if not address:
            return None, error_response("Address not found", status_code=status.HTTP_404_NOT_FOUND)
        if address.user_id != user.id and not user.is_admin:
            return None, error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)
        return address, None

    def get(self, request, address_id):
        address, err = self._get_address_or_404(address_id, request.user)
        if err:
            return err
        serializer = ShippingAddressSerializer(address)
        return success_response(data=serializer.data, message="Address retrieved")

    def put(self, request, address_id):
        address, err = self._get_address_or_404(address_id, request.user)
        if err:
            return err

        serializer = ShippingAddressCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        try:
            address = services.ShippingAddressService.update_address(
                address=address,
                user=request.user,
                data=serializer.validated_data,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        serializer = ShippingAddressSerializer(address)
        return success_response(data=serializer.data, message="Address updated")

    def delete(self, request, address_id):
        address, err = self._get_address_or_404(address_id, request.user)
        if err:
            return err

        try:
            services.ShippingAddressService.delete_address(address=address, user=request.user)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Address deleted")


class ShipmentDetailView(APIView):
    """Detalle de un envío. Accesible para el propietario del pedido o admin."""

    permission_classes = [IsAuthenticated]

    def get(self, request, shipment_id):
        shipment = selectors.get_shipment_by_id(str(shipment_id))
        if not shipment:
            return error_response("Shipment not found", status_code=status.HTTP_404_NOT_FOUND)
        if shipment.order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)
        serializer = ShipmentSerializer(shipment)
        return success_response(data=serializer.data, message="Shipment retrieved")


# --- Vistas administrativas ---


class AdminCreateShipmentView(APIView):
    """Crea un envío para un pedido. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, order_id):
        serializer = CreateShipmentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        try:
            shipment = services.ShipmentService.create_shipment(
                order=order,
                carrier_name=serializer.validated_data.get("carrier_name", ""),
                tracking_number=serializer.validated_data.get("tracking_number", ""),
                shipping_cost=serializer.validated_data.get("shipping_cost", 0),
                shipping_notes=serializer.validated_data.get("shipping_notes", ""),
                created_by=request.user,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return created_response(
            data={"shipment_id": str(shipment.id)},
            message="Shipment created",
        )


class AdminMarkShipmentDeliveredView(APIView):
    """Marca un envío como entregado. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, shipment_id):
        shipment = selectors.get_shipment_by_id(str(shipment_id))
        if not shipment:
            return error_response("Shipment not found", status_code=status.HTTP_404_NOT_FOUND)

        try:
            services.ShipmentService.mark_delivered(shipment=shipment, admin=request.user)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(data={}, message="Shipment marked as delivered")
