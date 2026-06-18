"""
URLs principales de Imprint Studio.

Todas las rutas de la API viven bajo /api/v1/
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Panel de administración de Django
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/", include("config.api_router")),
]

# Servir archivos de media en desarrollo (comprobantes de pago, etc.)
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
