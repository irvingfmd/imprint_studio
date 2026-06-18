"""
Helpers para construir respuestas estándar de la API.

Formato documentado en 04-api-specification.md:
    {
        "success": true/false,
        "message": "...",
        "data": {...}
    }
"""

from rest_framework import status
from rest_framework.response import Response


def success_response(
    data=None,
    message: str = "Operation completed successfully",
    status_code: int = status.HTTP_200_OK,
) -> Response:
    """
    Construye una respuesta exitosa en formato estándar.
    """
    payload = {
        "success": True,
        "message": message,
    }

    if data is not None:
        payload["data"] = data

    return Response(payload, status=status_code)


def created_response(
    data=None,
    message: str = "Resource created successfully",
) -> Response:
    """
    Respuesta para recursos creados (201).
    """
    return success_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED,
    )


def error_response(
    message: str = "An error occurred",
    errors=None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    """
    Construye una respuesta de error en formato estándar.
    """
    payload = {
        "success": False,
        "message": message,
    }

    if errors is not None:
        payload["errors"] = errors

    return Response(payload, status=status_code)
