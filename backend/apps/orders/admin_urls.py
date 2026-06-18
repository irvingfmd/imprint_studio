"""
URLs administrativas de la app orders.
Incluye pedidos, pagos manuales, reembolsos, estado, cancelación, cotizaciones y envíos.
"""

from django.urls import path

from apps.payments.views import AdminManualConfirmationView, AdminRefundView
from apps.production.views import AdminCancelOrderView, AdminUpdateOrderStatusView
from apps.quotes.views import AdminCreateQuoteView
from apps.shipping.views import AdminCreateShipmentView

from .views import AdminOrderDetailView, AdminOrderListView

urlpatterns = [
    # GET /api/v1/admin/orders/
    path("", AdminOrderListView.as_view(), name="admin-order-list"),
    # GET /api/v1/admin/orders/{order_id}/
    path("<uuid:order_id>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),
    # PUT /api/v1/admin/orders/{order_id}/status/
    path("<uuid:order_id>/status/", AdminUpdateOrderStatusView.as_view(), name="admin-order-status"),
    # PUT /api/v1/admin/orders/{order_id}/cancel/
    path("<uuid:order_id>/cancel/", AdminCancelOrderView.as_view(), name="admin-order-cancel"),
    # POST /api/v1/admin/orders/{order_id}/quote/
    path("<uuid:order_id>/quote/", AdminCreateQuoteView.as_view(), name="admin-order-quote"),
    # POST /api/v1/admin/orders/{order_id}/shipment/
    path("<uuid:order_id>/shipment/", AdminCreateShipmentView.as_view(), name="admin-order-shipment"),
    # POST /api/v1/admin/orders/{order_id}/payments/manual-confirmation/
    path(
        "<uuid:order_id>/payments/manual-confirmation/",
        AdminManualConfirmationView.as_view(),
        name="admin-order-manual-payment",
    ),
    # POST /api/v1/admin/orders/{order_id}/refund/
    path("<uuid:order_id>/refund/", AdminRefundView.as_view(), name="admin-order-refund"),
]
