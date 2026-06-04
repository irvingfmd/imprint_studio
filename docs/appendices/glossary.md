# Glossary

## Imprint Studio

Versión: 1.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define la terminología oficial utilizada dentro de Imprint Studio.

Todos los documentos, código, APIs y modelos de datos deben utilizar estas definiciones.

---

# Customer

Usuario final que solicita servicios de impresión 3D.

Permisos:

* Crear solicitudes.
* Ver sus pedidos.
* Ver cotizaciones.
* Subir archivos.
* Gestionar direcciones.
* Subir comprobantes.

---

# Admin

Usuario encargado de operar el negocio.

Permisos:

* Ver todos los pedidos.
* Crear cotizaciones.
* Confirmar pagos.
* Gestionar producción.
* Gestionar configuración.

---

# Order

Solicitud realizada por un cliente.

Representa el ciclo completo desde la solicitud hasta la entrega.

Tabla:

```text
orders
```

---

# Request Type

Tipo de solicitud.

Valores:

```text
REFERENCE
PRINTABLE_FILE
```

---

# Reference Request

Solicitud basada en:

* Imagen
* Boceto
* Captura
* Referencia externa

Requiere revisión manual.

---

# Printable File Request

Solicitud que incluye:

* STL
* OBJ
* 3MF

Puede automatizarse en el futuro.

---

# Quote

Cotización generada por el administrador.

Contiene:

* Costos
* Tiempo
* Peso
* Margen
* Total

Tabla:

```text
quotes
```

---

# Quote Snapshot

Copia de la configuración financiera utilizada al momento de generar una cotización.

Tabla:

```text
quote_snapshots
```

---

# Deposit

Anticipo requerido para iniciar producción.

Valor por defecto:

```text
50%
```

---

# Balance

Monto restante pendiente de pago.

Normalmente:

```text
50%
```

---

# Full Payment

Pago total realizado al aprobar la cotización.

Beneficio:

```text
Descuento configurable
```

---

# Payment

Movimiento financiero asociado a un pedido.

Tabla:

```text
payments
```

---

# Refund

Devolución parcial o total de dinero al cliente.

Se registra como un movimiento financiero.

---

# Shipping Address

Dirección de entrega del cliente.

Tabla:

```text
shipping_addresses
```

---

# Shipment

Registro logístico de un envío.

Tabla:

```text
shipments
```

---

# Production History

Historial de cambios de estado de producción.

Tabla:

```text
production_history
```

---

# Order Event

Evento auditado del sistema.

Tabla:

```text
order_events
```

---

# Business Configuration

Configuración financiera y operativa del negocio.

Tabla:

```text
business_config
```

---

# Business Hours

Horarios de atención.

Tabla:

```text
business_hours
```

---

# Holiday

Día festivo que afecta producción, entregas o recogidas.

Tabla:

```text
holidays
```

---

# Payment Instructions

Datos bancarios mostrados al cliente.

Tabla:

```text
payment_instructions
```

---

# Bambu Studio

Software oficial utilizado para obtener:

* Peso real.
* Tiempo real.

Fuente oficial para cotizaciones.

---

# AI Analysis

Información generada por futuros agentes de IA.

No utilizada durante el MVP.

---

# Order Lifecycle

Ciclo completo:

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

# Objetivo

Garantizar un lenguaje común entre:

* Backend
* Frontend
* QA
* Administración
* Documentación
* IA futura

Fin del documento.
