# Cost Calculator

## Imprint Studio

Versión: 2.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define la calculadora oficial de costos de Imprint Studio.

La calculadora se utiliza para generar cotizaciones basadas en datos reales de impresión 3D, configuración operativa del negocio y reglas financieras definidas por el administrador.

Este documento es la fuente oficial para implementar:

* `QuoteCalculatorService`
* `PricingService`
* `POST /api/v1/admin/orders/{order_id}/quote/`
* `POST /api/v1/admin/calculator/calculate/`
* Pruebas unitarias de cotización
* Futuras recomendaciones de IA

---

# Principio Fundamental

La cotización debe basarse en datos reales obtenidos del laminado.

La fuente oficial es:

```text
Bambu Studio
```

---

# Datos Oficiales de Producción

Los siguientes valores deben obtenerse desde Bambu Studio:

```text
weight_grams

print_time_hours
```

---

## weight_grams

Peso real estimado por Bambu Studio.

Unidad:

```text
gramos
```

---

## print_time_hours

Tiempo real estimado por Bambu Studio.

Unidad:

```text
horas
```

---

# Regla Principal

No se debe generar una cotización final sin:

```text
weight_grams
print_time_hours
```

---

# Variables Configurables

Las siguientes variables deben existir en:

```text
business_config
```

---

## material_cost_per_kg

Costo por kilogramo de material.

Unidad:

```text
MXN
```

---

## energy_cost_per_hour

Costo energético estimado por hora de impresión.

Unidad:

```text
MXN
```

---

## labor_cost_per_hour

Costo de mano de obra por hora de impresión.

Unidad:

```text
MXN
```

---

## post_processing_cost_per_gram

Costo de postprocesado por gramo.

Unidad:

```text
MXN
```

---

## packaging_cost

Costo fijo de empaque por pedido.

Unidad:

```text
MXN
```

---

## failure_percentage

Porcentaje destinado a cubrir riesgo operativo por fallas.

Unidad:

```text
porcentaje
```

---

## profit_margin_percentage

Margen de ganancia.

Unidad:

```text
porcentaje
```

---

## urgent_multiplier

Multiplicador para prioridad urgente.

Valor inicial recomendado:

```text
1.30
```

---

## express_multiplier

Multiplicador para prioridad express.

Valor inicial recomendado:

```text
1.50
```

---

## full_payment_discount_percentage

Descuento aplicado cuando el cliente paga el 100% al aprobar la cotización.

Valor inicial recomendado:

```text
5.00
```

---

# Valores Iniciales Recomendados

Estos valores son iniciales y deben poder modificarse desde administración.

| Variable                         | Valor |
| -------------------------------- | ----- |
| material_cost_per_kg             | 25.00 |
| energy_cost_per_hour             | 0.50  |
| labor_cost_per_hour              | 15.00 |
| post_processing_cost_per_gram    | 0.05  |
| packaging_cost                   | 2.00  |
| failure_percentage               | 10.00 |
| profit_margin_percentage         | 30.00 |
| urgent_multiplier                | 1.30  |
| express_multiplier               | 1.50  |
| full_payment_discount_percentage | 5.00  |

---

# Nota sobre Valores Iniciales

Los valores iniciales son configurables.

No deben considerarse valores definitivos del negocio.

Especialmente:

```text
material_cost_per_kg
```

debe ajustarse al costo real del filamento utilizado.

---

# Prioridades

## NORMAL

Multiplicador:

```text
1.00
```

---

## URGENT

Multiplicador:

```text
urgent_multiplier
```

Valor inicial:

```text
1.30
```

---

## EXPRESS

Multiplicador:

```text
express_multiplier
```

Valor inicial:

```text
1.50
```

---

# Fórmula Oficial

Todas las variables internas deben estar en inglés.

Los comentarios del código deben estar en español mexicano.

---

# Material Cost

```python
material_cost = (
    weight_grams / Decimal("1000")
) * material_cost_per_kg
```

---

# Energy Cost

```python
energy_cost = (
    print_time_hours
    * energy_cost_per_hour
)
```

---

# Labor Cost

```python
labor_cost = (
    print_time_hours
    * labor_cost_per_hour
)
```

---

# Post Processing Cost

```python
post_processing_cost = (
    weight_grams
    * post_processing_cost_per_gram
)
```

---

# Packaging Cost

```python
packaging_cost = packaging_cost
```

---

# Risk Cost

```python
risk_cost = (
    material_cost
    + energy_cost
) * (
    failure_percentage / Decimal("100")
)
```

---

# Base Cost

```python
base_cost = (
    material_cost
    + energy_cost
    + labor_cost
    + post_processing_cost
    + packaging_cost
    + risk_cost
)
```

---

# Priority Multiplier

```python
if priority == "NORMAL":
    priority_multiplier = Decimal("1.00")

elif priority == "URGENT":
    priority_multiplier = urgent_multiplier

elif priority == "EXPRESS":
    priority_multiplier = express_multiplier
```

---

# Priority Cost

```python
priority_cost = (
    base_cost
    * priority_multiplier
)
```

---

# Shipping Cost

El costo de envío no se calcula automáticamente.

Debe capturarse manualmente por el administrador.

```python
shipping_cost = manual_shipping_cost
```

---

# Subtotal

```python
subtotal = (
    priority_cost
    + shipping_cost
)
```

---

# Profit Amount

```python
profit_amount = (
    subtotal
    * (
        profit_margin_percentage / Decimal("100")
    )
)
```

---

# Total Before Discount

```python
total_before_discount = (
    subtotal
    + profit_amount
)
```

---

# Full Payment Discount

Solo aplica si el cliente selecciona:

```text
FULL_PAYMENT
```

---

```python
discount_amount = (
    total_before_discount
    * (
        full_payment_discount_percentage / Decimal("100")
    )
)
```

---

# Total Price

## Si el cliente paga 50/50

```python
total_price = total_before_discount
```

---

## Si el cliente paga 100%

```python
total_price = (
    total_before_discount
    - discount_amount
)
```

---

# Fórmula Completa

```python
from decimal import Decimal, ROUND_HALF_UP


def calculate_quote_price(
    weight_grams: Decimal,
    print_time_hours: Decimal,
    material_cost_per_kg: Decimal,
    energy_cost_per_hour: Decimal,
    labor_cost_per_hour: Decimal,
    post_processing_cost_per_gram: Decimal,
    packaging_cost: Decimal,
    failure_percentage: Decimal,
    profit_margin_percentage: Decimal,
    priority: str,
    urgent_multiplier: Decimal,
    express_multiplier: Decimal,
    shipping_cost: Decimal,
    full_payment_discount_percentage: Decimal,
    full_payment_selected: bool,
) -> dict:
    """
    Calcula el precio final de una cotización usando
    datos reales de Bambu Studio y configuración del negocio.
    """

    material_cost = (
        weight_grams / Decimal("1000")
    ) * material_cost_per_kg

    energy_cost = (
        print_time_hours
        * energy_cost_per_hour
    )

    labor_cost = (
        print_time_hours
        * labor_cost_per_hour
    )

    post_processing_cost = (
        weight_grams
        * post_processing_cost_per_gram
    )

    risk_cost = (
        material_cost
        + energy_cost
    ) * (
        failure_percentage / Decimal("100")
    )

    base_cost = (
        material_cost
        + energy_cost
        + labor_cost
        + post_processing_cost
        + packaging_cost
        + risk_cost
    )

    if priority == "NORMAL":
        priority_multiplier = Decimal("1.00")
    elif priority == "URGENT":
        priority_multiplier = urgent_multiplier
    elif priority == "EXPRESS":
        priority_multiplier = express_multiplier
    else:
        raise ValueError("Invalid priority")

    priority_cost = (
        base_cost
        * priority_multiplier
    )

    subtotal = (
        priority_cost
        + shipping_cost
    )

    profit_amount = (
        subtotal
        * (
            profit_margin_percentage / Decimal("100")
        )
    )

    total_before_discount = (
        subtotal
        + profit_amount
    )

    discount_amount = Decimal("0.00")

    if full_payment_selected:
        discount_amount = (
            total_before_discount
            * (
                full_payment_discount_percentage
                / Decimal("100")
            )
        )

    total_price = (
        total_before_discount
        - discount_amount
    )

    return {
        "material_cost": round_money(material_cost),
        "energy_cost": round_money(energy_cost),
        "labor_cost": round_money(labor_cost),
        "post_processing_cost": round_money(
            post_processing_cost
        ),
        "packaging_cost": round_money(packaging_cost),
        "risk_cost": round_money(risk_cost),
        "base_cost": round_money(base_cost),
        "priority_multiplier": priority_multiplier,
        "priority_cost": round_money(priority_cost),
        "shipping_cost": round_money(shipping_cost),
        "subtotal": round_money(subtotal),
        "profit_amount": round_money(profit_amount),
        "discount_amount": round_money(discount_amount),
        "total_price": round_money(total_price),
    }


def round_money(value: Decimal) -> Decimal:
    """
    Redondea importes monetarios a dos decimales.
    """

    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )
```

---

# Regla de Redondeo

Todos los importes monetarios deben redondearse a:

```text
2 decimales
```

---

## Método Recomendado

Usar:

```python
Decimal
```

No usar:

```python
float
```

---

## Redondeo

```python
ROUND_HALF_UP
```

---

# Campos Guardados en quotes

El resultado de la calculadora debe almacenarse en:

```text
quotes
```

---

## Campos

```text
weight_grams

print_time_hours

material_cost

energy_cost

labor_cost

post_processing_cost

packaging_cost

risk_cost

shipping_cost

subtotal

profit_amount

discount_amount

total_price
```

---

# Snapshot de Configuración

Cada cotización debe guardar un snapshot en:

```text
quote_snapshots
```

---

# Campos del Snapshot

```text
material_cost_per_kg

energy_cost_per_hour

labor_cost_per_hour

post_processing_cost_per_gram

packaging_cost

failure_percentage

profit_margin_percentage

urgent_multiplier

express_multiplier

full_payment_discount_percentage
```

---

# Regla de Snapshot

Cada vez que se cree una cotización:

1. Se consulta `business_config`.
2. Se calcula la cotización.
3. Se guarda el registro en `quotes`.
4. Se guarda el registro en `quote_snapshots`.
5. Se genera un evento `QUOTE_CREATED` en `order_events`.

---

# Endpoint Administrativo

## Calculate Without Saving

Este endpoint sirve para simular una cotización sin crearla.

```http
POST /api/v1/admin/calculator/calculate/
```

---

## Request

```json
{
  "weight_grams": 250.00,
  "print_time_hours": 12.50,
  "priority": "NORMAL",
  "shipping_cost": 120.00,
  "full_payment_selected": false
}
```

---

## Response

```json
{
  "material_cost": 6.25,
  "energy_cost": 6.25,
  "labor_cost": 187.50,
  "post_processing_cost": 12.50,
  "packaging_cost": 2.00,
  "risk_cost": 1.25,
  "base_cost": 215.75,
  "priority_multiplier": 1.00,
  "priority_cost": 215.75,
  "shipping_cost": 120.00,
  "subtotal": 335.75,
  "profit_amount": 100.73,
  "discount_amount": 0.00,
  "total_price": 436.48
}
```

---

# Endpoint para Crear Cotización

```http
POST /api/v1/admin/orders/{order_id}/quote/
```

---

## Request

```json
{
  "weight_grams": 250.00,
  "print_time_hours": 12.50,
  "shipping_cost": 120.00
}
```

---

## Regla

Este endpoint sí debe guardar:

* `quotes`
* `quote_snapshots`
* `order_events`

---

# Ejemplo de Cálculo

## Datos

```text
weight_grams = 250.00

print_time_hours = 12.50

material_cost_per_kg = 25.00

energy_cost_per_hour = 0.50

labor_cost_per_hour = 15.00

post_processing_cost_per_gram = 0.05

packaging_cost = 2.00

failure_percentage = 10.00

profit_margin_percentage = 30.00

priority = NORMAL

shipping_cost = 120.00

full_payment_selected = false
```

---

## Resultado

```text
material_cost = 6.25

energy_cost = 6.25

labor_cost = 187.50

post_processing_cost = 12.50

packaging_cost = 2.00

risk_cost = 1.25

base_cost = 215.75

priority_multiplier = 1.00

priority_cost = 215.75

subtotal = 335.75

profit_amount = 100.73

discount_amount = 0.00

total_price = 436.48
```

---

# Ejemplo con Pago Completo

## Datos

```text
total_before_discount = 436.48

full_payment_discount_percentage = 5.00
```

---

## Resultado

```text
discount_amount = 21.82

total_price = 414.66
```

---

# Validaciones

## weight_grams

Debe ser mayor que:

```text
0
```

---

## print_time_hours

Debe ser mayor que:

```text
0
```

---

## shipping_cost

Debe ser mayor o igual a:

```text
0
```

---

## percentages

Deben ser mayores o iguales a:

```text
0
```

---

## priority

Debe ser uno de:

```text
NORMAL
URGENT
EXPRESS
```

---

# Errores Esperados

## Peso Inválido

```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "weight_grams": [
      "Weight must be greater than zero."
    ]
  }
}
```

---

## Tiempo Inválido

```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "print_time_hours": [
      "Print time must be greater than zero."
    ]
  }
}
```

---

# Pruebas Unitarias Requeridas

Se deben probar al menos:

* Cálculo normal.
* Cálculo urgente.
* Cálculo express.
* Cálculo con envío.
* Cálculo sin envío.
* Cálculo con pago completo.
* Cálculo con peso inválido.
* Cálculo con tiempo inválido.
* Redondeo correcto.
* Uso correcto de `Decimal`.

---

# Reglas para IA Futura

La IA podrá sugerir valores.

La IA no podrá modificar la fórmula oficial.

La IA no podrá aprobar precios.

La IA no podrá cambiar configuración financiera.

---

# Objetivo

Garantizar que toda cotización de Imprint Studio sea:

* Reproducible.
* Auditable.
* Explicable.
* Consistente.
* Basada en datos reales.
* Independiente de IA durante el MVP.

---

# Estado del Documento

Versión: 2.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* QuoteCalculatorService
* PricingService
* Tests
* Admin Calculator
* Quote Creation Endpoint
* Futuras integraciones de IA

Fin del documento.
