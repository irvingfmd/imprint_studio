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
    def test_url_valida(self):
        s = PaymentProofSerializer(data={"file_url": "https://cdn.example.com/comprobante.pdf"})
        assert s.is_valid(), s.errors

    def test_url_invalida_rechazada(self):
        s = PaymentProofSerializer(data={"file_url": "no-es-una-url"})
        assert not s.is_valid()
        assert "file_url" in s.errors

    def test_sin_url_es_invalido(self):
        s = PaymentProofSerializer(data={})
        assert not s.is_valid()
        assert "file_url" in s.errors


class TestManualConfirmationSerializer:
    def test_datos_validos(self):
        data = {
            "payment_type": "DEPOSIT",
            "payment_method": "BANK_TRANSFER",
            "amount": "218.24",
        }
        s = ManualConfirmationSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_notes_opcional(self):
        data = {
            "payment_type": "FULL_PAYMENT",
            "payment_method": "CASH",
            "amount": "500.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == ""

    def test_amount_cero_es_invalido(self):
        data = {
            "payment_type": "DEPOSIT",
            "payment_method": "BANK_TRANSFER",
            "amount": "0.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert not s.is_valid()
        assert "amount" in s.errors

    def test_amount_negativo_es_invalido(self):
        data = {
            "payment_type": "DEPOSIT",
            "payment_method": "BANK_TRANSFER",
            "amount": "-100.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert not s.is_valid()
        assert "amount" in s.errors

    def test_tipo_pago_invalido_rechazado(self):
        data = {
            "payment_type": "CRYPTO",
            "payment_method": "BANK_TRANSFER",
            "amount": "100.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert not s.is_valid()
        assert "payment_type" in s.errors

    def test_metodo_pago_invalido_rechazado(self):
        data = {
            "payment_type": "DEPOSIT",
            "payment_method": "BITCOIN",
            "amount": "100.00",
        }
        s = ManualConfirmationSerializer(data=data)
        assert not s.is_valid()
        assert "payment_method" in s.errors


class TestConfirmPaymentSerializer:
    def test_notas_opcionales(self):
        s = ConfirmPaymentSerializer(data={})
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == ""

    def test_notas_con_valor(self):
        s = ConfirmPaymentSerializer(data={"notes": "Verificado vía WhatsApp"})
        assert s.is_valid(), s.errors
        assert s.validated_data["notes"] == "Verificado vía WhatsApp"


class TestRejectPaymentSerializer:
    def test_reason_requerido(self):
        s = RejectPaymentSerializer(data={})
        assert not s.is_valid()
        assert "reason" in s.errors

    def test_reason_valido(self):
        s = RejectPaymentSerializer(data={"reason": "Comprobante ilegible"})
        assert s.is_valid(), s.errors


class TestRefundSerializer:
    def test_datos_validos(self):
        s = RefundSerializer(data={"amount": "150.00", "reason": "Pedido cancelado"})
        assert s.is_valid(), s.errors

    def test_amount_cero_es_invalido(self):
        s = RefundSerializer(data={"amount": "0.00", "reason": "x"})
        assert not s.is_valid()
        assert "amount" in s.errors

    def test_reason_requerido(self):
        s = RefundSerializer(data={"amount": "100.00"})
        assert not s.is_valid()
        assert "reason" in s.errors
