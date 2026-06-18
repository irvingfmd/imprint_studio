"""
URLs públicas de la app configuration.

Registradas bajo /api/v1/payment-instructions/
"""

from django.urls import path

from . import views

urlpatterns = [
    # GET /api/v1/payment-instructions/
    path("", views.PublicPaymentInstructionsView.as_view(), name="public-payment-instructions"),
]
