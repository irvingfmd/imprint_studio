# Database Design

## Imprint Studio

Versión: 2.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define el diseño oficial de base de datos para Imprint Studio.

Este documento es la fuente de verdad para:

* Django Models
* Migraciones
* PostgreSQL
* Django Admin
* Django REST Framework
* Servicios de negocio
* Automatizaciones
* Futuras integraciones de IA

Toda implementación deberá respetar las estructuras aquí definidas.

---

# Objetivos del Diseño

La base de datos debe ser:

* Consistente
* Escalable
* Mantenible
* Auditable
* Segura
* Compatible con PostgreSQL
* Compatible con Django ORM
* Preparada para futuras capacidades de IA

---

# Motor de Base de Datos

## Desarrollo

```text
SQLite
```

---

## Producción

```text
PostgreSQL
```

Versión recomendada:

```text
PostgreSQL 16+
```

---

# Convenciones Generales

## Idioma

Todo el esquema utiliza inglés.

---

## Formato de nombres

Todo utiliza:

```text
snake_case
```

---

## Ejemplos

Correcto:

```text
shipping_addresses
payment_instructions
created_at
```

Incorrecto:

```text
DireccionesEnvio
shippingAddresses
fechaCreacion
```

---

# Claves Primarias

Todas las tablas utilizan:

```text
UUID
```

---

## Django

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

---

# Auditoría

Todas las entidades principales incluyen:

```text
created_at
updated_at
```

---

## Tipo

```text
TIMESTAMP WITH TIME ZONE
```

---

# Zona Horaria Oficial

```text
America/Mexico_City
```

---

# Moneda Oficial

```text
MXN
```

---

# Enumeraciones Oficiales

Todas las enumeraciones deben implementarse utilizando:

```python
models.TextChoices
```

---

# UserRole

```python
class UserRole(models.TextChoices):
    CUSTOMER = "CUSTOMER", "Customer"
    ADMIN = "ADMIN", "Admin"
```

---

# RequestType

```python
class RequestType(models.TextChoices):
    REFERENCE = "REFERENCE", "Reference"
    PRINTABLE_FILE = "PRINTABLE_FILE", "Printable File"
```

---

# OrderPriority

```python
class OrderPriority(models.TextChoices):
    NORMAL = "NORMAL", "Normal"
    URGENT = "URGENT", "Urgent"
    EXPRESS = "EXPRESS", "Express"
```

---

# OrderStatus

```python
class OrderStatus(models.TextChoices):

    RECEIVED = "RECEIVED", "Received"

    PENDING_ANALYSIS = (
        "PENDING_ANALYSIS",
        "Pending Analysis"
    )

    QUOTED = "QUOTED", "Quoted"

    APPROVED = "APPROVED", "Approved"

    PENDING_DEPOSIT = (
        "PENDING_DEPOSIT",
        "Pending Deposit"
    )

    DEPOSIT_PAID = (
        "DEPOSIT_PAID",
        "Deposit Paid"
    )

    PRINTING = "PRINTING", "Printing"

    POST_PROCESSING = (
        "POST_PROCESSING",
        "Post Processing"
    )

    READY = "READY", "Ready"

    PENDING_BALANCE = (
        "PENDING_BALANCE",
        "Pending Balance"
    )

    FULLY_PAID = (
        "FULLY_PAID",
        "Fully Paid"
    )

    DELIVERED = "DELIVERED", "Delivered"

    CANCELLED = "CANCELLED", "Cancelled"
```

---

# PaymentType

```python
class PaymentType(models.TextChoices):
    DEPOSIT = "DEPOSIT", "Deposit"
    BALANCE = "BALANCE", "Balance"
    FULL_PAYMENT = "FULL_PAYMENT", "Full Payment"
    REFUND = "REFUND", "Refund"
```

---

# PaymentMethod

```python
class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = (
        "BANK_TRANSFER",
        "Bank Transfer"
    )

    CASH = "CASH", "Cash"
```

---

# PaymentStatus

```python
class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    REJECTED = "REJECTED", "Rejected"
```

---

# QuoteStatus

```python
class QuoteStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    EXPIRED = "EXPIRED", "Expired"
```

---

# DeliveryMethod

```python
class DeliveryMethod(models.TextChoices):
    PICKUP = "PICKUP", "Pickup"
    SHIPPING = "SHIPPING", "Shipping"
```

---

# Reglas de Transición de Estados

Los cambios de estado no deben realizarse directamente desde los views.

Toda transición debe pasar por:

```python
OrderStatusTransitionService
```

---

# Transiciones Permitidas

```text
RECEIVED
↓
QUOTED

PENDING_ANALYSIS
↓
QUOTED

QUOTED
↓
APPROVED

APPROVED
↓
PENDING_DEPOSIT

APPROVED
↓
FULLY_PAID

PENDING_DEPOSIT
↓
DEPOSIT_PAID

DEPOSIT_PAID
↓
PRINTING

PRINTING
↓
POST_PROCESSING

POST_PROCESSING
↓
READY

READY
↓
PENDING_BALANCE

READY
↓
FULLY_PAID

PENDING_BALANCE
↓
FULLY_PAID

FULLY_PAID
↓
DELIVERED
```

---

# Cancelación

Puede ocurrir desde:

```text
RECEIVED
PENDING_ANALYSIS
QUOTED
APPROVED
PENDING_DEPOSIT
```

---

Estado destino:

```text
CANCELLED
```

---

# Soft Delete

Las siguientes tablas no deben eliminarse físicamente:

```text
users
orders
quotes
payments
```

---

## Campos

```text
is_deleted
deleted_at
```

---

## Tipo

```text
BOOLEAN
TIMESTAMP NULL
```

---

# Relación General

```text
users
│
├── shipping_addresses
│
└── orders
     │
     ├── request_files
     │
     ├── quotes
     │     │
     │     └── quote_snapshots
     │
     ├── payments
     │
     ├── production_history
     │
     ├── order_events
     │
     └── shipments
```

---

# Tabla: users

## Propósito

Almacena clientes y administradores.

---

## Campos

| Campo      | Tipo         | Nullable |
| ---------- | ------------ | -------- |
| id         | UUID         | No       |
| phone      | VARCHAR(20)  | No       |
| email      | VARCHAR(255) | Sí       |
| first_name | VARCHAR(100) | No       |
| last_name  | VARCHAR(100) | Sí       |
| role       | VARCHAR(20)  | No       |
| is_active  | BOOLEAN      | No       |
| last_login | TIMESTAMP    | Sí       |
| is_deleted | BOOLEAN      | No       |
| deleted_at | TIMESTAMP    | Sí       |
| created_at | TIMESTAMP    | No       |
| updated_at | TIMESTAMP    | No       |

---

## Restricciones

### phone

Formato obligatorio:

```text
E.164
```

Ejemplo:

```text
+5219611234567
```

---

## role

Valores permitidos:

```text
CUSTOMER
ADMIN
```

---

## Índices

```text
phone
email
role
is_active
```

---

## Índices Únicos

```text
phone
email
```

---

# Tabla: shipping_addresses

## Propósito

Almacena direcciones de envío reutilizables.

---

## Justificación

No almacenar direcciones directamente en orders.

Ventajas:

* Historial
* Escalabilidad
* Reutilización
* Normalización
* Menos columnas nulas

---

## Campos

| Campo           | Tipo         | Nullable |
| --------------- | ------------ | -------- |
| id              | UUID         | No       |
| user_id         | UUID         | No       |
| address_name    | VARCHAR(100) | No       |
| street          | VARCHAR(255) | No       |
| external_number | VARCHAR(50)  | No       |
| internal_number | VARCHAR(50)  | Sí       |
| neighborhood    | VARCHAR(255) | No       |
| postal_code     | VARCHAR(20)  | No       |
| city            | VARCHAR(100) | No       |
| state           | VARCHAR(100) | No       |
| country         | VARCHAR(100) | No       |
| references      | TEXT         | Sí       |
| is_default      | BOOLEAN      | No       |
| created_at      | TIMESTAMP    | No       |
| updated_at      | TIMESTAMP    | No       |

---

## Relaciones

```text
shipping_addresses.user_id
→ users.id
```

---

## Índices

```text
user_id
postal_code
city
state
```

---

## Regla de Negocio

Un usuario puede tener múltiples direcciones.

---

## Regla de Negocio

Solo una dirección puede tener:

```text
is_default = true
```

por usuario.

---

# Tabla: orders

## Propósito

Representa una solicitud de impresión realizada por un cliente.

Es la entidad principal del sistema y concentra el flujo completo desde la solicitud inicial hasta la entrega final.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| customer_id | UUID | No |
| shipping_address_id | UUID | Sí |
| request_type | VARCHAR(30) | No |
| title | VARCHAR(255) | No |
| description | TEXT | No |
| color | VARCHAR(100) | Sí |
| quantity | INTEGER | No |
| dimensions_notes | TEXT | Sí |
| priority | VARCHAR(20) | No |
| status | VARCHAR(50) | No |
| payment_stage | VARCHAR(50) | Sí |
| delivery_method | VARCHAR(20) | No |
| estimated_delivery_date | DATE | Sí |
| approved_at | TIMESTAMP | Sí |
| ready_at | TIMESTAMP | Sí |
| delivered_at | TIMESTAMP | Sí |
| cancelled_at | TIMESTAMP | Sí |
| cancellation_reason | TEXT | Sí |
| ai_analysis | JSONB | Sí |
| ai_notes | TEXT | Sí |
| ai_confidence | DECIMAL(5,2) | Sí |
| ai_category | VARCHAR(100) | Sí |
| is_deleted | BOOLEAN | No |
| deleted_at | TIMESTAMP | Sí |
| created_at | TIMESTAMP | No |
| updated_at | TIMESTAMP | No |

---

## Relaciones

```text
customer_id
→ users.id
```

```text
shipping_address_id
→ shipping_addresses.id
```

---

## Request Type

Valores permitidos:

```text
REFERENCE
PRINTABLE_FILE
```

---

## Priority

Valores permitidos:

```text
NORMAL
URGENT
EXPRESS
```

---

## Delivery Method

Valores permitidos:

```text
PICKUP
SHIPPING
```

---

## Status

Valores permitidos:

```text
RECEIVED

PENDING_ANALYSIS

QUOTED

APPROVED

PENDING_DEPOSIT

DEPOSIT_PAID

PRINTING

POST_PROCESSING

READY

PENDING_BALANCE

FULLY_PAID

DELIVERED

CANCELLED
```

---

## Payment Stage

Valores permitidos:

```text
NO_PAYMENT

DEPOSIT_PENDING

DEPOSIT_PAID

BALANCE_PENDING

FULLY_PAID

REFUNDED
```

---

## Índices

```text
customer_id
status
priority
request_type
delivery_method
created_at
updated_at
```

---

## Regla de Negocio

Si:

```text
delivery_method = SHIPPING
```

entonces:

```text
shipping_address_id
```

es obligatorio.

---

## Regla de Negocio

Si:

```text
request_type = REFERENCE
```

el estado inicial será:

```text
RECEIVED
```

---

## Regla de Negocio

Si:

```text
request_type = PRINTABLE_FILE
```

el estado inicial será:

```text
PENDING_ANALYSIS
```

---

## Regla de Negocio

Los campos:

```text
ai_analysis
ai_notes
ai_confidence
ai_category
```

deben permanecer vacíos durante el MVP.

---

# Tabla: request_files

## Propósito

Almacenar archivos relacionados con una solicitud.

Puede contener:

- Imágenes de referencia.
- STL.
- OBJ.
- 3MF.
- Comprobantes de pago.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| order_id | UUID | No |
| file_type | VARCHAR(30) | No |
| file_url | TEXT | No |
| original_filename | VARCHAR(255) | No |
| mime_type | VARCHAR(100) | No |
| file_size_bytes | BIGINT | No |
| uploaded_by | UUID | No |
| uploaded_at | TIMESTAMP | No |

---

## Relaciones

```text
order_id
→ orders.id
```

```text
uploaded_by
→ users.id
```

---

## File Types

```text
IMAGE

STL

OBJ

THREE_MF

PAYMENT_PROOF
```

---

## Índices

```text
order_id
file_type
uploaded_at
```

---

## Regla de Negocio

Un pedido puede tener múltiples archivos.

---

## Regla de Negocio

No existe límite técnico de archivos.

El límite operativo deberá definirse mediante configuración.

---

## Regla de Negocio

Todos los archivos deben almacenarse fuera del servidor:

Opciones soportadas:

```text
Cloudinary

Supabase Storage
```

---

# Tabla: quotes

## Propósito

Almacena las cotizaciones oficiales generadas por el administrador.

Los datos utilizados deben provenir del laminado realizado en Bambu Studio.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| order_id | UUID | No |
| weight_grams | DECIMAL(10,2) | No |
| print_time_hours | DECIMAL(10,2) | No |
| material_cost | DECIMAL(10,2) | No |
| energy_cost | DECIMAL(10,2) | No |
| labor_cost | DECIMAL(10,2) | No |
| post_processing_cost | DECIMAL(10,2) | No |
| packaging_cost | DECIMAL(10,2) | No |
| risk_cost | DECIMAL(10,2) | No |
| shipping_cost | DECIMAL(10,2) | No |
| subtotal | DECIMAL(10,2) | No |
| profit_amount | DECIMAL(10,2) | No |
| discount_amount | DECIMAL(10,2) | No |
| total_price | DECIMAL(10,2) | No |
| quote_status | VARCHAR(20) | No |
| accepted_at | TIMESTAMP | Sí |
| rejected_at | TIMESTAMP | Sí |
| expires_at | TIMESTAMP | Sí |
| created_by | UUID | No |
| created_at | TIMESTAMP | No |
| updated_at | TIMESTAMP | No |

---

## Relaciones

```text
order_id
→ orders.id
```

```text
created_by
→ users.id
```

---

## Quote Status

```text
PENDING

ACCEPTED

REJECTED

EXPIRED
```

---

## Índices

```text
order_id
quote_status
created_at
expires_at
```

---

## Regla de Negocio

Un pedido puede tener múltiples cotizaciones históricas.

---

## Regla de Negocio

Solo una cotización puede estar activa al mismo tiempo.

---

## Regla de Negocio

La cotización aceptada se convierte en la referencia financiera oficial del pedido.

---

## Regla de Negocio

Todos los montos monetarios utilizan:

```text
DECIMAL(10,2)
```

Nunca:

```text
FLOAT
DOUBLE
REAL
```

---

# Tabla: quote_snapshots

## Propósito

Almacenar una copia exacta de la configuración utilizada para generar una cotización.

Permite reconstruir una cotización histórica incluso si la configuración global del negocio cambia posteriormente.

---

## Relación

```text
quotes
│
└── quote_snapshots
```

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| quote_id | UUID | No |
| material_cost_per_kg | DECIMAL(10,2) | No |
| energy_cost_per_hour | DECIMAL(10,2) | No |
| labor_cost_per_hour | DECIMAL(10,2) | No |
| post_processing_cost_per_gram | DECIMAL(10,2) | No |
| packaging_cost | DECIMAL(10,2) | No |
| failure_percentage | DECIMAL(5,2) | No |
| profit_margin_percentage | DECIMAL(5,2) | No |
| urgent_multiplier | DECIMAL(5,2) | No |
| express_multiplier | DECIMAL(5,2) | No |
| full_payment_discount_percentage | DECIMAL(5,2) | No |
| created_at | TIMESTAMP | No |

---

## Relaciones

```text
quote_id
→ quotes.id
```

---

## Índices

```text
quote_id
```

---

## Regla de Negocio

Cada vez que se genere una cotización se deberá crear automáticamente un snapshot de la configuración vigente.

---

## Regla de Negocio

Los snapshots nunca deben modificarse.

---

## Regla de Negocio

Los snapshots nunca deben eliminarse.

---

## Beneficios

- Auditoría financiera.
- Historial de costos.
- Reportes históricos.
- Métricas.
- Entrenamiento futuro de IA.

---

# Tabla: payments

## Propósito

Registrar movimientos financieros asociados a un pedido.

Incluye:

- Anticipos.
- Pagos finales.
- Pagos completos.
- Reembolsos.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| order_id | UUID | No |
| amount | DECIMAL(10,2) | No |
| payment_type | VARCHAR(30) | No |
| payment_method | VARCHAR(30) | No |
| payment_status | VARCHAR(30) | No |
| proof_file_url | TEXT | Sí |
| manual_confirmation | BOOLEAN | No |
| confirmed_by | UUID | Sí |
| confirmed_at | TIMESTAMP | Sí |
| notes | TEXT | Sí |
| created_at | TIMESTAMP | No |

---

## Relaciones

```text
order_id
→ orders.id
```

```text
confirmed_by
→ users.id
```

---

## Payment Type

```text
DEPOSIT

BALANCE

FULL_PAYMENT

REFUND
```

---

## Payment Method

```text
BANK_TRANSFER

CASH
```

---

## Payment Status

```text
PENDING

CONFIRMED

REJECTED
```

---

## Índices

```text
order_id
payment_type
payment_method
payment_status
created_at
confirmed_at
```

---

## Regla de Negocio

El comprobante es opcional.

El administrador puede confirmar manualmente mediante:

```text
manual_confirmation = true
```

---

## Regla de Negocio

Un pago confirmado no debe modificarse.

---

## Regla de Negocio

Los reembolsos se registran como un pago independiente:

```text
payment_type = REFUND
```

---

## Regla de Negocio

No se eliminan registros financieros.

Nunca.

---

## Regla de Negocio

Todos los movimientos financieros deben ser auditables.

# Tabla: production_history

## Propósito

Mantener un historial completo y auditable de los cambios de estado de una solicitud.

Esta tabla funciona como bitácora oficial del sistema.

Nunca debe modificarse ni eliminarse información histórica.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| order_id | UUID | No |
| previous_status | VARCHAR(50) | Sí |
| new_status | VARCHAR(50) | No |
| changed_by | UUID | No |
| notes | TEXT | Sí |
| changed_at | TIMESTAMP | No |

---

## Relaciones

```text
order_id
→ orders.id
```

```text
changed_by
→ users.id
```

---

## Índices

```text
order_id
changed_at
new_status
```

---

## Regla de Negocio

Cada cambio de estado debe generar automáticamente un registro.

---

## Regla de Negocio

No se permiten modificaciones posteriores.

---

## Regla de Negocio

Esta tabla es utilizada para:

- Auditoría.
- Trazabilidad.
- Investigación de incidencias.
- Métricas futuras.
- IA futura.

---

# Tabla: order_events

## Propósito

Registrar todos los eventos relevantes relacionados con una solicitud.

Complementa a production_history ya que no todos los eventos representan cambios de estado.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| order_id | UUID | No |
| event_type | VARCHAR(100) | No |
| event_description | TEXT | Sí |
| metadata | JSONB | Sí |
| created_by | UUID | Sí |
| created_at | TIMESTAMP | No |

---

## Relaciones

```text
order_id
→ orders.id
```

```text
created_by
→ users.id
```

---

## Event Types Iniciales

```text
ORDER_CREATED

FILE_UPLOADED

QUOTE_CREATED

QUOTE_ACCEPTED

QUOTE_REJECTED

PAYMENT_PROOF_UPLOADED

PAYMENT_CONFIRMED

PAYMENT_REJECTED

DEPOSIT_CONFIRMED

BALANCE_CONFIRMED

FULL_PAYMENT_CONFIRMED

STATUS_CHANGED

PRIORITY_CHANGED

SHIPPING_ADDRESS_UPDATED

SHIPMENT_CREATED

ORDER_DELIVERED

REFUND_REQUESTED

REFUND_PROCESSED

ORDER_CANCELLED
```

---

## Metadata

Permite almacenar información adicional específica del evento.

Ejemplo:

```json
{
  "previous_priority": "NORMAL",
  "new_priority": "URGENT"
}
```

---

## Índices

```text
order_id

event_type

created_at
```

---

## Regla de Negocio

Todo evento relevante del sistema debe generar un registro.

---

## Regla de Negocio

Los eventos nunca deben modificarse.

---

## Regla de Negocio

Los eventos nunca deben eliminarse.

---

## Beneficios

- Auditoría completa.
- Dashboard administrativo.
- Reportes.
- Métricas.
- IA futura.
- Trazabilidad.

---

# Tabla: shipments

## Propósito

Registrar información relacionada con envíos a domicilio.

Solo se utiliza cuando:

```text
delivery_method = SHIPPING
```

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| order_id | UUID | No |
| carrier_name | VARCHAR(100) | Sí |
| tracking_number | VARCHAR(100) | Sí |
| shipping_cost | DECIMAL(10,2) | No |
| shipped_at | TIMESTAMP | Sí |
| delivered_at | TIMESTAMP | Sí |
| shipping_notes | TEXT | Sí |
| created_at | TIMESTAMP | No |
| updated_at | TIMESTAMP | No |

---

## Relaciones

```text
order_id
→ orders.id
```

---

## Índices

```text
order_id
tracking_number
shipped_at
```

---

## Regla de Negocio

Un pedido puede tener cero o un envío.

---

## Regla de Negocio

El costo registrado aquí debe coincidir con el costo aprobado en la cotización.

---

## Regla de Negocio

La información de guía es opcional.

---

# Tabla: business_config

## Propósito

Almacenar configuración global del negocio.

Esta tabla es utilizada por:

- Calculadora de costos.
- Pagos.
- Producción.
- Automatizaciones.

---

## Estrategia

Debe existir únicamente un registro activo.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| material_cost_per_kg | DECIMAL(10,2) | No |
| energy_cost_per_hour | DECIMAL(10,2) | No |
| labor_cost_per_hour | DECIMAL(10,2) | No |
| post_processing_cost_per_gram | DECIMAL(10,2) | No |
| packaging_cost | DECIMAL(10,2) | No |
| failure_percentage | DECIMAL(5,2) | No |
| profit_margin_percentage | DECIMAL(5,2) | No |
| urgent_multiplier | DECIMAL(5,2) | No |
| express_multiplier | DECIMAL(5,2) | No |
| full_payment_discount_percentage | DECIMAL(5,2) | No |
| deposit_deadline_hours | INTEGER | No |
| balance_deadline_days | INTEGER | No |
| created_at | TIMESTAMP | No |
| updated_at | TIMESTAMP | No |

---

## Valores Iniciales Recomendados

| Configuración | Valor |
|---------|---------|
| material_cost_per_kg | 25.00 |
| energy_cost_per_hour | 0.50 |
| labor_cost_per_hour | 15.00 |
| post_processing_cost_per_gram | 0.05 |
| packaging_cost | 2.00 |
| failure_percentage | 10.00 |
| profit_margin_percentage | 30.00 |
| urgent_multiplier | 1.30 |
| express_multiplier | 1.50 |
| full_payment_discount_percentage | 5.00 |
| deposit_deadline_hours | 72 |
| balance_deadline_days | 7 |

---

## Regla de Negocio

Todas las cotizaciones deben calcularse utilizando la configuración vigente al momento de crear la cotización.

---

# Tabla: business_hours

## Propósito

Configurar horarios oficiales del taller.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| weekday | INTEGER | No |
| is_open | BOOLEAN | No |
| opening_time | TIME | Sí |
| closing_time | TIME | Sí |
| notes | TEXT | Sí |

---

## Valores de weekday

| Valor | Día |
|---------|---------|
| 1 | Monday |
| 2 | Tuesday |
| 3 | Wednesday |
| 4 | Thursday |
| 5 | Friday |
| 6 | Saturday |
| 7 | Sunday |

---

## Regla de Negocio

Si:

```text
is_open = false
```

entonces:

```text
opening_time
closing_time
```

deben ser NULL.

---

## Regla de Negocio

Estos horarios son utilizados para:

- Recolección en taller.
- Cálculo de plazos.
- Información al cliente.

---

# Tabla: holidays

## Propósito

Registrar días festivos que afectan la operación.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| holiday_date | DATE | No |
| holiday_name | VARCHAR(255) | No |
| affects_shipping | BOOLEAN | No |
| affects_pickup | BOOLEAN | No |
| created_at | TIMESTAMP | No |

---

## Índices

```text
holiday_date
```

---

## Regla de Negocio

Los días festivos deben excluirse del cálculo de fechas de entrega.

---

## Regla de Negocio

No deben existir fechas duplicadas.

---

# Tabla: payment_instructions

## Propósito

Almacenar información bancaria visible para clientes.

---

## Campos

| Campo | Tipo | Nullable |
|---------|---------|---------|
| id | UUID | No |
| bank_name | VARCHAR(100) | No |
| account_holder | VARCHAR(255) | No |
| account_number | VARCHAR(50) | Sí |
| clabe | VARCHAR(30) | Sí |
| card_number | VARCHAR(30) | Sí |
| additional_notes | TEXT | Sí |
| updated_at | TIMESTAMP | No |

---

## Regla de Negocio

Debe existir únicamente un registro activo.

---

## Regla de Negocio

Los cambios deben reflejarse inmediatamente en futuras instrucciones de pago.

---

# Constraints Recomendados

## Users

```text
UNIQUE(phone)

UNIQUE(email)
```

---

## Shipping Addresses

```text
CHECK(
    country <> ''
)
```

---

## Orders

```text
CHECK(
    quantity > 0
)
```

---

## Quotes

```text
CHECK(
    total_price >= 0
)
```

---

## Payments

```text
CHECK(
    amount > 0
)
```

---

## Business Config

```text
CHECK(
    profit_margin_percentage >= 0
)
```

```text
CHECK(
    urgent_multiplier >= 1
)
```

```text
CHECK(
    express_multiplier >= 1
)
```

---

# Índices Adicionales Recomendados

## Orders

```text
(status, created_at)

(customer_id, status)

(priority, status)
```

---

## Quotes

```text
(order_id, quote_status)
```

---

## Payments

```text
(order_id, payment_status)
```

---

## Production History

```text
(order_id, changed_at)
```

---

# Recomendaciones para Django Models

## UUID

Todas las entidades:

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

---

## BaseModel

Crear una clase abstracta reutilizable:

```python
class BaseModel(models.Model):

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True
```

---

## SoftDeleteModel

Crear una segunda clase abstracta:

```python
class SoftDeleteModel(BaseModel):

    is_deleted = models.BooleanField(
        default=False
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
```

---

# Recomendaciones para Migraciones

Orden sugerido:

```text
users

shipping_addresses

orders

request_files

quotes

payments

production_history

shipments

business_config

business_hours

holidays

payment_instructions
```

---

# Preparación para IA

Los siguientes campos existen únicamente para expansión futura:

```text
ai_analysis

ai_notes

ai_confidence

ai_category
```

---

## Restricción MVP

Durante el MVP:

```text
Todos los campos AI deben permanecer vacíos.
```

---

## Fases Futuras

### Fase 1

Clasificación automática de solicitudes.

---

### Fase 2

Sugerencia de cotizaciones.

---

### Fase 3

Optimización de producción.

---

# Integridad del Sistema

No deben existir:

- Pagos huérfanos.
- Cotizaciones huérfanas.
- Archivos huérfanos.
- Historial huérfano.
- Envíos huérfanos.

Todas las relaciones deben estar protegidas mediante claves foráneas.

---

# Objetivo del Diseño

Proporcionar una estructura de datos robusta, escalable y mantenible que permita operar completamente Imprint Studio utilizando reglas de negocio claras, automatización controlada y una arquitectura preparada para futuras expansiones sin requerir rediseños significativos.

---

# Estado del Documento

Versión: 2.0

Estado:

Aprobado para implementación.

Fuente oficial para:

- Django Models
- Migraciones
- PostgreSQL
- DRF
- Servicios
- Automatizaciones
- Futuras integraciones de IA

Fin del documento.