"""
URLs administrativas de la app materials.
"""

from django.urls import path

from .views import AdminMaterialDetailView, AdminMaterialListCreateView, AdminStockAdjustmentView

urlpatterns = [
    # GET/POST /api/v1/admin/materials/
    path("", AdminMaterialListCreateView.as_view(), name="admin-material-list"),
    # GET/PUT/DELETE /api/v1/admin/materials/{material_id}/
    path("<uuid:material_id>/", AdminMaterialDetailView.as_view(), name="admin-material-detail"),
    # POST /api/v1/admin/materials/{material_id}/stock/
    path("<uuid:material_id>/stock/", AdminStockAdjustmentView.as_view(), name="admin-material-stock"),
]
