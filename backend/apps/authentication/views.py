"""
Views de la app authentication.

Endpoints de registro, OTP y JWT.
Documentados en 04-api-specification.md
"""
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.serializers import (
    RegisterSerializer,
    SendOTPSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from apps.authentication.services import JWTService, OTPService, RegisterService
from core.responses import created_response, error_response, success_response
from core.throttles import OTPSendThrottle, OTPVerifyThrottle

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    Registro de nuevos usuarios.
    POST /api/v1/auth/register/
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        RegisterService().register(serializer.validated_data)

        return created_response(
            message="User registered successfully",
        )


class SendOTPView(APIView):
    """
    Solicitar envío de código OTP.
    POST /api/v1/auth/otp/send/
    """

    permission_classes = [AllowAny]
    throttle_classes = [OTPSendThrottle]

    def post(self, request: Request) -> Response:
        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        otp = OTPService().generate_and_send(
            phone=serializer.validated_data["phone"],
        )

        # En desarrollo incluir el código en la respuesta para facilitar pruebas.
        data = {}
        if settings.DEBUG and otp is not None:
            data["dev_code"] = otp.code

        return success_response(
            data=data if data else None,
            message="OTP sent successfully",
        )


class VerifyOTPView(APIView):
    """
    Verificar código OTP y obtener tokens JWT.
    POST /api/v1/auth/otp/verify/
    """

    permission_classes = [AllowAny]
    throttle_classes = [OTPVerifyThrottle]

    def post(self, request: Request) -> Response:
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = OTPService().verify(
                phone=serializer.validated_data["phone"],
                code=serializer.validated_data["otp_code"],
            )
        except ValueError as e:
            return error_response(
                message=str(e),
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = JWTService().generate_tokens(user)

        return Response(tokens, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    Información del usuario autenticado.
    GET /api/v1/auth/me/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)