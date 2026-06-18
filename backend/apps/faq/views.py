"""
Vistas para la app faq.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import FAQCreateUpdateSerializer, FAQSerializer


class FAQListView(APIView):
    """Lista pública de preguntas frecuentes activas."""

    permission_classes = [AllowAny]

    def get(self, request):
        faqs = selectors.get_active_faqs()
        serializer = FAQSerializer(faqs, many=True)
        return success_response(
            data={"count": faqs.count(), "results": serializer.data},
            message="FAQs retrieved",
        )


class AdminFAQListCreateView(APIView):
    """Lista todas las FAQs o crea una nueva. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        faqs = selectors.get_all_faqs()
        serializer = FAQSerializer(faqs, many=True)
        return success_response(
            data={"count": faqs.count(), "results": serializer.data},
            message="FAQs retrieved",
        )

    def post(self, request):
        serializer = FAQCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        faq = services.FAQService.create_faq(serializer.validated_data)
        return created_response(
            data=FAQSerializer(faq).data,
            message="FAQ created",
        )


class AdminFAQDetailView(APIView):
    """Detalle, actualización o eliminación de una FAQ. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, faq_id):
        faq = selectors.get_faq_by_id(str(faq_id))
        if not faq:
            return error_response("FAQ not found", status_code=status.HTTP_404_NOT_FOUND)
        return success_response(data=FAQSerializer(faq).data, message="FAQ retrieved")

    def put(self, request, faq_id):
        faq = selectors.get_faq_by_id(str(faq_id))
        if not faq:
            return error_response("FAQ not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = FAQCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        faq = services.FAQService.update_faq(faq, serializer.validated_data)
        return success_response(data=FAQSerializer(faq).data, message="FAQ updated")

    def delete(self, request, faq_id):
        faq = selectors.get_faq_by_id(str(faq_id))
        if not faq:
            return error_response("FAQ not found", status_code=status.HTTP_404_NOT_FOUND)

        services.FAQService.delete_faq(faq)
        return success_response(data={}, message="FAQ deleted")
