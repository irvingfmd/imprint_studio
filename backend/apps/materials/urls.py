"""
URLs públicas de la app materials.
"""

from django.urls import path

from .views import PublicMaterialListView

urlpatterns = [
    # GET /api/v1/materials/
    path("", PublicMaterialListView.as_view(), name="material-list"),
]
