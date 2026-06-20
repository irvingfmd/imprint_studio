"""
Vistas para la app reviews.

Las rutas de cliente se registran bajo /api/v1/orders/{order_id}/review/
Las rutas admin se registran bajo /api/v1/admin/reviews/
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.orders.selectors import get_order_by_id
from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import CreateReviewSerializer, ReviewSerializer


class OrderReviewView(APIView):
    """GET la reseña de un pedido. Dueño del pedido o admin."""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_order_by_id(str(order_id))
        if not order:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        if order.customer_id != request.user.id and not request.user.is_admin:
            return error_response("Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        review = selectors.get_review_for_order(str(order_id))
        if not review:
            return success_response(data=None, message="No review yet")

        serializer = ReviewSerializer(review)
        return success_response(data=serializer.data, message="Review retrieved")


class CreateReviewView(APIView):
    """POST crea una reseña para un pedido entregado. Solo el dueño."""

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        serializer = CreateReviewSerializer(data=request.data)
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
            review = services.ReviewService.create_review(
                order=order,
                customer=request.user,
                rating=serializer.validated_data["rating"],
                comment=serializer.validated_data.get("comment", ""),
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return created_response(
            data=ReviewSerializer(review).data,
            message="Review created",
        )


class AdminReviewListView(APIView):
    """Lista todas las reseñas con paginación. Solo admin."""

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

        reviews = selectors.get_all_reviews()
        paginator = Paginator(reviews, page_size)
        page = paginator.get_page(request.query_params.get("page", 1))
        serializer = ReviewSerializer(page.object_list, many=True)
        return success_response(
            data={
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "results": serializer.data,
            },
            message="Reviews retrieved",
        )
