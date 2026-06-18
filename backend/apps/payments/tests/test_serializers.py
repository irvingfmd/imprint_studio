"""
Tests de serializers de la app payments.
Cubre: PaymentProofSerializer, ManualConfirmationSerializer,
       ConfirmPaymentSerializer, RejectPaymentSerializer, RefundSerializer.
"""

from apps.payments.serializers import (
    ConfirmPaymentSerializer,
    ManualConfirmationSerializer,
    PaymentProofSerializer,
    RefundSerializer,
    RejectPaymentSerializer,
)


class TestPaymentProofSerializer:
    def test_valid_url(self):
        s = PaymentProofSerializer(data={"file_url": "https://cdn.example.com/comprobante.pdf"})
        assert s.is_valid(), s.errors

    def test_invalid_url_rejected(self):
        s = PaymentProofSerializer(data={"file_url": "no-es-una-url"})
        assert not s.is_valid()
        assert "file_url" in s.errors

    def test_missing_url_is_invalid(self):
        s = PaymentProofSerializer(data={})
        assert not s.is_valid()
        assert "file_url" in s.errors


class TestManualConfirmationSerializer:
    def test_valid_data(self):
        data = {
            "payment_type": "DEPOSIT",
            "payment_method": "BANK_TRANSFER",
            "amount": "218.24",
        }
        s = ManualConfirmationSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_notes_optional(self):
        data = {
            "payment_type": "FULL_PAYMENT",
            "payment_method": "CASH",
            "amount": "500.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == ""

    def test_zero_amount_is_invalid(self):
        data = {
            "payment_type": "DEPOSIT",
            "payment_method": "BANK_TRANSFER",
            "amount": "0.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert not s.is_valid()
        assert "amount" in s.errors

    def test_negative_amount_is_invalid(self):
        data = {
            "payment_type": "DEPOSIT",
            "payment_method": "BANK_TRANSFER",
            "amount": "-100.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert not s.is_valid()
        assert "amount" in s.errors

    def test_invalid_payment_type_rejected(self):
        data = {
            "payment_type": "CRYPTO",
            "payment_method": "BANK_TRANSFER",
            "amount": "100.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert not s.is_valid()
        assert "payment_type" in s.errors

    def test_invalid_payment_method_rejected(self):
        data = {
            "payment_type": "DEPOSIT",
            "payment_method": "BITCOIN",
            "amount": "100.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert not s.is_valid()
        assert "payment_method" in s.errors


class TestConfirmPaymentSerializer:
    def test_notes_optional(self):
        s = ConfirmPaymentSerializer(data={})
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == ""

    def test_notes_with_value(self):
        s = ConfirmPaymentSerializer(data={"notes": "Verificado vía WhatsApp"})
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == "Verificado vía WhatsApp"


class TestRejectPaymentSerializer:
    def test_reason_required(self):
        s = RejectPaymentSerializer(data={})
        assert not s.is_valid()
        assert "reason" in s.errors

    def test_reason_valid(self):
        s = RejectPaymentSerializer(data={"reason": "Comprobante ilegible"})
        assert s.is_valid(), s.errors


class TestRefundSerializer:
    def test_valid_data(self):
        s = RefundSerializer(data={"amount": "150.00", "reason": "Pedido cancelado"})
        assert s.is_valid(), s.errors

    def test_zero_amount_is_invalid(self):
        s = RefundSerializer(data={"amount": "0.00", "reason": "x"})
        assert not s.is_valid()
        assert "amount" in s.errors

    def test_reason_required(self):
        s = RefundSerializer(data={"amount": "100.00"})
        assert not s.is_valid()
        assert "reason" in s.errors
