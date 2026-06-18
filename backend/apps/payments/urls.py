"""
URLs de la app payments para clientes.

Rutas registradas bajo /api/v1/payments/
La ruta nested /api/v1/orders/{order_id}/payments/ vive en apps/orders/urls.py
"""

from django.urls import path

from . import views

urlpatterns = [
    # GET /api/v1/payments/{payment_id}/
    path("<uuid:payment_id>/", views.PaymentDetailView.as_view(), name="payment-detail"),
    # POST /api/v1/payments/{payment_id}/proof/
    path("<uuid:payment_id>/proof/", views.PaymentProofView.as_view(), name="payment-proof"),
]
