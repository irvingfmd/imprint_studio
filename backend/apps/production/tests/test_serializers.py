"""
Tests de serializers de la app production.
Cubre: UpdateOrderStatusSerializer, CancelOrderSerializer.
"""
from apps.production.serializers import CancelOrderSerializer, UpdateOrderStatusSerializer


class TestUpdateOrderStatusSerializer:
    def test_status_valido(self):
        s = UpdateOrderStatusSerializer(data={"status": "PRINTING"})
        assert s.is_valid(), s.errors

    def test_status_invalido_rechazado(self):
        s = UpdateOrderStatusSerializer(data={"status": "VOLANDO"})
        assert not s.is_valid()
        assert "status" in s.errors

    def test_sin_status_es_invalido(self):
        s = UpdateOrderStatusSerializer(data={})
        assert not s.is_valid()
        assert "status" in s.errors

    def test_notes_es_opcional(self):
        s = UpdateOrderStatusSerializer(data={"status": "QUOTED"})
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == ""

    def test_notes_con_valor(self):
        s = UpdateOrderStatusSerializer(data={"status": "QUOTED", "notes": "Revisado"})
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == "Revisado"

    def test_todos_los_estados_validos_aceptados(self):
        estados_validos = [
            "RECEIVED", "PENDING_ANALYSIS", "QUOTED", "APPROVED",
            "PENDING_DEPOSIT", "DEPOSIT_PAID", "PRINTING", "POST_PROCESSING",
            "READY", "PENDING_BALANCE", "FULLY_PAID", "DELIVERED", "CANCELLED",
        ]
        for estado in estados_validos:
            s = UpdateOrderStatusSerializer(data={"status": estado})
            assert s.is_valid(), f"Estado '{estado}' debería ser válido: {s.errors}"


class TestCancelOrderSerializer:
    def test_reason_requerido(self):
        s = CancelOrderSerializer(data={})
        assert not s.is_valid()
        assert "reason" in s.errors

    def test_reason_valido(self):
        s = CancelOrderSerializer(data={"reason": "Cliente desistió"})
        assert s.is_valid(), s.errors
        assert s.validated_data["reason"] == "Cliente desistió"
