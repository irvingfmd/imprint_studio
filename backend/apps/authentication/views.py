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

from apps.authentication.selectors import get_all_users, get_user_by_id
from apps.authentication.serializers import (
    AdminUserSerializer,
    RegisterSerializer,
    SendOTPSerializer,
    UpdateUserRoleSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from apps.authentication.models import UserRole
from apps.authentication.services import JWTService, OTPService, RegisterService
from core.permissions import IsAdmin
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

        # En desarrollo incluir el código en claro para facilitar pruebas.
        data = {}
        if settings.DEBUG and otp is not None:
            data["dev_code"] = getattr(otp, "_raw_code", None)

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

        return success_response(data=tokens, message="OTP verified successfully")


class LogoutView(APIView):
    """
    Invalida el refresh token en el servidor.
    POST /api/v1/auth/logout/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError

        refresh = request.data.get("refresh")
        if not refresh:
            return error_response(
                "Se requiere el refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            pass
        return success_response(data={}, message="Logged out")


class MeView(APIView):
    """
    Información del usuario autenticado.
    GET /api/v1/auth/me/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)


class AdminListUsersView(APIView):
    """
    Lista todos los usuarios del sistema.
    GET /api/v1/admin/users/
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request: Request) -> Response:
        from django.core.paginator import Paginator
        try:
            page_size = max(1, min(int(request.query_params.get("page_size", 20)), 100))
        except (ValueError, TypeError):
            return error_response("page_size debe ser un entero positivo.", status_code=status.HTTP_400_BAD_REQUEST)

        users = get_all_users()
        page_num = request.query_params.get("page", 1)
        paginator = Paginator(users, page_size)
        page = paginator.get_page(page_num)
        serializer = AdminUserSerializer(page.object_list, many=True)
        return success_response(
            data={
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "results": serializer.data,
            },
            message="Users retrieved",
        )


class AdminRetrieveUserView(APIView):
    """
    Detalle de un usuario.
    GET /api/v1/admin/users/{user_id}/
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request: Request, user_id) -> Response:
        user = get_user_by_id(str(user_id))
        if not user:
            return error_response("User not found", status_code=status.HTTP_404_NOT_FOUND)
        serializer = AdminUserSerializer(user)
        return success_response(data=serializer.data, message="User retrieved")


class AdminUpdateUserRoleView(APIView):
    """
    Cambia el rol de un usuario (CUSTOMER ↔ ADMIN).
    PUT /api/v1/admin/users/{user_id}/role/
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request: Request, user_id) -> Response:
        serializer = UpdateUserRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = get_user_by_id(str(user_id))
        if not user:
            return error_response("User not found", status_code=status.HTTP_404_NOT_FOUND)

        # Un admin no puede cambiar su propio rol — evita bloqueo accidental.
        if user.id == request.user.id:
            return error_response(
                "No puedes cambiar tu propio rol.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        new_role = serializer.validated_data["role"]
        user.role = new_role
        # is_staff controla acceso al panel Django — se sincroniza con el rol.
        user.is_staff = (new_role == UserRole.ADMIN)
        user.save(update_fields=["role", "is_staff", "updated_at"])

        logger.info("Rol de usuario %s cambiado a %s por %s", user.phone, new_role, request.user.phone)

        return success_response(
            data=AdminUserSerializer(user).data,
            message="User role updated",
        )