# Status Flow

## Imprint Studio

Versión: 1.0

Estado: Aprobado para implementación

---

# Propósito

Define las transiciones válidas e inválidas de los pedidos.

Este documento es la referencia oficial para:

```text
OrderStatusTransitionService
```

---

# Flujo Principal

```text
RECEIVED
↓
PENDING_ANALYSIS
↓
QUOTED
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

---

## PENDING_ANALYSIS

Solicitud con STL/OBJ/3MF pendiente de revisión.

---

## QUOTED

Cotización generada.

---

## PENDING_DEPOSIT

Esperando anticipo.

---

## DEPOSIT_PAID

Anticipo confirmado.

---

## PRINTING

Producción iniciada.

---

## POST_PROCESSING

Postprocesado.

---

## READY

Pedido terminado.

---

## PENDING_BALANCE

Esperando pago restante.

---

## FULLY_PAID

Pago completado.

---

## DELIVERED

Pedido entregado.

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
PENDING_DEPOSIT
FULLY_PAID
CANCELLED
```

---

## PENDING_DEPOSIT

Puede cambiar a:

```text
DEPOSIT_PAID
CANCELLED
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
PENDING_BALANCE
FULLY_PAID
DELIVERED
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

## Pago Completo

Si el cliente paga 100%:

```text
QUOTED
↓
FULLY_PAID
↓
PRINTING
```

---

## Entrega Local en Efectivo

Puede ocurrir:

```text
READY
↓
DELIVERED
↓
FULLY_PAID
```

No permitido.

Debe ser:

```text
READY
↓
FULLY_PAID
↓
DELIVERED
```

---

# Transiciones Inválidas

Ejemplos:

```text
RECEIVED → PRINTING

QUOTED → DELIVERED

PENDING_DEPOSIT → READY

PRINTING → FULLY_PAID

DELIVERED → PRINTING
```

---

# Cancelaciones

Permitidas desde:

```text
RECEIVED
PENDING_ANALYSIS
QUOTED
PENDING_DEPOSIT
DEPOSIT_PAID
```

Según reglas de negocio.

---

# Estados Finales

Estados que no permiten más cambios:

```text
DELIVERED
CANCELLED
```

---

# Objetivo

Garantizar integridad del flujo de negocio y evitar estados inconsistentes.

Fin del documento.
