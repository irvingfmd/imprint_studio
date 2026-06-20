"""
Servicios para la app loyalty.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from apps.authentication.models import User
from apps.orders.models import Order

from .models import DiscountCode, DiscountRedemption, DiscountType


class DiscountService:
    @staticmethod
    def validate_code(code: str, order_total: Decimal) -> DiscountCode:
        """Valida un código de descuento. Lanza ValueError si no es válido."""
        try:
            discount = DiscountCode.objects.get(code=code.upper())
        except DiscountCode.DoesNotExist:
            raise ValueError("Código de descuento no encontrado.")

        if not discount.is_active:
            raise ValueError("Este código de descuento ya no está activo.")

        now = timezone.now()
        if now < discount.valid_from:
            raise ValueError("Este código aún no es válido.")
        if discount.valid_until and now > discount.valid_until:
            raise ValueError("Este código de descuento ha expirado.")

        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise ValueError("Este código ha alcanzado el límite de usos.")

        if order_total < discount.min_order_amount:
            raise ValueError(
                f"El monto mínimo para usar este código es ${discount.min_order_amount}."
            )

        return discount

    @staticmethod
    def calculate_discount(discount_code: DiscountCode, order_total: Decimal) -> Decimal:
        """Calcula el monto a descontar."""
        if discount_code.discount_type == DiscountType.PERCENTAGE:
            amount = order_total * (discount_code.discount_value / Decimal("100"))
        else:
            amount = discount_code.discount_value

        amount = min(amount, order_total)
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    @transaction.atomic
    def apply_discount(
        code: str, order: Order, customer: User, order_total: Decimal
    ) -> Decimal:
        """Aplica un descuento: valida, crea redemption, incrementa usos."""
        discount = DiscountService.validate_code(code, order_total)
        discount_amount = DiscountService.calculate_discount(discount, order_total)

        DiscountRedemption.objects.create(
            discount_code=discount,
            order=order,
            customer=customer,
            discount_applied=discount_amount,
        )

        discount.current_uses += 1
        discount.save(update_fields=["current_uses", "updated_at"])

        return discount_amount
