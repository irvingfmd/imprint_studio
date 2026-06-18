"""
Tarifas eléctricas domésticas de la CFE por zona climática.

Las zonas se asignan por municipio según la temperatura máxima promedio anual:
  1   < 25 °C   1A  25–28 °C   1B  28–30 °C   1C  30–33 °C
  1D  33–36 °C  1E  36–40 °C   1F  > 40 °C

La tarifa de referencia corresponde al bloque intermedio 2025 (aproximado).
Para el costo real consulta tu recibo CFE o cfe.mx — varía según consumo mensual
y si el contrato es doméstico (tarifa 1x), doméstico alto consumo (DAC) o comercial.
"""

# Zona → descripción + tarifa de referencia MXN/kWh (bloque intermedio)
ZONE_RATES: dict[str, dict] = {
    "1": {"description": "Zona templada (< 25 °C promedio)", "rate_kwh": "1.50"},
    "1A": {"description": "Zona templada-cálida (25–28 °C promedio)", "rate_kwh": "1.50"},
    "1B": {"description": "Zona semicálida (28–30 °C promedio)", "rate_kwh": "1.45"},
    "1C": {"description": "Zona cálida media (30–33 °C promedio)", "rate_kwh": "1.40"},
    "1D": {"description": "Zona cálida (33–36 °C promedio)", "rate_kwh": "1.35"},
    "1E": {"description": "Zona muy cálida (36–40 °C promedio)", "rate_kwh": "1.25"},
    "1F": {"description": "Zona extremadamente cálida (> 40 °C promedio)", "rate_kwh": "1.15"},
}

# Primeros 2 dígitos del CP → zona CFE (basado en asignación por estado/municipio)
_PREFIX_ZONE: dict[str, str] = {
    # Ciudad de México
    "01": "1",
    "02": "1",
    "03": "1",
    "04": "1",
    "05": "1",
    "06": "1",
    "07": "1",
    "08": "1",
    "09": "1",
    "10": "1",
    "11": "1",
    "12": "1",
    "13": "1",
    "14": "1",
    "15": "1",
    "16": "1",
    # Aguascalientes
    "20": "1D",
    # Baja California Norte (Tijuana/Ensenada 1E, Mexicali/San Luis 1F)
    "21": "1F",
    "22": "1E",
    # Baja California Sur
    "23": "1D",
    # Campeche
    "24": "1E",
    # Coahuila (Saltillo más templado, norte muy caliente)
    "25": "1F",
    "26": "1E",
    "27": "1D",
    # Colima
    "28": "1D",
    # Chiapas
    "29": "1E",
    "30": "1E",
    # Chihuahua (Juárez/norte 1F, capital 1C)
    "31": "1F",
    "32": "1C",
    "33": "1C",
    # Durango
    "34": "1C",
    "35": "1C",
    # Guanajuato
    "36": "1C",
    "37": "1C",
    "38": "1C",
    # Guerrero
    "39": "1E",
    "40": "1E",
    "41": "1E",
    # Hidalgo
    "42": "1",
    "43": "1",
    # Jalisco (GDL 1C, costa 1E)
    "44": "1C",
    "45": "1C",
    "46": "1C",
    "47": "1D",
    "48": "1E",
    "49": "1D",
    # Estado de México (Toluca/poniente 1, oriente conurbado 1B)
    "50": "1",
    "51": "1",
    "52": "1",
    "53": "1",
    "54": "1",
    "55": "1B",
    "56": "1B",
    "57": "1B",
    # Michoacán
    "58": "1C",
    "59": "1C",
    "60": "1D",
    "61": "1D",
    # Morelos
    "62": "1C",
    # Nayarit
    "63": "1E",
    # Nuevo León (GDL 1D, norte/noreste 1E)
    "64": "1D",
    "65": "1D",
    "66": "1E",
    "67": "1E",
    # Oaxaca (capital 1C, Tehuantepec/Istmo 1E)
    "68": "1C",
    "69": "1D",
    "70": "1E",
    "71": "1E",
    # Puebla (capital 1B, tierra caliente 1C)
    "72": "1B",
    "73": "1B",
    "74": "1B",
    "75": "1C",
    # Querétaro
    "76": "1C",
    # Quintana Roo
    "77": "1E",
    # San Luis Potosí
    "78": "1C",
    "79": "1D",
    # Sinaloa (Los Mochis/norte 1F, Culiacán/sur 1E)
    "80": "1E",
    "81": "1F",
    "82": "1E",
    # Sonora (Hermosillo 1E, extremos 1F)
    "83": "1E",
    "84": "1F",
    "85": "1F",
    # Tabasco
    "86": "1E",
    # Tamaulipas (CD Victoria 1E, Reynosa/NL frontera 1F, Tampico 1E)
    "87": "1E",
    "88": "1F",
    "89": "1E",
    # Tlaxcala
    "90": "1B",
    # Veracruz (Xalapa/norte 1D, costa sur 1E)
    "91": "1D",
    "92": "1D",
    "93": "1D",
    "94": "1D",
    "95": "1E",
    "96": "1E",
    # Yucatán
    "97": "1E",
    # Zacatecas
    "98": "1C",
    "99": "1C",
}


def lookup_cfe(postal_code: str) -> dict | None:
    """
    Devuelve zona CFE y tarifa de referencia para un CP mexicano de 5 dígitos.
    Retorna None si el prefijo no corresponde a ninguna zona registrada.
    """
    cp = postal_code.strip().zfill(5)
    zone = _PREFIX_ZONE.get(cp[:2])
    if zone is None:
        return None
    info = ZONE_RATES[zone]
    return {
        "postal_code": cp,
        "tariff_zone": zone,
        "rate_kwh": info["rate_kwh"],
        "zone_description": info["description"],
    }
