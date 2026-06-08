"""
URLs principales de Imprint Studio.

Todas las rutas de la API viven bajo /api/v1/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel de administración de Django
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/", include("config.api_router")),
]