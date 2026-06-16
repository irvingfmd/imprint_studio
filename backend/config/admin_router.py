"""
Router de rutas administrativas.

Todas las rutas aquí requieren rol ADMIN.
Documentadas en 04-api-specification.md bajo /api/v1/admin/
"""
from django.urls import path, include

urlpatterns = [
    # Pedidos
    path("orders/", include("apps.orders.admin_urls")),

    # Cotizaciones
    path("quotes/", include("apps.quotes.admin_urls")),

    # Pagos
    path("payments/", include("apps.payments.admin_urls")),

    # Envíos
    path("shipments/", include("apps.shipping.admin_urls")),

    # Dashboard
    path("dashboard/", include("apps.orders.dashboard_urls")),

    # Calculadora
    path("calculator/", include("apps.quotes.calculator_urls")),

    # Configuración del negocio
    path("", include("apps.configuration.admin_urls")),

    # Usuarios
    path("users/", include("apps.authentication.admin_urls")),
]