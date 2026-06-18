"""
URLs de envíos para clientes (lectura).
"""

from django.urls import path

from .views import ShipmentDetailView

urlpatterns = [
    # GET /api/v1/shipments/{shipment_id}/
    path("<uuid:shipment_id>/", ShipmentDetailView.as_view(), name="shipment-detail"),
]
