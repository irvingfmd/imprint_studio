"""
URLs del dashboard administrativo.
"""
from django.urls import path

from .views import AdminDashboardView

urlpatterns = [
    # GET /api/v1/admin/dashboard/
    path("", AdminDashboardView.as_view(), name="admin-dashboard"),
]
