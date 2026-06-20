"""
Vistas para la app loyalty.
"""

from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import (
    CreateDiscountCodeSerializer,
    DiscountCodeSerializer,
    DiscountRedemptionSerializer,
    ValidateDiscountCodeSerializer,
)


# --- Vistas para clientes ---


class ValidateDiscountCodeView(APIView):
    """Valida un código de descuento sin aplicarlo."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ValidateDiscountCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        try:
            discount = services.DiscountService.validate_code(
                code=serializer.validated_data["code"],
                order_total=Decimal("999999"),
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(
            data={
                "code": discount.code,
                "discount_type": discount.discount_type,
                "discount_value": str(discount.discount_value),
                "min_order_amount": str(discount.min_order_amount),
            },
            message="Discount code is valid",
        )


# --- Vistas administrativas ---


class AdminDiscountListCreateView(APIView):
    """Lista y crea códigos de descuento. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        active_only = request.query_params.get("active_only", "").lower() == "true"
        codes = selectors.get_all_discount_codes(active_only=active_only)
        serializer = DiscountCodeSerializer(codes, many=True)
        return success_response(
            data={"count": codes.count(), "results": serializer.data},
            message="Discount codes retrieved",
        )

    def post(self, request):
        serializer = CreateDiscountCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        from .models import DiscountCode

        if DiscountCode.objects.filter(code=serializer.validated_data["code"]).exists():
            return error_response(
                "Ya existe un código con ese nombre.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        code = DiscountCode.objects.create(**serializer.validated_data)
        return created_response(
            data=DiscountCodeSerializer(code).data,
            message="Discount code created",
        )


class AdminDiscountDetailView(APIView):
    """Detalle, edición y eliminación de un código de descuento. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, discount_id):
        code = selectors.get_discount_code_by_id(str(discount_id))
        if not code:
            return error_response("Discount code not found", status_code=status.HTTP_404_NOT_FOUND)
        return success_response(data=DiscountCodeSerializer(code).data, message="Discount code retrieved")

    def put(self, request, discount_id):
        code = selectors.get_discount_code_by_id(str(discount_id))
        if not code:
            return error_response("Discount code not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = CreateDiscountCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        data = serializer.validated_data
        for field, value in data.items():
            setattr(code, field, value)
        code.save()

        return success_response(data=DiscountCodeSerializer(code).data, message="Discount code updated")

    def delete(self, request, discount_id):
        code = selectors.get_discount_code_by_id(str(discount_id))
        if not code:
            return error_response("Discount code not found", status_code=status.HTTP_404_NOT_FOUND)

        code.is_active = False
        code.save(update_fields=["is_active", "updated_at"])
        return success_response(data={}, message="Discount code deactivated")


class AdminDiscountRedemptionsView(APIView):
    """Lista las redenciones de un código de descuento. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, discount_id):
        code = selectors.get_discount_code_by_id(str(discount_id))
        if not code:
            return error_response("Discount code not found", status_code=status.HTTP_404_NOT_FOUND)

        redemptions = selectors.get_redemptions_for_discount(str(discount_id))
        serializer = DiscountRedemptionSerializer(redemptions, many=True)
        return success_response(
            data={"count": redemptions.count(), "results": serializer.data},
            message="Redemptions retrieved",
        )
