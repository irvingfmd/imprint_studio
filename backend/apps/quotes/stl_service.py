"""
Análisis de archivos STL para auto-cotización.
Calcula volumen del mesh → peso estimado → tiempo de impresión estimado.
Sin dependencias externas — parseo binario directo.
"""

import struct
from decimal import ROUND_HALF_UP, Decimal

# ponytail: constantes fijas, mover a BusinessConfig si se necesita calibrar por impresora
PLA_DENSITY = Decimal("1.24")  # g/cm³
INFILL_FACTOR = Decimal("0.30")  # ~20% infill + 3 perimeters + top/bottom
PRINT_SPEED_GPH = Decimal("8.0")  # gramos por hora (FDM, 0.2mm layer, 50mm/s)


def stl_volume_mm3(data: bytes) -> float:
    """Volumen en mm³ de un STL binario (signed tetrahedra method)."""
    if len(data) < 84:
        raise ValueError("Archivo STL inválido o muy pequeño.")

    if data[:5] == b"solid" and b"\n" in data[:80]:
        raise ValueError("STL en formato ASCII no soportado. Exporta como STL binario.")

    n_tri = struct.unpack_from("<I", data, 80)[0]
    max_triangles = 2_000_000
    if n_tri > max_triangles:
        raise ValueError(f"STL demasiado grande ({n_tri:,} triángulos, máx {max_triangles:,}).")
    if len(data) < 84 + n_tri * 50:
        raise ValueError("Archivo STL corrupto (tamaño no coincide con triángulos declarados).")

    vol = 0.0
    for i in range(n_tri):
        off = 84 + i * 50 + 12
        v1x, v1y, v1z, v2x, v2y, v2z, v3x, v3y, v3z = struct.unpack_from("<9f", data, off)
        vol += v1x * (v2y * v3z - v3y * v2z) - v2x * (v1y * v3z - v3y * v1z) + v3x * (v1y * v2z - v2y * v1z)
    return abs(vol) / 6.0


def estimate_from_stl(data: bytes) -> dict:
    """
    Analiza un STL y retorna estimados de peso y tiempo de impresión.
    El peso asume PLA con ~20% infill (factor 0.30 del volumen sólido).
    El tiempo asume ~8 g/h (velocidad típica FDM).
    """
    vol_mm3 = stl_volume_mm3(data)
    vol_cm3 = Decimal(str(round(vol_mm3 / 1000.0, 4)))

    weight = (vol_cm3 * PLA_DENSITY * INFILL_FACTOR).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    weight = max(weight, Decimal("1.00"))

    print_time = (weight / PRINT_SPEED_GPH).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    print_time = max(print_time, Decimal("0.25"))

    return {
        "volume_cm3": float(vol_cm3),
        "estimated_weight_grams": weight,
        "estimated_print_time_hours": print_time,
    }
