"""
Tests de los serializers de orders.
"""

from apps.orders.serializers import (
    CancelOrderSerializer,
    OrderCreateSerializer,
    RequestFileUploadSerializer,
)


class TestOrderCreateSerializer:
    def test_valid_data_reference(self):
        s = OrderCreateSerializer(
            data={
                "request_type": "REFERENCE",
                "title": "Figura Grogu",
                "description": "Bebé Yoda a escala",
                "quantity": 1,
            }
        )
        assert s.is_valid(), s.errors

    def test_valid_data_printable_file(self):
        s = OrderCreateSerializer(
            data={
                "request_type": "PRINTABLE_FILE",
                "title": "Engrane",
                "description": "Adjunto STL",
                "quantity": 3,
                "priority": "URGENT",
            }
        )
        assert s.is_valid(), s.errors

    def test_zero_quantity_is_invalid(self):
        # Caso 10: quantity = 0 → error de validación
        s = OrderCreateSerializer(
            data={
                "request_type": "REFERENCE",
                "title": "Figura",
                "description": "Desc",
                "quantity": 0,
            }
        )
        assert not s.is_valid()
        assert "quantity" in s.errors

    def test_negative_quantity_is_invalid(self):
        s = OrderCreateSerializer(
            data={
                "request_type": "REFERENCE",
                "title": "Figura",
                "description": "Desc",
                "quantity": -5,
            }
        )
        assert not s.is_valid()
        assert "quantity" in s.errors

    def test_invalid_priority_is_rejected(self):
        # Caso 11: prioridad inexistente
        s = OrderCreateSerializer(
            data={
                "request_type": "REFERENCE",
                "title": "Figura",
                "description": "Desc",
                "quantity": 1,
                "priority": "SUPER_URGENTE",
            }
        )
        assert not s.is_valid()
        assert "priority" in s.errors

    def test_invalid_request_type_is_rejected(self):
        s = OrderCreateSerializer(
            data={
                "request_type": "ESCULTURA",
                "title": "Figura",
                "description": "Desc",
                "quantity": 1,
            }
        )
        assert not s.is_valid()
        assert "request_type" in s.errors

    def test_title_required(self):
        s = OrderCreateSerializer(
            data={
                "request_type": "REFERENCE",
                "description": "Sin título",
                "quantity": 1,
            }
        )
        assert not s.is_valid()
        assert "title" in s.errors

    def test_description_required(self):
        s = OrderCreateSerializer(
            data={
                "request_type": "REFERENCE",
                "title": "Figura",
                "quantity": 1,
            }
        )
        assert not s.is_valid()
        assert "description" in s.errors

    def test_priority_default_is_normal(self):
        s = OrderCreateSerializer(
            data={
                "request_type": "REFERENCE",
                "title": "Figura",
                "description": "Desc",
                "quantity": 1,
            }
        )
        assert s.is_valid()
        assert s.validated_data["priority"] == "NORMAL"

    def test_delivery_method_default_is_pickup(self):
        s = OrderCreateSerializer(
            data={
                "request_type": "REFERENCE",
                "title": "Figura",
                "description": "Desc",
                "quantity": 1,
            }
        )
        assert s.is_valid()
        assert s.validated_data["delivery_method"] == "PICKUP"


class TestCancelOrderSerializer:
    def test_reason_required(self):
        s = CancelOrderSerializer(data={})
        assert not s.is_valid()
        assert "reason" in s.errors

    def test_reason_valid(self):
        s = CancelOrderSerializer(data={"reason": "Cambié de opinión"})
        assert s.is_valid(), s.errors


class TestRequestFileUploadSerializer:
    def test_valid_data(self):
        s = RequestFileUploadSerializer(
            data={
                "file_url": "https://cdn.test/model.stl",
                "file_type": "STL",
                "original_filename": "model.stl",
                "mime_type": "model/stl",
                "file_size_bytes": 102400,
            }
        )
        assert s.is_valid(), s.errors

    def test_zero_file_size_is_invalid(self):
        s = RequestFileUploadSerializer(
            data={
                "file_url": "https://cdn.test/a.jpg",
                "file_type": "IMAGE",
                "original_filename": "a.jpg",
                "mime_type": "image/jpeg",
                "file_size_bytes": 0,
            }
        )
        assert not s.is_valid()
        assert "file_size_bytes" in s.errors

    def test_web_model_solo_requiere_url_y_nombre(self):
        s = RequestFileUploadSerializer(
            data={
                "file_url": "https://makerworld.com/models/12345",
                "file_type": "WEB_MODEL",
                "original_filename": "Yoda Mini.html",
            }
        )
        assert s.is_valid(), s.errors
        assert s.validated_data["mime_type"] == "text/uri-list"
        assert s.validated_data["file_size_bytes"] == 0

    def test_web_model_con_url_invalida_es_rechazado(self):
        s = RequestFileUploadSerializer(
            data={
                "file_url": "no-es-una-url",
                "file_type": "WEB_MODEL",
                "original_filename": "modelo.html",
            }
        )
        assert not s.is_valid()
        assert "file_url" in s.errors

    def test_invalid_file_type_is_rejected(self):
        # Caso 17: tipo de archivo no permitido
        s = RequestFileUploadSerializer(
            data={
                "file_url": "https://cdn.test/virus.exe",
                "file_type": "EXE",
                "original_filename": "virus.exe",
                "mime_type": "application/octet-stream",
                "file_size_bytes": 1024,
            }
        )
        assert not s.is_valid()
        assert "file_type" in s.errors
