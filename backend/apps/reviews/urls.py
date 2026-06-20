"""
URLs de reseñas para clientes.
Se incluyen bajo /api/v1/orders/{order_id}/ desde orders/urls.py.
"""

from django.urls import path

from .views import CreateReviewView, OrderReviewView

urlpatterns = [
    # GET /api/v1/orders/{order_id}/review/
    path("", OrderReviewView.as_view(), name="order-review"),
    # POST /api/v1/orders/{order_id}/review/
    path("create/", CreateReviewView.as_view(), name="order-review-create"),
]
