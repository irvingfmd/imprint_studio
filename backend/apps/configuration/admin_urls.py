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
    # GET/POST /api/v1/admin/printers/
    path("printers/", views.AdminPrinterListCreateView.as_view(), name="admin-printers"),
    # GET/PUT/DELETE /api/v1/admin/printers/{printer_id}/
    path("printers/<uuid:printer_id>/", views.AdminPrinterDetailView.as_view(), name="admin-printer-detail"),
    # GET /api/v1/admin/electricity-rate-lookup/?postal_code=29000
    path("electricity-rate-lookup/", views.ElectricityRateLookupView.as_view(), name="electricity-rate-lookup"),
]
