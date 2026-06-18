"""
Tests de serializers de la app quotes.
Cubre: CreateQuoteSerializer, AcceptQuoteSerializer, RejectQuoteSerializer,
       CalculateSerializer, QuoteSerializer (salida).
Casos del plan: 28 (peso inválido), 29 (tiempo inválido).
"""

from decimal import Decimal

from apps.quotes.serializers import (
    AcceptQuoteSerializer,
    CalculateSerializer,
    CreateQuoteSerializer,
    RejectQuoteSerializer,
)


class TestCreateQuoteSerializer:
    def test_datos_validos(self):
        data = {
            "weight_grams": "250.00",
            "print_time_hours": "12.50",
            "shipping_cost": "120.00",
        }
        s = CreateQuoteSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_weight_grams_cero_es_invalido(self):
        # Caso 28: peso inválido
        data = {"weight_grams": "0.00", "print_time_hours": "5.00"}
        s = CreateQuoteSerializer(data=data)
        assert not s.is_valid()
        assert "weight_grams" in s.errors

    def test_weight_grams_negativo_es_invalido(self):
        data = {"weight_grams": "-10.00", "print_time_hours": "5.00"}
        s = CreateQuoteSerializer(data=data)
        assert not s.is_valid()
        assert "weight_grams" in s.errors

    def test_print_time_hours_cero_es_invalido(self):
        # Caso 29: tiempo inválido
        data = {"weight_grams": "100.00", "print_time_hours": "0.00"}
        s = CreateQuoteSerializer(data=data)
        assert not s.is_valid()
        assert "print_time_hours" in s.errors

    def test_shipping_cost_default_es_cero(self):
        data = {"weight_grams": "100.00", "print_time_hours": "5.00"}
        s = CreateQuoteSerializer(data=data)
        assert s.is_valid(), s.errors
        assert s.validated_data["shipping_cost"] == Decimal("0.00")

    def test_shipping_cost_negativo_es_invalido(self):
        data = {
            "weight_grams": "100.00",
            "print_time_hours": "5.00",
            "shipping_cost": "-50.00",
        }
        s = CreateQuoteSerializer(data=data)
        assert not s.is_valid()
        assert "shipping_cost" in s.errors


class TestAcceptQuoteSerializer:
    def test_deposit_es_valido(self):
        s = AcceptQuoteSerializer(data={"payment_option": "DEPOSIT"})
        assert s.is_valid(), s.errors

    def test_full_payment_es_valido(self):
        s = AcceptQuoteSerializer(data={"payment_option": "FULL_PAYMENT"})
        assert s.is_valid(), s.errors

    def test_opcion_invalida_es_rechazada(self):
        s = AcceptQuoteSerializer(data={"payment_option": "CASH"})
        assert not s.is_valid()
        assert "payment_option" in s.errors

    def test_sin_opcion_es_invalido(self):
        s = AcceptQuoteSerializer(data={})
        assert not s.is_valid()
        assert "payment_option" in s.errors


class TestRejectQuoteSerializer:
    def test_reason_opcional(self):
        s = RejectQuoteSerializer(data={})
        assert s.is_valid(), s.errors
        assert s.validated_data["reason"] == ""

    def test_reason_valido(self):
        s = RejectQuoteSerializer(data={"reason": "Precio muy alto"})
        assert s.is_valid(), s.errors
        assert s.validated_data["reason"] == "Precio muy alto"


class TestCalculateSerializer:
    def test_datos_validos_normal(self):
        data = {
            "weight_grams": "250.00",
            "print_time_hours": "12.50",
            "priority": "NORMAL",
            "shipping_cost": "120.00",
            "full_payment_selected": False,
        }
        s = CalculateSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_prioridad_urgente_valida(self):
        data = {"weight_grams": "100.00", "print_time_hours": "5.00", "priority": "URGENT"}
        s = CalculateSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_prioridad_express_valida(self):
        data = {"weight_grams": "100.00", "print_time_hours": "5.00", "priority": "EXPRESS"}
        s = CalculateSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_prioridad_invalida_rechazada(self):
        data = {"weight_grams": "100.00", "print_time_hours": "5.00", "priority": "SUPER_FAST"}
        s = CalculateSerializer(data=data)
        assert not s.is_valid()
        assert "priority" in s.errors

    def test_weight_cero_es_invalido(self):
        # Caso 28
        data = {"weight_grams": "0.00", "print_time_hours": "5.00", "priority": "NORMAL"}
        s = CalculateSerializer(data=data)
        assert not s.is_valid()
        assert "weight_grams" in s.errors

    def test_time_cero_es_invalido(self):
        # Caso 29
        data = {"weight_grams": "100.00", "print_time_hours": "0.00", "priority": "NORMAL"}
        s = CalculateSerializer(data=data)
        assert not s.is_valid()
        assert "print_time_hours" in s.errors

    def test_full_payment_default_es_false(self):
        data = {"weight_grams": "100.00", "print_time_hours": "5.00", "priority": "NORMAL"}
        s = CalculateSerializer(data=data)
        assert s.is_valid(), s.errors
        assert s.validated_data["full_payment_selected"] is False
