"""
Tests de serializers de la app shipping.
Cubre: ShippingAddressCreateSerializer, CreateShipmentSerializer.
"""
from decimal import Decimal

from apps.shipping.serializers import CreateShipmentSerializer, ShippingAddressCreateSerializer


class TestShippingAddressCreateSerializer:
    def _valid_data(self) -> dict:
        return {
            "address_name": "Casa",
            "street": "Av. Central",
            "external_number": "100",
            "neighborhood": "Centro",
            "postal_code": "29000",
            "city": "Tuxtla Gutiérrez",
            "state": "Chiapas",
        }

    def test_datos_validos(self):
        s = ShippingAddressCreateSerializer(data=self._valid_data())
        assert s.is_valid(), s.errors

    def test_address_name_requerido(self):
        data = self._valid_data()
        del data["address_name"]
        s = ShippingAddressCreateSerializer(data=data)
        assert not s.is_valid()
        assert "address_name" in s.errors

    def test_street_requerido(self):
        data = self._valid_data()
        del data["street"]
        s = ShippingAddressCreateSerializer(data=data)
        assert not s.is_valid()
        assert "street" in s.errors

    def test_external_number_requerido(self):
        data = self._valid_data()
        del data["external_number"]
        s = ShippingAddressCreateSerializer(data=data)
        assert not s.is_valid()
        assert "external_number" in s.errors

    def test_campos_opcionales_tienen_default(self):
        s = ShippingAddressCreateSerializer(data=self._valid_data())
        s.is_valid()
        assert s.validated_data["internal_number"] == ""
        assert s.validated_data["references"] == ""
        assert s.validated_data["country"] == "Mexico"
        assert s.validated_data["is_default"] is False

    def test_is_default_opcional(self):
        data = self._valid_data()
        data["is_default"] = True
        s = ShippingAddressCreateSerializer(data=data)
        assert s.is_valid(), s.errors
        assert s.validated_data["is_default"] is True


class TestCreateShipmentSerializer:
    def test_todos_los_campos_son_opcionales(self):
        s = CreateShipmentSerializer(data={})
        assert s.is_valid(), s.errors

    def test_shipping_cost_no_puede_ser_negativo(self):
        s = CreateShipmentSerializer(data={"shipping_cost": "-1.00"})
        assert not s.is_valid()
        assert "shipping_cost" in s.errors

    def test_shipping_cost_default_es_cero(self):
        s = CreateShipmentSerializer(data={})
        s.is_valid()
        assert s.validated_data["shipping_cost"] == Decimal("0.00")

    def test_datos_completos_validos(self):
        s = CreateShipmentSerializer(data={
            "carrier_name": "DHL",
            "tracking_number": "1234567890",
            "shipping_cost": "50.00",
            "shipping_notes": "Frágil",
        })
        assert s.is_valid(), s.errors
        assert s.validated_data["shipping_cost"] == Decimal("50.00")
