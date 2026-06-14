"""
Throttle classes para endpoints sensibles.
Configuradas en settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].
En modo DEBUG el throttle se desactiva para facilitar el desarrollo.
"""
from django.conf import settings
from rest_framework.throttling import AnonRateThrottle


class OTPSendThrottle(AnonRateThrottle):
    """Máximo 5 solicitudes de OTP por hora por IP."""
    scope = "otp_send"

    def allow_request(self, request, view):
        if settings.DEBUG:
            return True
        return super().allow_request(request, view)


class OTPVerifyThrottle(AnonRateThrottle):
    """Máximo 10 intentos de verificación de OTP por hora por IP."""
    scope = "otp_verify"

    def allow_request(self, request, view):
        if settings.DEBUG:
            return True
        return super().allow_request(request, view)
