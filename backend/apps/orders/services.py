"""
Servicios para la app orders.
Toda la lógica de negocio de pedidos vive aquí.
"""

from django.db import transaction

from .models import EventType, InternalNote, Order, OrderEvent, OrderStatus, RequestFile, RequestType


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(customer, data: dict) -> Order:
        """
        Crea un nuevo pedido.
        Estado inicial: RECEIVED para REFERENCE, PENDING_ANALYSIS para PRINTABLE_FILE y WEB_MODEL.
        """
        request_type = data["request_type"]
        initial_status = OrderStatus.RECEIVED if request_type == RequestType.REFERENCE else OrderStatus.PENDING_ANALYSIS

        order = Order.objects.create(
            customer=customer,
            request_type=request_type,
            title=data["title"],
            description=data["description"],
            color=data.get("color", ""),
            quantity=data["quantity"],
            dimensions_notes=data.get("dimensions_notes", ""),
            priority=data.get("priority", "NORMAL"),
            delivery_method=data.get("delivery_method", "PICKUP"),
            status=initial_status,
        )

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.ORDER_CREATED,
            event_description=f"Pedido «{order.title}» creado.",
            metadata={"request_type": request_type, "priority": order.priority},
            created_by=customer,
        )

        from apps.notifications.services import NotificationService

        NotificationService.notify_admin_new_order(order)

        return order

    @staticmethod
    @transaction.atomic
    def repeat_order(original_order: Order, customer) -> Order:
        """Clona un pedido existente como uno nuevo. No copia archivos, pagos ni estado."""
        return OrderService.create_order(
            customer=customer,
            data={
                "request_type": original_order.request_type,
                "title": original_order.title,
                "description": original_order.description,
                "color": original_order.color,
                "quantity": original_order.quantity,
                "dimensions_notes": original_order.dimensions_notes,
                "priority": original_order.priority,
                "delivery_method": original_order.delivery_method,
            },
        )

    @staticmethod
    @transaction.atomic
    def assign_shipping_address(order: Order, address_id: str, user) -> Order:
        """Asigna una dirección de envío al pedido. La dirección debe pertenecer al usuario."""
        from apps.shipping.models import ShippingAddress

        try:
            address = ShippingAddress.objects.get(id=address_id, user=user)
        except ShippingAddress.DoesNotExist:
            raise ValueError("Dirección no encontrada o no pertenece al usuario.")

        order.shipping_address = address
        order.save(update_fields=["shipping_address_id", "updated_at"])

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.SHIPPING_ADDRESS_UPDATED,
            event_description=f"Dirección de envío asignada: {address.address_name}.",
            metadata={"address_id": str(address.id)},
            created_by=user,
        )

        return order

    @staticmethod
    @transaction.atomic
    def upload_file(
        order: Order,
        file_url: str,
        file_type: str,
        original_filename: str,
        mime_type: str,
        file_size_bytes: int,
        user,
    ) -> RequestFile:
        """Adjunta un archivo a un pedido y registra el evento correspondiente."""
        request_file = RequestFile.objects.create(
            order=order,
            uploaded_by=user,
            file_type=file_type,
            file_url=file_url,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
        )

        OrderEvent.objects.create(
            order=order,
            event_type=EventType.FILE_UPLOADED,
            event_description=f"Archivo «{original_filename}» adjuntado.",
            metadata={
                "file_id": str(request_file.id),
                "file_type": file_type,
                "filename": original_filename,
            },
            created_by=user,
        )

        return request_file


class InternalNoteService:
    @staticmethod
    def create_note(order: Order, user, content: str) -> InternalNote:
        return InternalNote.objects.create(
            order=order,
            created_by=user,
            content=content,
        )
