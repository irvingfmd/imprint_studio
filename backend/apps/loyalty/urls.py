"""URLs públicas de la app loyalty."""

from django.urls import path

from .views import ValidateDiscountCodeView

urlpatterns = [
    path("validate/", ValidateDiscountCodeView.as_view(), name="discount-validate"),
]
