"""URLs administrativas de la app loyalty."""

from django.urls import path

from .views import AdminDiscountDetailView, AdminDiscountListCreateView, AdminDiscountRedemptionsView

urlpatterns = [
    path("", AdminDiscountListCreateView.as_view(), name="admin-discount-list"),
    path("<uuid:discount_id>/", AdminDiscountDetailView.as_view(), name="admin-discount-detail"),
    path(
        "<uuid:discount_id>/redemptions/",
        AdminDiscountRedemptionsView.as_view(),
        name="admin-discount-redemptions",
    ),
]
