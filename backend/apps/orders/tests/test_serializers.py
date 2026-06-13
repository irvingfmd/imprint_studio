"""
Tests de los serializers de orders.
"""
import pytest

from apps.orders.serializers import (
    CancelOrderSerializer,
    OrderCreateSerializer,
    RequestFileUploadSerializer,
)


class TestOrderCreateSerializer:
    def test_datos_validos_reference(self):
        s = OrderCreateSerializer(data={
            "request_type": "REFERENCE",
            "title": "Figura Grogu",
            "description": "Bebé Yoda a escala",
            "quantity": 1,
        })
        assert s.is_valid(), s.errors

    def test_datos_validos_printable_file(self):
        s = OrderCreateSerializer(data={
            "request_type": "PRINTABLE_FILE",
            "title": "Engrane",
            "description": "Adjunto STL",
            "quantity": 3,
            "priority": "URGENT",
        })
        assert s.is_valid(), s.errors

    def test_cantidad_cero_es_invalida(self):
        # Caso 10: quantity = 0 → error de validación
        s = OrderCreateSerializer(data={
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Desc",
            "quantity": 0,
        })
        assert not s.is_valid()
        assert "quantity" in s.errors

    def test_cantidad_negativa_es_invalida(self):
        s = OrderCreateSerializer(data={
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Desc",
            "quantity": -5,
        })
        assert not s.is_valid()
        assert "quantity" in s.errors

    def test_prioridad_invalida_es_rechazada(self):
        # Caso 11: prioridad inexistente
        s = OrderCreateSerializer(data={
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Desc",
            "quantity": 1,
            "priority": "SUPER_URGENTE",
        })
        assert not s.is_valid()
        assert "priority" in s.errors

    def test_request_type_invalido_es_rechazado(self):
        s = OrderCreateSerializer(data={
            "request_type": "ESCULTURA",
            "title": "Figura",
            "description": "Desc",
            "quantity": 1,
        })
        assert not s.is_valid()
        assert "request_type" in s.errors

    def test_title_requerido(self):
        s = OrderCreateSerializer(data={
            "request_type": "REFERENCE",
            "description": "Sin título",
            "quantity": 1,
        })
        assert not s.is_valid()
        assert "title" in s.errors

    def test_description_requerida(self):
        s = OrderCreateSerializer(data={
            "request_type": "REFERENCE",
            "title": "Figura",
            "quantity": 1,
        })
        assert not s.is_valid()
        assert "description" in s.errors

    def test_priority_default_es_normal(self):
        s = OrderCreateSerializer(data={
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Desc",
            "quantity": 1,
        })
        assert s.is_valid()
        assert s.validated_data["priority"] == "NORMAL"

    def test_delivery_method_default_es_pickup(self):
        s = OrderCreateSerializer(data={
            "request_type": "REFERENCE",
            "title": "Figura",
            "description": "Desc",
            "quantity": 1,
        })
        assert s.is_valid()
        assert s.validated_data["delivery_method"] == "PICKUP"


class TestCancelOrderSerializer:
    def test_reason_requerido(self):
        s = CancelOrderSerializer(data={})
        assert not s.is_valid()
        assert "reason" in s.errors

    def test_reason_valido(self):
        s = CancelOrderSerializer(data={"reason": "Cambié de opinión"})
        assert s.is_valid(), s.errors


class TestRequestFileUploadSerializer:
    def test_datos_validos(self):
        s = RequestFileUploadSerializer(data={
            "file_url": "https://cdn.test/model.stl",
            "file_type": "STL",
            "original_filename": "model.stl",
            "mime_type": "model/stl",
            "file_size_bytes": 102400,
        })
        assert s.is_valid(), s.errors

    def test_file_size_cero_es_invalido(self):
        s = RequestFileUploadSerializer(data={
            "file_url": "https://cdn.test/a.jpg",
            "file_type": "IMAGE",
            "original_filename": "a.jpg",
            "mime_type": "image/jpeg",
            "file_size_bytes": 0,
        })
        assert not s.is_valid()
        assert "file_size_bytes" in s.errors

    def test_file_type_invalido_es_rechazado(self):
        # Caso 17: tipo de archivo no permitido
        s = RequestFileUploadSerializer(data={
            "file_url": "https://cdn.test/virus.exe",
            "file_type": "EXE",
            "original_filename": "virus.exe",
            "mime_type": "application/octet-stream",
            "file_size_bytes": 1024,
        })
        assert not s.is_valid()
        assert "file_type" in s.errors
