"""
Tests de serializers de la app production.
Cubre: UpdateOrderStatusSerializer, CancelOrderSerializer.
"""

from apps.production.serializers import CancelOrderSerializer, UpdateOrderStatusSerializer


class TestUpdateOrderStatusSerializer:
    def test_valid_status(self):
        s = UpdateOrderStatusSerializer(data={"status": "PRINTING"})
        assert s.is_valid(), s.errors

    def test_invalid_status_rejected(self):
        s = UpdateOrderStatusSerializer(data={"status": "VOLANDO"})
        assert not s.is_valid()
        assert "status" in s.errors

    def test_missing_status_is_invalid(self):
        s = UpdateOrderStatusSerializer(data={})
        assert not s.is_valid()
        assert "status" in s.errors

    def test_notes_is_optional(self):
        s = UpdateOrderStatusSerializer(data={"status": "QUOTED"})
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == ""

    def test_notes_with_value(self):
        s = UpdateOrderStatusSerializer(data={"status": "QUOTED", "notes": "Revisado"})
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == "Revisado"

    def test_all_valid_statuses_accepted(self):
        valid_statuses = [
            "RECEIVED",
            "PENDING_ANALYSIS",
            "QUOTED",
            "APPROVED",
            "PENDING_DEPOSIT",
            "DEPOSIT_PAID",
            "PRINTING",
            "POST_PROCESSING",
            "READY",
            "PENDING_BALANCE",
            "FULLY_PAID",
            "DELIVERED",
            "CANCELLED",
        ]
        for status in valid_statuses:
            s = UpdateOrderStatusSerializer(data={"status": status})
            assert s.is_valid(), f"Estado '{status}' debería ser válido: {s.errors}"


class TestCancelOrderSerializer:
    def test_reason_required(self):
        s = CancelOrderSerializer(data={})
        assert not s.is_valid()
        assert "reason" in s.errors

    def test_reason_valid(self):
        s = CancelOrderSerializer(data={"reason": "Cliente desistió"})
        assert s.is_valid(), s.errors
        assert s.validated_data["reason"] == "Cliente desistió"
