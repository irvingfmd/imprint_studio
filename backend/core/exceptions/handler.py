"""
Handler global de excepciones para Django REST Framework.

Normaliza todas las respuestas de error al formato estándar
documentado en 04-api-specification.md:

    {
        "success": false,
        "message": "...",
        "errors": {...}
    }
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context) -> Response | None:
    """
    Reemplaza el handler por defecto de DRF para normalizar
    todas las respuestas de error al formato estándar del sistema.
    """
    # Llamar al handler por defecto primero para que DRF procese
    # la excepción y nos devuelva la respuesta base.
    response = exception_handler(exc, context)

    if response is None:
        # Error no manejado por DRF (500). Django lo captura aparte.
        logger.exception("Error no manejado: %s", exc)
        return None

    error_data = {
        "success": False,
        "message": _get_error_message(response.status_code),
    }

    # Agregar errores de validación solo cuando aplica.
    errors = _extract_validation_errors(response.data)
    if errors:
        error_data["errors"] = errors

    response.data = error_data
    return response


def _get_error_message(status_code: int) -> str:
    """
    Devuelve el mensaje estándar según el código HTTP.
    """
    messages = {
        status.HTTP_400_BAD_REQUEST: "Validation error",
        status.HTTP_401_UNAUTHORIZED: "Authentication required",
        status.HTTP_403_FORBIDDEN: "Permission denied",
        status.HTTP_404_NOT_FOUND: "Resource not found",
        status.HTTP_405_METHOD_NOT_ALLOWED: "Method not allowed",
        status.HTTP_409_CONFLICT: "Conflict",
        status.HTTP_429_TOO_MANY_REQUESTS: "Too many requests",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
    }
    return messages.get(status_code, "An error occurred")


def _extract_validation_errors(data) -> dict | None:
    """
    Extrae errores de validación por campo.
    Solo aplica para errores 400 con detalle por campo.
    """
    if not isinstance(data, dict):
        return None

    # Errores simples con campo 'detail' no son errores de validación por campo.
    if list(data.keys()) == ["detail"]:
        return None

    return data