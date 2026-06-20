"""
URLs administrativas de la app authentication.

Documentadas en 04-api-specification.md bajo /api/v1/admin/users/
"""

from django.urls import path

from apps.authentication.views import (
    AdminCustomerPaymentHistoryView,
    AdminListUsersView,
    AdminRetrieveUserView,
    AdminUpdateUserRoleView,
)

urlpatterns = [
    # GET  /api/v1/admin/users/
    path("", AdminListUsersView.as_view(), name="admin-user-list"),
    # GET  /api/v1/admin/users/{user_id}/
    path("<uuid:user_id>/", AdminRetrieveUserView.as_view(), name="admin-user-detail"),
    # PUT  /api/v1/admin/users/{user_id}/role/
    path("<uuid:user_id>/role/", AdminUpdateUserRoleView.as_view(), name="admin-user-role"),
    # GET  /api/v1/admin/users/{user_id}/payments/
    path("<uuid:user_id>/payments/", AdminCustomerPaymentHistoryView.as_view(), name="admin-user-payments"),
]
