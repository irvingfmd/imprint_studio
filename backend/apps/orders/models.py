"""
Modelos de la app orders.

Order: solicitud principal de impresión 3D.
RequestFile: archivos adjuntos a una solicitud.
"""

import uuid

from django.db import models

from apps.authentication.models import User


class OrderStatus(models.TextChoices):
    RECEIVED = "RECEIVED", "Received"
    PENDING_ANALYSIS = "PENDING_ANALYSIS", "Pending Analysis"
    QUOTED = "QUOTED", "Quoted"
    APPROVED = "APPROVED", "Approved"
    PENDING_DEPOSIT = "PENDING_DEPOSIT", "Pending Deposit"
    DEPOSIT_PAID = "DEPOSIT_PAID", "Deposit Paid"
    PRINTING = "PRINTING", "Printing"
    POST_PROCESSING = "POST_PROCESSING", "Post Processing"
    READY = "READY", "Ready"
    PENDING_BALANCE = "PENDING_BALANCE", "Pending Balance"
    FULLY_PAID = "FULLY_PAID", "Fully Paid"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"


class OrderPaymentStatus(models.TextChoices):
    NO_PAYMENT = "NO_PAYMENT", "No Payment"
    DEPOSIT_PENDING = "DEPOSIT_PENDING", "Deposit Pending"
    DEPOSIT_PAID = "DEPOSIT_PAID", "Deposit Paid"
    BALANCE_PENDING = "BALANCE_PENDING", "Balance Pending"
    FULLY_PAID = "FULLY_PAID", "Fully Paid"
    REFUNDED = "REFUNDED", "Refunded"


class OrderPriority(models.TextChoices):
    NORMAL = "NORMAL", "Normal"
    URGENT = "URGENT", "Urgent"
    EXPRESS = "EXPRESS", "Express"


class RequestType(models.TextChoices):
    REFERENCE = "REFERENCE", "Reference"
    PRINTABLE_FILE = "PRINTABLE_FILE", "Printable File"
    WEB_MODEL = "WEB_MODEL", "Web Model"


class DeliveryMethod(models.TextChoices):
    PICKUP = "PICKUP", "Pickup"
    SHIPPING = "SHIPPING", "Shipping"


class FileType(models.TextChoices):
    IMAGE = "IMAGE", "Image"
    STL = "STL", "STL"
    OBJ = "OBJ", "OBJ"
    THREE_MF = "THREE_MF", "3MF"
    WEB_MODEL = "WEB_MODEL", "Web Model"
    PAYMENT_PROOF = "PAYMENT_PROOF", "Payment Proof"


class Order(models.Model):
    """
    Solicitud de impresión 3D realizada por un cliente.
    Es la entidad principal del sistema.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="orders",
    )

    shipping_address = models.ForeignKey(
        "shipping.ShippingAddress",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    request_type = models.CharField(
        max_length=30,
        choices=RequestType.choices,
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    color = models.CharField(max_length=100, blank=True, default="")
    quantity = models.PositiveIntegerField()
    dimensions_notes = models.TextField(blank=True, default="")

    priority = models.CharField(
        max_length=20,
        choices=OrderPriority.choices,
        default=OrderPriority.NORMAL,
    )

    status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        default=OrderStatus.RECEIVED,
    )

    payment_status = models.CharField(
        max_length=50,
        choices=OrderPaymentStatus.choices,
        default=OrderPaymentStatus.NO_PAYMENT,
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.PICKUP,
    )

    estimated_delivery_date = models.DateField(null=True, blank=True)

    approved_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, default="")

    # Campos reservados para IA futura. Vacíos durante el MVP.
    ai_analysis = models.JSONField(null=True, blank=True)
    ai_notes = models.TextField(blank=True, default="")
    ai_confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    ai_category = models.CharField(max_length=100, blank=True, default="")

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["request_type"]),
            models.Index(fields=["delivery_method"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["priority", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.status}"


class RequestFile(models.Model):
    """
    Archivo adjunto a una solicitud de impresión.
    Puede ser imagen, STL, OBJ, 3MF o comprobante de pago.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.RESTRICT,
        related_name="files",
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="uploaded_files",
    )

    file_type = models.CharField(
        max_length=30,
        choices=FileType.choices,
    )

    file_url = models.TextField()
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    file_size_bytes = models.PositiveBigIntegerField()

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "request_files"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["file_type"]),
            models.Index(fields=["uploaded_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.file_type} — {self.original_filename}"


class EventType(models.TextChoices):
    ORDER_CREATED = "ORDER_CREATED", "Order Created"
    FILE_UPLOADED = "FILE_UPLOADED", "File Uploaded"
    QUOTE_CREATED = "QUOTE_CREATED", "Quote Created"
    QUOTE_ACCEPTED = "QUOTE_ACCEPTED", "Quote Accepted"
    QUOTE_REJECTED = "QUOTE_REJECTED", "Quote Rejected"
    PAYMENT_PROOF_UPLOADED = "PAYMENT_PROOF_UPLOADED", "Payment Proof Uploaded"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED", "Payment Confirmed"
    PAYMENT_REJECTED = "PAYMENT_REJECTED", "Payment Rejected"
    DEPOSIT_CONFIRMED = "DEPOSIT_CONFIRMED", "Deposit Confirmed"
    BALANCE_CONFIRMED = "BALANCE_CONFIRMED", "Balance Confirmed"
    FULL_PAYMENT_CONFIRMED = "FULL_PAYMENT_CONFIRMED", "Full Payment Confirmed"
    STATUS_CHANGED = "STATUS_CHANGED", "Status Changed"
    PRIORITY_CHANGED = "PRIORITY_CHANGED", "Priority Changed"
    SHIPPING_ADDRESS_UPDATED = "SHIPPING_ADDRESS_UPDATED", "Shipping Address Updated"
    SHIPMENT_CREATED = "SHIPMENT_CREATED", "Shipment Created"
    ORDER_DELIVERED = "ORDER_DELIVERED", "Order Delivered"
    REFUND_REQUESTED = "REFUND_REQUESTED", "Refund Requested"
    REFUND_PROCESSED = "REFUND_PROCESSED", "Refund Processed"
    ORDER_CANCELLED = "ORDER_CANCELLED", "Order Cancelled"
    DEPOSIT_REMINDER = "DEPOSIT_REMINDER", "Deposit Reminder"


class OrderEvent(models.Model):
    """
    Evento de auditoría asociado a un pedido.
    Registro inmutable: nunca se modifica ni elimina.
    No tiene updated_at por diseño.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.RESTRICT,
        related_name="events",
    )

    event_type = models.CharField(
        max_length=100,
        choices=EventType.choices,
    )

    event_description = models.TextField(blank=True, default="")

    metadata = models.JSONField(null=True, blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_events",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_events"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["order", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} — Order {self.order_id}"


class InternalNote(models.Model):
    """Nota interna de un pedido. Solo visible para administradores."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="internal_notes",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="internal_notes",
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "internal_notes"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Nota — Order {self.order_id}"
