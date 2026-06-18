"""
URLs de la app authentication.

Documentadas en 04-api-specification.md bajo /api/v1/auth/
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.authentication.views import (
    LogoutView,
    MeView,
    RegisterView,
    SendOTPView,
    VerifyOTPView,
)

urlpatterns = [
    # Registro
    path("register/", RegisterView.as_view(), name="auth-register"),
    # OTP
    path("otp/send/", SendOTPView.as_view(), name="auth-otp-send"),
    path("otp/verify/", VerifyOTPView.as_view(), name="auth-otp-verify"),
    # JWT
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    # Usuario autenticado
    path("me/", MeView.as_view(), name="auth-me"),
]
