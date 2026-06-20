"""
URLs administrativas de la app reviews.
"""

from django.urls import path

from .views import AdminReviewListView

urlpatterns = [
    # GET /api/v1/admin/reviews/
    path("", AdminReviewListView.as_view(), name="admin-review-list"),
]
