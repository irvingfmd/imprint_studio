# Initial Configuration

## Imprint Studio

Versión: 1.0

Estado: Aprobado para implementación

---

# Propósito

Define los valores iniciales que deben cargarse antes de utilizar el sistema.

---

# Business Configuration

## Costos

| Variable                      | Valor |
| ----------------------------- | ----- |
| material_cost_per_kg          | 25.00 |
| energy_cost_per_hour          | 0.50  |
| labor_cost_per_hour           | 15.00 |
| post_processing_cost_per_gram | 0.05  |
| packaging_cost                | 2.00  |

---

## Riesgo

| Variable           | Valor |
| ------------------ | ----- |
| failure_percentage | 10.00 |

---

## Ganancia

| Variable                 | Valor |
| ------------------------ | ----- |
| profit_margin_percentage | 30.00 |

---

## Prioridades

| Variable           | Valor |
| ------------------ | ----- |
| urgent_multiplier  | 1.30  |
| express_multiplier | 1.50  |

---

## Descuentos

| Variable                         | Valor |
| -------------------------------- | ----- |
| full_payment_discount_percentage | 5.00  |

---

## Tiempos

| Variable               | Valor |
| ---------------------- | ----- |
| deposit_deadline_hours | 72    |
| balance_deadline_days  | 7     |

---

# Payment Instructions

Valores de ejemplo.

Deben sustituirse antes de producción.

```text
Banco: BBVA

Titular: Imprint Studio

Cuenta: PENDIENTE

CLABE: PENDIENTE

Tarjeta: PENDIENTE

Notas:
Enviar comprobante al finalizar la transferencia.
```

---

# Business Hours

## Lunes

```text
09:00 - 18:00
```

---

## Martes

```text
09:00 - 18:00
```

---

## Miércoles

```text
09:00 - 18:00
```

---

## Jueves

```text
09:00 - 18:00
```

---

## Viernes

```text
09:00 - 18:00
```

---

## Sábado

```text
09:00 - 14:00
```

---

## Domingo

```text
CERRADO
```

---

# Holidays

Ejemplos iniciales:

```text
01 Enero

05 Febrero

21 Marzo

01 Mayo

16 Septiembre

20 Noviembre

25 Diciembre
```

---

# Usuario Administrador Inicial

```text
Role:
ADMIN
```

---

Datos reales definidos durante despliegue.

---

# Configuración Técnica

## Timezone

```text
America/Mexico_City
```

---

## Currency

```text
MXN
```

---

## Phone Format

```text
E.164
```

Ejemplo:

```text
+5219611234567
```

---

# Checklist Inicial

Antes de abrir el sistema:

* Business Config cargado.
* Payment Instructions cargadas.
* Business Hours cargados.
* Holidays cargados.
* Usuario administrador creado.
* Cloudinary configurado.
* PostgreSQL configurado.
* JWT configurado.

---

# Objetivo

Permitir que una instalación nueva de Imprint Studio quede operativa en menos de 30 minutos.

Fin del documento.
