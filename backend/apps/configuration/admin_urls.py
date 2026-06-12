"""
URLs administrativas de la app configuration.

Registradas bajo /api/v1/admin/
"""
from django.urls import path

from . import views

urlpatterns = [
    # GET/PUT /api/v1/admin/business-config/
    path("business-config/", views.AdminBusinessConfigView.as_view(), name="admin-business-config"),

    # GET/PUT /api/v1/admin/business-hours/
    path("business-hours/", views.AdminBusinessHoursListView.as_view(), name="admin-business-hours"),

    # GET/POST /api/v1/admin/holidays/
    path("holidays/", views.AdminHolidayListCreateView.as_view(), name="admin-holidays"),

    # DELETE /api/v1/admin/holidays/{holiday_id}/
    path("holidays/<uuid:holiday_id>/", views.AdminHolidayDeleteView.as_view(), name="admin-holiday-delete"),

    # GET/PUT /api/v1/admin/payment-instructions/
    path("payment-instructions/", views.AdminPaymentInstructionsView.as_view(), name="admin-payment-instructions"),
]
