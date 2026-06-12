"""
URLs administrativas de la app payments.

Rutas registradas bajo /api/v1/admin/payments/
Las rutas nested bajo /api/v1/admin/orders/{order_id}/ viven en apps/orders/admin_urls.py
"""
from django.urls import path

from . import views

urlpatterns = [
    # GET /api/v1/admin/payments/
    path("", views.AdminPaymentListView.as_view(), name="admin-payment-list"),

    # PUT /api/v1/admin/payments/{payment_id}/confirm/
    path("<uuid:payment_id>/confirm/", views.AdminConfirmPaymentView.as_view(), name="admin-payment-confirm"),

    # PUT /api/v1/admin/payments/{payment_id}/reject/
    path("<uuid:payment_id>/reject/", views.AdminRejectPaymentView.as_view(), name="admin-payment-reject"),
]
