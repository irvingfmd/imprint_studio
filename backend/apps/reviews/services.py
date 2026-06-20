"""
Servicios para la app reviews.
"""

from django.db import transaction

from apps.orders.models import Order, OrderStatus

from .models import Review


class ReviewService:
    @staticmethod
    @transaction.atomic
    def create_review(order: Order, customer, rating: int, comment: str = "") -> Review:
        """
        Crea una reseña para un pedido entregado.
        Solo el dueño del pedido puede dejar reseña y solo si está en DELIVERED.
        """
        if order.status != OrderStatus.DELIVERED:
            raise ValueError("Solo puedes calificar pedidos entregados.")

        if order.customer_id != customer.id:
            raise ValueError("Solo el dueño del pedido puede dejar una reseña.")

        if Review.objects.filter(order=order).exists():
            raise ValueError("Este pedido ya tiene una reseña.")

        return Review.objects.create(
            order=order,
            customer=customer,
            rating=rating,
            comment=comment,
        )
