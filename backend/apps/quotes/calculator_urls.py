"""
URLs del módulo calculadora.
"""
from django.urls import path

from .views import CalculatorView

urlpatterns = [
    # POST /api/v1/admin/calculator/calculate/
    path("calculate/", CalculatorView.as_view(), name="admin-calculator"),
]
