"""
Throttle classes para endpoints sensibles.
Configuradas en settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].
"""
from rest_framework.throttling import AnonRateThrottle


class OTPSendThrottle(AnonRateThrottle):
    """Máximo 5 solicitudes de OTP por hora por IP."""
    scope = "otp_send"


class OTPVerifyThrottle(AnonRateThrottle):
    """Máximo 10 intentos de verificación de OTP por hora por IP."""
    scope = "otp_verify"
