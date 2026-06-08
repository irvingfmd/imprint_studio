# Status Flow

## Imprint Studio

Versión: 2.0

Estado: Aprobado para implementación

---

# Historial de Cambios

| Versión | Cambio                                                                 |
| ------- | ---------------------------------------------------------------------- |
| 1.0     | Versión inicial                                                        |
| 2.0     | Se agrega estado APPROVED. Se unifica grafo de transiciones completo.  |

---

# Propósito

Define las transiciones válidas e inválidas de los pedidos.

Este documento es la referencia oficial y única para:

```text
OrderStatusTransitionService
```

En caso de conflicto con otro documento, este prevalece.

---

# Flujo Principal

```text
RECEIVED
↓
PENDING_ANALYSIS
↓
QUOTED
↓
APPROVED
↓
PENDING_DEPOSIT
↓
DEPOSIT_PAID
↓
PRINTING
↓
POST_PROCESSING
↓
READY
↓
PENDING_BALANCE
↓
FULLY_PAID
↓
DELIVERED
```

---

# Estados

## RECEIVED

Solicitud por referencia recibida.

Aplica cuando:

```text
request_type = REFERENCE
```

---

## PENDING_ANALYSIS

Solicitud con STL/OBJ/3MF pendiente de revisión técnica.

Aplica cuando:

```text
request_type = PRINTABLE_FILE
```

---

## QUOTED

Cotización generada por el administrador.

Esperando respuesta del cliente.

---

## APPROVED

Cotización aceptada por el cliente.

El cliente selecciona modalidad de pago:

```text
DEPOSIT     → continúa a PENDING_DEPOSIT
FULL_PAYMENT → continúa a FULLY_PAID
```

Este estado es obligatorio antes de cualquier movimiento financiero.

---

## PENDING_DEPOSIT

Esperando confirmación del anticipo (50%).

Plazo máximo configurable desde:

```text
business_config.deposit_deadline_hours
```

Valor inicial:

```text
72 horas
```

---

## DEPOSIT_PAID

Anticipo confirmado por el administrador.

Producción autorizada.

---

## PRINTING

Producción iniciada.

---

## POST_PROCESSING

Postprocesado en curso.

---

## READY

Pedido terminado.

Lista para entrega o recogida.

---

## PENDING_BALANCE

Esperando pago del saldo restante (50%).

Plazo máximo configurable desde:

```text
business_config.balance_deadline_days
```

Valor inicial:

```text
7 días
```

---

## FULLY_PAID

Pago completado en su totalidad.

---

## DELIVERED

Pedido entregado al cliente.

---

## CANCELLED

Pedido cancelado.

---

# Transiciones Válidas

## RECEIVED

Puede cambiar a:

```text
QUOTED
CANCELLED
```

---

## PENDING_ANALYSIS

Puede cambiar a:

```text
QUOTED
CANCELLED
```

---

## QUOTED

Puede cambiar a:

```text
APPROVED
CANCELLED
```

---

## APPROVED

Puede cambiar a:

```text
PENDING_DEPOSIT   ← cliente seleccionó DEPOSIT
FULLY_PAID        ← cliente seleccionó FULL_PAYMENT
CANCELLED
```

---

## PENDING_DEPOSIT

Puede cambiar a:

```text
DEPOSIT_PAID
CANCELLED
```

Cancelación automática si vence el plazo:

```text
deposit_deadline_hours
```

---

## DEPOSIT_PAID

Puede cambiar a:

```text
PRINTING
```

---

## PRINTING

Puede cambiar a:

```text
POST_PROCESSING
```

---

## POST_PROCESSING

Puede cambiar a:

```text
READY
```

---

## READY

Puede cambiar a:

```text
PENDING_BALANCE   ← modalidad anticipo/saldo
FULLY_PAID        ← pago en efectivo contra entrega
DELIVERED         ← solo si ya está FULLY_PAID (ver regla especial)
```

---

## PENDING_BALANCE

Puede cambiar a:

```text
FULLY_PAID
```

---

## FULLY_PAID

Puede cambiar a:

```text
DELIVERED
```

---

# Reglas Especiales

## Flujo con Anticipo (50/50)

```text
APPROVED
↓
PENDING_DEPOSIT
↓
DEPOSIT_PAID
↓
PRINTING
↓
POST_PROCESSING
↓
READY
↓
PENDING_BALANCE
↓
FULLY_PAID
↓
DELIVERED
```

---

## Flujo con Pago Completo (100%)

```text
APPROVED
↓
FULLY_PAID
↓
PRINTING
↓
POST_PROCESSING
↓
READY
↓
DELIVERED
```

Nota: en este flujo READY transiciona directamente a DELIVERED
porque el pedido ya está liquidado.

---

## Entrega Local en Efectivo

El cliente paga en efectivo al recoger.

Flujo correcto:

```text
READY
↓
FULLY_PAID
↓
DELIVERED
```

Flujo incorrecto — no permitido:

```text
READY
↓
DELIVERED   ← inválido si hay saldo pendiente
```

Regla: nunca marcar como DELIVERED si payment_status no es FULLY_PAID.

---

# Matriz Completa de Transiciones

| Estado Origen    | Estados Destino Válidos                          |
| ---------------- | ------------------------------------------------- |
| RECEIVED         | QUOTED, CANCELLED                                 |
| PENDING_ANALYSIS | QUOTED, CANCELLED                                 |
| QUOTED           | APPROVED, CANCELLED                               |
| APPROVED         | PENDING_DEPOSIT, FULLY_PAID, CANCELLED            |
| PENDING_DEPOSIT  | DEPOSIT_PAID, CANCELLED                           |
| DEPOSIT_PAID     | PRINTING                                          |
| PRINTING         | POST_PROCESSING                                   |
| POST_PROCESSING  | READY                                             |
| READY            | PENDING_BALANCE, FULLY_PAID, DELIVERED*           |
| PENDING_BALANCE  | FULLY_PAID                                        |
| FULLY_PAID       | DELIVERED                                         |
| DELIVERED        | — (estado final)                                  |
| CANCELLED        | — (estado final)                                  |

*READY → DELIVERED solo es válido si payment_status = FULLY_PAID.

---

# Transiciones Inválidas — Ejemplos

```text
RECEIVED         → PRINTING
QUOTED           → DELIVERED
QUOTED           → PENDING_DEPOSIT    ← debe pasar por APPROVED
PENDING_DEPOSIT  → READY
PRINTING         → FULLY_PAID
DEPOSIT_PAID     → DELIVERED
DELIVERED        → PRINTING
CANCELLED        → cualquier estado
```

---

# Cancelaciones

Permitidas desde:

```text
RECEIVED
PENDING_ANALYSIS
QUOTED
APPROVED
PENDING_DEPOSIT
```

No permitidas desde:

```text
DEPOSIT_PAID
PRINTING
POST_PROCESSING
READY
PENDING_BALANCE
FULLY_PAID
DELIVERED
```

Nota: las cancelaciones desde DEPOSIT_PAID en adelante requieren
evaluación manual del administrador y gestión de reembolso según
la política documentada en 06-payments-and-refunds.md.

---

# Cancelación Automática por Vencimiento de Anticipo

Condición:

```text
status = PENDING_DEPOSIT
AND tiempo transcurrido > deposit_deadline_hours
```

Acción automática:

```text
→ CANCELLED
```

Evento generado:

```text
ORDER_CANCELLED
```

Reembolso aplicable:

```text
100% (no inició producción)
```

---

# Estados Finales

Estados que no permiten más cambios:

```text
DELIVERED
CANCELLED
```

---

# Estado Inicial por Tipo de Solicitud

| request_type   | Estado Inicial   |
| -------------- | ---------------- |
| REFERENCE      | RECEIVED         |
| PRINTABLE_FILE | PENDING_ANALYSIS |

---

# Objetivo

Garantizar integridad del flujo de negocio, evitar estados inconsistentes
y proporcionar una fuente única de verdad para OrderStatusTransitionService.

---

# Estado del Documento

Versión: 2.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* OrderStatusTransitionService
* Django Models
* Tests de transición
* QA
* Frontend (lógica de UI condicional)

Fin del documento.