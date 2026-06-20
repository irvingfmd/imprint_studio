"""
URLs de la app orders para clientes.
Incluye rutas nested de payments, production, quotes, eventos y archivos.
"""

from django.urls import include, path

from apps.payments.views import OrderPaymentListView
from apps.production.views import (
    OrderEventDetailView,
    OrderEventListView,
    ProductionHistoryListView,
)
from apps.quotes.views import OrderQuoteListView

from .views import (
    AssignShippingAddressView,
    CancelOrderView,
    OrderDetailView,
    OrderFileListUploadView,
    OrderListCreateView,
    RepeatOrderView,
)

urlpatterns = [
    # GET /api/v1/orders/  POST /api/v1/orders/
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    # GET /api/v1/orders/{order_id}/
    path("<uuid:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    # PUT /api/v1/orders/{order_id}/cancel/
    path("<uuid:order_id>/cancel/", CancelOrderView.as_view(), name="order-cancel"),
    # POST /api/v1/orders/{order_id}/repeat/
    path("<uuid:order_id>/repeat/", RepeatOrderView.as_view(), name="order-repeat"),
    # PUT /api/v1/orders/{order_id}/shipping-address/
    path(
        "<uuid:order_id>/shipping-address/",
        AssignShippingAddressView.as_view(),
        name="order-shipping-address",
    ),
    # GET /api/v1/orders/{order_id}/files/  POST /api/v1/orders/{order_id}/files/
    path("<uuid:order_id>/files/", OrderFileListUploadView.as_view(), name="order-files"),
    # GET /api/v1/orders/{order_id}/quotes/
    path("<uuid:order_id>/quotes/", OrderQuoteListView.as_view(), name="order-quote-list"),
    # GET /api/v1/orders/{order_id}/payments/
    path("<uuid:order_id>/payments/", OrderPaymentListView.as_view(), name="order-payment-list"),
    # GET /api/v1/orders/{order_id}/production-history/
    path(
        "<uuid:order_id>/production-history/",
        ProductionHistoryListView.as_view(),
        name="order-production-history",
    ),
    # GET /api/v1/orders/{order_id}/events/
    path("<uuid:order_id>/events/", OrderEventListView.as_view(), name="order-event-list"),
    # GET /api/v1/orders/{order_id}/events/{event_id}/
    path(
        "<uuid:order_id>/events/<uuid:event_id>/",
        OrderEventDetailView.as_view(),
        name="order-event-detail",
    ),
    # GET/POST /api/v1/orders/{order_id}/review/
    path("<uuid:order_id>/review/", include("apps.reviews.urls")),
]
