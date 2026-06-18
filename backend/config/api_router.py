"""
Router principal de la API v1.

Agrupa todas las rutas por módulo siguiendo la especificación
documentada en 04-api-specification.md.
"""

from django.urls import include, path

urlpatterns = [
    # Autenticación
    path("auth/", include("apps.authentication.urls")),
    # Pedidos (clientes)
    path("orders/", include("apps.orders.urls")),
    # Cotizaciones (clientes)
    path("quotes/", include("apps.quotes.urls")),
    # Pagos (clientes)
    path("payments/", include("apps.payments.urls")),
    # Direcciones de envío (clientes)
    path("shipping-addresses/", include("apps.shipping.urls")),
    # Envíos (clientes — lectura)
    path("shipments/", include("apps.shipping.shipment_urls")),
    # Instrucciones de pago (público autenticado)
    path("payment-instructions/", include("apps.configuration.urls")),
    # FAQ (público)
    path("faq/", include("apps.faq.urls")),
    # Rutas administrativas
    path("admin/", include("config.admin_router")),
]
