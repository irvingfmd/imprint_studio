"""
Vistas para la app materials.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.permissions import IsAdmin
from core.responses import created_response, error_response, success_response

from . import selectors, services
from .serializers import (
    CreateUpdateMaterialSerializer,
    MaterialSerializer,
    PublicMaterialSerializer,
    StockAdjustmentSerializer,
)


class PublicMaterialListView(APIView):
    """Lista materiales activos con colores disponibles. Público autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        materials = selectors.get_all_materials(active_only=True)
        serializer = PublicMaterialSerializer(materials, many=True)
        return success_response(
            data={"count": materials.count(), "results": serializer.data},
            message="Materials retrieved",
        )


class AdminMaterialListCreateView(APIView):
    """Lista todos los materiales o crea uno nuevo. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        active_only = request.query_params.get("active_only") == "true"
        low_stock = request.query_params.get("low_stock") == "true"
        materials = selectors.get_all_materials(active_only=active_only, low_stock=low_stock)
        serializer = MaterialSerializer(materials, many=True)
        return success_response(
            data={"count": materials.count(), "results": serializer.data},
            message="Materials retrieved",
        )

    def post(self, request):
        serializer = CreateUpdateMaterialSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        material = services.MaterialService.create_material(serializer.validated_data)
        return created_response(
            data=MaterialSerializer(material).data,
            message="Material created",
        )


class AdminMaterialDetailView(APIView):
    """Detalle, edición y eliminación de un material. Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, material_id):
        material = selectors.get_material_by_id(str(material_id))
        if not material:
            return error_response("Material not found", status_code=status.HTTP_404_NOT_FOUND)
        return success_response(data=MaterialSerializer(material).data, message="Material retrieved")

    def put(self, request, material_id):
        material = selectors.get_material_by_id(str(material_id))
        if not material:
            return error_response("Material not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = CreateUpdateMaterialSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        material = services.MaterialService.update_material(material, serializer.validated_data)
        return success_response(data=MaterialSerializer(material).data, message="Material updated")

    def delete(self, request, material_id):
        material = selectors.get_material_by_id(str(material_id))
        if not material:
            return error_response("Material not found", status_code=status.HTTP_404_NOT_FOUND)
        material.delete()
        return success_response(data={}, message="Material deleted")


class AdminStockAdjustmentView(APIView):
    """Ajusta el stock de un material (agregar o descontar). Solo admin."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, material_id):
        material = selectors.get_material_by_id(str(material_id))
        if not material:
            return error_response("Material not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = StockAdjustmentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation error", errors=serializer.errors)

        try:
            if serializer.validated_data["operation"] == "add":
                material = services.MaterialService.add_stock(material, serializer.validated_data["grams"])
            else:
                material = services.MaterialService.deduct_stock(material, serializer.validated_data["grams"])
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(
            data={"stock_grams": str(material.stock_grams)},
            message="Stock adjusted",
        )
