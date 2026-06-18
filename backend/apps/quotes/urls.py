"""
URLs de la app quotes para clientes.
"""

from django.urls import path

from .views import AcceptQuoteView, QuoteDetailView, QuotePDFView, QuoteSnapshotView, RejectQuoteView

urlpatterns = [
    # GET /api/v1/quotes/{quote_id}/
    path("<uuid:quote_id>/", QuoteDetailView.as_view(), name="quote-detail"),
    # PUT /api/v1/quotes/{quote_id}/accept/
    path("<uuid:quote_id>/accept/", AcceptQuoteView.as_view(), name="quote-accept"),
    # PUT /api/v1/quotes/{quote_id}/reject/
    path("<uuid:quote_id>/reject/", RejectQuoteView.as_view(), name="quote-reject"),
    # GET /api/v1/quotes/{quote_id}/snapshot/
    path("<uuid:quote_id>/snapshot/", QuoteSnapshotView.as_view(), name="quote-snapshot"),
    # GET /api/v1/quotes/{quote_id}/pdf/
    path("<uuid:quote_id>/pdf/", QuotePDFView.as_view(), name="quote-pdf"),
]
