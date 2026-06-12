"""
Servicios para la app shipping.
"""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.orders.models import EventType, Order, OrderEvent

from .models import Shipment, ShippingAddress


class ShippingAddressService:

    @staticmethod
    def create_address(user, data: dict) -> ShippingAddress:
        """Crea una dirección de envío para el usuario."""
        # Si la nueva dirección es default, limpia la anterior
        if data.get("is_default"):
            ShippingAddress.objects.filter(user=user, is_default=True).update(is_default=False)

        return ShippingAddress.objects.create(
            user=user,
            address_name=data["address_name"],
            street=data["street"],
            external_number=data["external_number"],
            internal_number=data.get("internal_number", ""),
            neighborhood=data["neighborhood"],
            postal_code=data["postal_code"],
            city=data["city"],
            state=data["state"],
            country=data.get("country", "Mexico"),
            references=data.get("references", ""),
            is_default=data.get("is_default", False),
        )

    @staticmethod
    def update_address(address: ShippingAddress, user, data: dict) -> ShippingAddress:
        """Actualiza una dirección existente. Solo el propietario puede hacerlo."""
        if address.user_id != user.id:
            raise ValueError("No tienes permiso para modificar esta dirección.")

        # Si la dirección actualizada es default, limpia la anterior
        if data.get("is_default"):
            ShippingAddress.objects.filter(user=user, is_default=True).exclude(id=address.id).update(is_default=False)

        for field in [
            "address_name", "street", "external_number", "internal_number",
            "neighborhood", "postal_code", "city", "state", "country",
            "references", "is_default",
        ]:
            if field in data:
                setattr(address, field, data[field])

        address.save()
        return address

    @staticmethod
    def delete_address(address: ShippingAddress, user) -> None:
        """Elimina una dirección. Solo el propietario puede hacerlo."""
        if address.user_id != user.id:
            raise ValueError("No tienes permiso para eliminar esta dirección.")
        address.delete()


class ShipmentService:

    @staticmethod
    @transaction.atomic
    def create_shipment(
        order: Order,
        carrier_name: str,
        tracking_number: str,
        shipping_cost: Decimal,
        shipping_notes: str,
        created_by,
    ) -> Shipment:
        """
        Crea un envío para el pedido.
        Solo aplica cuando delivery_method = SHIPPING.
        """
        if hasattr(order, "shipment"):
            raise ValueError("El pedido ya tiene un envío registrado.")

        shipment = Shipment.objects.create(
            order=order,
            carrier_name=carrier_name,
            tracking_number=tracking_number,
            shipping_cost=shipping_cost,
            shipping_notes=shipping_notes,
            shipped_at=timezone.now(),
        )

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.SHIPMENT_CREATED,
            event_description=f"Envío creado. Transportista: {carrier_name or 'N/A'}.",
            metadata={
                "shipment_id": str(shipment.id),
                "carrier_name": carrier_name,
                "tracking_number": tracking_number,
            },
            created_by=created_by,
        )

        return shipment

    @staticmethod
    @transaction.atomic
    def mark_delivered(shipment: Shipment, admin) -> Shipment:
        """
        Marca un envío como entregado y transiciona el pedido a DELIVERED.
        El pedido debe estar completamente pagado.
        """
        if shipment.delivered_at:
            raise ValueError("El envío ya fue marcado como entregado.")

        shipment.delivered_at = timezone.now()
        shipment.save(update_fields=["delivered_at", "updated_at"])

        order = shipment.order

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.ORDER_DELIVERED,
            event_description="Envío marcado como entregado.",
            metadata={"shipment_id": str(shipment.id)},
            created_by=admin,
        )

        # Transición del pedido a DELIVERED usando el servicio oficial
        from apps.production.services import OrderStatusTransitionService
        try:
            OrderStatusTransitionService.transition(
                order=order,
                new_status="DELIVERED",
                changed_by=admin,
                notes="Envío entregado al cliente.",
            )
        except ValueError as e:
            raise ValueError(f"No se pudo marcar como entregado: {e}")

        return shipment
