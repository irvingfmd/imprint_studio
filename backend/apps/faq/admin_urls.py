"""
URLs administrativas de la app faq.
"""

from django.urls import path

from .views import AdminFAQDetailView, AdminFAQListCreateView

urlpatterns = [
    path("", AdminFAQListCreateView.as_view(), name="admin-faq-list-create"),
    path("<uuid:faq_id>/", AdminFAQDetailView.as_view(), name="admin-faq-detail"),
]
