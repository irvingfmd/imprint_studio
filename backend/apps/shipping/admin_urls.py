"""
URLs administrativas de la app shipping.
"""

from django.urls import path

from .views import AdminMarkShipmentDeliveredView

urlpatterns = [
    # PUT /api/v1/admin/shipments/{shipment_id}/delivered/
    path(
        "<uuid:shipment_id>/delivered/",
        AdminMarkShipmentDeliveredView.as_view(),
        name="admin-shipment-delivered",
    ),
]
