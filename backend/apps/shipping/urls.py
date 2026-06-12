"""
URLs de la app shipping para clientes.
"""
from django.urls import path

from .views import ShipmentDetailView, ShippingAddressDetailView, ShippingAddressListCreateView

urlpatterns = [
    # GET /api/v1/shipping-addresses/  POST /api/v1/shipping-addresses/
    path("", ShippingAddressListCreateView.as_view(), name="shipping-address-list-create"),

    # GET PUT DELETE /api/v1/shipping-addresses/{address_id}/
    path(
        "<uuid:address_id>/",
        ShippingAddressDetailView.as_view(),
        name="shipping-address-detail",
    ),
]
