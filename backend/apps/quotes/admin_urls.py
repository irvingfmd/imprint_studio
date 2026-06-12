"""
URLs administrativas de la app quotes.
"""
from django.urls import path

from .views import AdminExpireQuoteView

urlpatterns = [
    # PUT /api/v1/admin/quotes/{quote_id}/expire/
    path("<uuid:quote_id>/expire/", AdminExpireQuoteView.as_view(), name="admin-quote-expire"),
]
