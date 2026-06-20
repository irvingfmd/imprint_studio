# API Specification

## Imprint Studio

Versión: 3.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define la especificación oficial de la API REST de Imprint Studio.

La API será consumida por:

* Frontend Vue 3
* Aplicaciones móviles futuras
* Integraciones externas futuras
* Herramientas administrativas
* Automatizaciones
* Futuras integraciones de IA

Toda implementación deberá respetar este contrato.

---

# Estándares Generales

## Arquitectura

Estilo:

```text
REST API
```

---

## Formato de Datos

Todas las peticiones y respuestas utilizan:

```text
application/json
```

Excepto carga de archivos:

```text
multipart/form-data
```

---

## Versionado

Todas las rutas deben incluir versión.

Formato:

```text
/api/v1/
```

---

## Base URL

### Desarrollo

```text
http://localhost:8000/api/v1
```

---

### Producción

```text
https://api.imprintstudio.com/api/v1
```

---

# Convenciones

## URLs

Utilizar:

```text
kebab-case
```

Ejemplo:

```http
/shipping-addresses/
```

---

## Campos JSON

Utilizar:

```text
snake_case
```

Ejemplo:

```json
{
  "weight_grams": 250
}
```

---

## UUID

Todas las entidades utilizan:

```text
UUID
```

Ejemplo:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

# Autenticación

Sistema:

```text
JWT
```

---

## Header Requerido

```http
Authorization: Bearer <access_token>
```

---

## Refresh Token

El sistema debe utilizar:

```text
SimpleJWT
```

---

# Respuestas Estándar

## Respuesta Exitosa

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

---

## Error de Validación

```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "phone": [
      "This field is required."
    ]
  }
}
```

---

## Error de Permisos

```json
{
  "success": false,
  "message": "Permission denied"
}
```

---

## Error No Encontrado

```json
{
  "success": false,
  "message": "Resource not found"
}
```

---

# Authentication Module

Base Path:

```http
/api/v1/auth/
```

---

# Register User

## Endpoint

```http
POST /api/v1/auth/register/
```

---

## Authentication

No requerida.

---

## Request

```json
{
  "phone": "+5219611234567",
  "email": "cliente@example.com",
  "first_name": "Irving",
  "last_name": "Martinez"
}
```

---

## Response

```json
{
  "success": true,
  "message": "User registered successfully"
}
```

---

# Send OTP

## Endpoint

```http
POST /api/v1/auth/otp/send/
```

---

## Authentication

No requerida.

---

## Request

```json
{
  "phone": "+5219611234567"
}
```

---

## Response

```json
{
  "success": true,
  "message": "OTP sent successfully"
}
```

---

# Verify OTP

## Endpoint

```http
POST /api/v1/auth/otp/verify/
```

---

## Authentication

No requerida.

---

## Request

```json
{
  "phone": "+5219611234567",
  "otp_code": "123456"
}
```

---

## Response

```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}
```

---

# Refresh Token

## Endpoint

```http
POST /api/v1/auth/token/refresh/
```

---

## Request

```json
{
  "refresh": "refresh_token"
}
```

---

## Response

```json
{
  "access": "new_access_token"
}
```

---

# Current User

## Endpoint

```http
GET /api/v1/auth/me/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "id": "uuid",
  "phone": "+5219611234567",
  "email": "cliente@example.com",
  "first_name": "Irving",
  "last_name": "Martinez",
  "role": "CUSTOMER"
}
```

---

# Orders Module

Base Path:

```http
/api/v1/orders/
```

---

# List Orders

## Endpoint

```http
GET /api/v1/orders/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "count": 1,
  "results": [
    {
      "id": "uuid",
      "title": "Figura personalizada",
      "status": "RECEIVED"
    }
  ]
}
```

---

# Create Order

## Endpoint

```http
POST /api/v1/orders/
```

---

## Authentication

Requerida.

---

## Request

```json
{
  "request_type": "REFERENCE",
  "title": "Figura personalizada",
  "description": "Figura estilo anime",
  "color": "Black",
  "quantity": 1,
  "priority": "NORMAL",
  "delivery_method": "PICKUP"
}
```

---

## Request Type

Valores permitidos:

```text
REFERENCE
PRINTABLE_FILE
WEB_MODEL
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

## Response

```json
{
  "id": "uuid",
  "status": "RECEIVED"
}
```

---

# Retrieve Order

## Endpoint

```http
GET /api/v1/orders/{order_id}/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "id": "uuid",
  "title": "Figura personalizada",
  "description": "Figura estilo anime",
  "status": "RECEIVED",
  "priority": "NORMAL"
}
```

---

# Cancel Order

## Endpoint

```http
PUT /api/v1/orders/{order_id}/cancel/
```

---

## Authentication

Requerida.

---

## Request

```json
{
  "reason": "Client request"
}
```

---

## Response

```json
{
  "success": true,
  "message": "Order cancelled"
}
```

---

# Assign Shipping Address

## Endpoint

```http
PUT /api/v1/orders/{order_id}/shipping-address/
```

---

## Authentication

Requerida.

---

## Request

```json
{
  "shipping_address_id": "uuid"
}
```

---

## Response

```json
{
  "success": true,
  "message": "Shipping address assigned"
}
```

---

# Request Files Module

Base Path:

```http
/api/v1/orders/{order_id}/files/
```

---

# Upload File

## Endpoint

```http
POST /api/v1/orders/{order_id}/files/
```

---

## Authentication

Requerida.

---

## Content Type

```text
multipart/form-data
```

---

## Fields

```text
file
file_type
```

---

## File Types

```text
REFERENCE

PRINTABLE_FILE

WEB_MODEL

PAYMENT_PROOF
```

---

## Response

```json
{
  "id": "uuid",
  "file_type": "STL"
}
```

---

# List Files

## Endpoint

```http
GET /api/v1/orders/{order_id}/files/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "results": []
}
```
# Quotes Module

Base Path:

```http
/api/v1/quotes/
```

---

# Get Quote

## Endpoint

```http
GET /api/v1/quotes/{quote_id}/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "id": "uuid",
  "order_id": "uuid",
  "weight_grams": 250.00,
  "print_time_hours": 12.50,
  "material_cost": 15.20,
  "energy_cost": 6.25,
  "labor_cost": 187.50,
  "post_processing_cost": 12.50,
  "packaging_cost": 2.00,
  "risk_cost": 2.15,
  "shipping_cost": 120.00,
  "subtotal": 345.60,
  "profit_amount": 103.68,
  "discount_amount": 0.00,
  "tax_amount": 69.84,
  "total_price": 506.31,
  "quote_status": "PENDING"
}
```

---

# List Order Quotes

## Endpoint

```http
GET /api/v1/orders/{order_id}/quotes/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "count": 1,
  "results": []
}
```

---

# Accept Quote

## Endpoint

```http
PUT /api/v1/quotes/{quote_id}/accept/
```

---

## Authentication

Requerida.

---

## Request

```json
{
  "payment_option": "DEPOSIT"
}
```

---

## Payment Options

```text
DEPOSIT
FULL_PAYMENT
```

---

## Response

```json
{
  "success": true,
  "message": "Quote accepted"
}
```

---

# Reject Quote

## Endpoint

```http
PUT /api/v1/quotes/{quote_id}/reject/
```

---

## Authentication

Requerida.

---

## Request

```json
{
  "reason": "Too expensive"
}
```

---

## Response

```json
{
  "success": true,
  "message": "Quote rejected"
}
```

---

# Quote Snapshots Module

Base Path:

```http
/api/v1/quotes/{quote_id}/snapshot/
```

---

# Get Quote Snapshot

## Endpoint

```http
GET /api/v1/quotes/{quote_id}/snapshot/
```

---

## Authentication

ADMIN únicamente.

---

## Response

```json
{
  "material_cost_per_kg": 25.00,
  "electricity_rate_kwh": 1.50,
  "labor_cost_per_hour": 15.00,
  "post_processing_cost_per_gram": 0.05,
  "failure_percentage": 10.00,
  "profit_margin_percentage": 30.00,
  "tax_percentage": 16.00,
  "printer_name": "Bambu Lab X1C",
  "printer_power_watts": 200
}
```

---

# Payments Module

Base Path:

```http
/api/v1/payments/
```

---

# List Payments

## Endpoint

```http
GET /api/v1/orders/{order_id}/payments/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "count": 2,
  "results": []
}
```

---

# Retrieve Payment

## Endpoint

```http
GET /api/v1/payments/{payment_id}/
```

---

## Authentication

Requerida.

---

# Upload Payment Proof

## Endpoint

```http
POST /api/v1/payments/{payment_id}/proof/
```

---

## Authentication

Requerida.

---

## Content Type

```text
multipart/form-data
```

---

## Fields

```text
file
```

---

## Response

```json
{
  "success": true,
  "message": "Payment proof uploaded"
}
```

---

# Shipping Addresses Module

Base Path:

```http
/api/v1/shipping-addresses/
```

---

# List Addresses

## Endpoint

```http
GET /api/v1/shipping-addresses/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "count": 1,
  "results": []
}
```

---

# Create Address

## Endpoint

```http
POST /api/v1/shipping-addresses/
```

---

## Authentication

Requerida.

---

## Request

```json
{
  "address_name": "Casa",
  "street": "Morelos",
  "external_number": "234",
  "internal_number": "A",
  "neighborhood": "Centro",
  "postal_code": "29000",
  "city": "Tuxtla Gutierrez",
  "state": "Chiapas",
  "country": "Mexico",
  "references": "Portón negro"
}
```

---

## Response

```json
{
  "id": "uuid"
}
```

---

# Retrieve Address

## Endpoint

```http
GET /api/v1/shipping-addresses/{address_id}/
```

---

## Authentication

Requerida.

---

# Update Address

## Endpoint

```http
PUT /api/v1/shipping-addresses/{address_id}/
```

---

## Authentication

Requerida.

---

# Delete Address

## Endpoint

```http
DELETE /api/v1/shipping-addresses/{address_id}/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "success": true,
  "message": "Address deleted"
}
```

---

# Order Events Module

Base Path:

```http
/api/v1/orders/{order_id}/events/
```

---

# List Order Events

## Endpoint

```http
GET /api/v1/orders/{order_id}/events/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "count": 10,
  "results": [
    {
      "event_type": "QUOTE_CREATED",
      "created_at": "2026-06-01T10:00:00Z"
    }
  ]
}
```

---

# Retrieve Event

## Endpoint

```http
GET /api/v1/orders/{order_id}/events/{event_id}/
```

---

## Authentication

Requerida.

---

# Production History Module

Base Path:

```http
/api/v1/orders/{order_id}/production-history/
```

---

# List Production History

## Endpoint

```http
GET /api/v1/orders/{order_id}/production-history/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "count": 5,
  "results": [
    {
      "previous_status": "PRINTING",
      "new_status": "POST_PROCESSING",
      "changed_at": "2026-06-01T14:00:00Z"
    }
  ]
}
```

---

# Shipments Module

Base Path:

```http
/api/v1/shipments/
```

---

# Retrieve Shipment

## Endpoint

```http
GET /api/v1/shipments/{shipment_id}/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "carrier_name": "Estafeta",
  "tracking_number": "123456789",
  "shipped_at": "2026-06-01T10:00:00Z"
}
```

---

# Public Payment Instructions

## Endpoint

```http
GET /api/v1/payment-instructions/
```

---

## Authentication

Requerida.

---

## Response

```json
{
  "bank_name": "BBVA",
  "account_holder": "Imprint Studio",
  "clabe": "012345678901234567",
  "additional_notes": "Enviar comprobante al finalizar."
}
```
# Admin Module

Todas las rutas administrativas deben vivir bajo:

```http
/api/v1/admin/
```

---

# Reglas Generales de Administración

## Authentication

Requerida.

---

## Permission

Únicamente usuarios con rol:

```text
ADMIN
```

---

## Regla

Los clientes nunca deben poder acceder a rutas administrativas.

---

# Admin Orders Module

Base Path:

```http
/api/v1/admin/orders/
```

---

# List All Orders

## Endpoint

```http
GET /api/v1/admin/orders/
```

---

## Authentication

Requerida.

---

## Permission

ADMIN.

---

## Query Params

```text
status
priority
customer_id
request_type
delivery_method
created_from
created_to
```

---

## Response

```json
{
  "count": 10,
  "results": []
}
```

---

# Create Admin Order

## Endpoint

```http
POST /api/v1/admin/orders/create/
```

---

## Authentication

Requerida.

---

## Permission

ADMIN.

---

## Request

```json
{
  "customer_id": "uuid",
  "request_type": "REFERENCE",
  "title": "Figura personalizada",
  "description": "",
  "color": "Negro",
  "quantity": 1,
  "priority": "NORMAL",
  "delivery_method": "PICKUP"
}
```

`description` es opcional (puede enviarse vacío).

---

## Response

```json
{
  "success": true,
  "message": "Order created by admin",
  "data": {
    "id": "uuid",
    "status": "RECEIVED"
  }
}
```

---

## Regla de Negocio

El pedido se crea a nombre del cliente identificado por `customer_id`.
El admin puede buscar clientes por teléfono usando `GET /api/v1/admin/users/?search=961`.

---

# Retrieve Admin Order

## Endpoint

```http
GET /api/v1/admin/orders/{order_id}/
```

---

## Authentication

Requerida.

---

## Permission

ADMIN.

---

# Update Order Status

## Endpoint

```http
PUT /api/v1/admin/orders/{order_id}/status/
```

---

## Authentication

Requerida.

---

## Permission

ADMIN.

---

## Request

```json
{
  "status": "PRINTING",
  "notes": "La impresión inició correctamente."
}
```

---

## Response

```json
{
  "success": true,
  "message": "Order status updated"
}
```

---

## Regla de Negocio

Este endpoint debe utilizar:

```text
OrderStatusTransitionService
```

---

## Regla de Negocio

Cada cambio de estado debe crear registros en:

```text
production_history
order_events
```

---

# Cancel Order as Admin

## Endpoint

```http
PUT /api/v1/admin/orders/{order_id}/cancel/
```

---

## Request

```json
{
  "reason": "Cancelled by admin"
}
```

---

## Response

```json
{
  "success": true,
  "message": "Order cancelled"
}
```

---

# Revert Order Status

## Endpoint

```http
PUT /api/v1/admin/orders/{order_id}/revert/
```

---

## Request

```json
{
  "reason": "Cambio accidental de estado"
}
```

---

## Response

```json
{
  "success": true,
  "message": "Order status reverted",
  "data": {
    "status": "DEPOSIT_PAID"
  }
}
```

---

## Regla de Negocio

No se puede revertir desde DELIVERED ni CANCELLED.
Requiere al menos un registro en production_history.

---

# Admin Quotes Module

Base Path:

```http
/api/v1/admin/quotes/
```

---

# Create Quote

## Endpoint

```http
POST /api/v1/admin/orders/{order_id}/quote/
```

---

## Authentication

Requerida.

---

## Permission

ADMIN.

---

## Request

```json
{
  "weight_grams": 250.00,
  "print_time_hours": 12.50,
  "shipping_cost": 120.00,
  "printer_id": "uuid-de-la-impresora-o-null",
  "include_post_processing": true
}
```

---

## Response

```json
{
  "success": true,
  "message": "Quote created",
  "data": {
    "quote_id": "uuid",
    "total_price": 506.31
  }
}
```

---

## Regla de Negocio

La cotización debe crearse usando datos reales de Bambu Studio.

---

## Regla de Negocio

Al crear una cotización también se debe crear:

```text
quote_snapshots
```

---

## Regla de Negocio

Al crear una cotización también se debe crear un evento:

```text
QUOTE_CREATED
```

en:

```text
order_events
```

---

# Expire Quote

## Endpoint

```http
PUT /api/v1/admin/quotes/{quote_id}/expire/
```

---

## Response

```json
{
  "success": true,
  "message": "Quote expired"
}
```

---

# Admin Payments Module

Base Path:

```http
/api/v1/admin/payments/
```

---

# List Admin Payments

## Endpoint

```http
GET /api/v1/admin/payments/
```

---

## Query Params

```text
payment_type
payment_method
payment_status
order_id
created_from
created_to
```

---

## Response

```json
{
  "count": 10,
  "results": []
}
```

---

# Confirm Payment

## Endpoint

```http
PUT /api/v1/admin/payments/{payment_id}/confirm/
```

---

## Request

```json
{
  "notes": "Pago confirmado por transferencia bancaria."
}
```

---

## Response

```json
{
  "success": true,
  "message": "Payment confirmed"
}
```

---

## Regla de Negocio

Al confirmar un pago, el sistema debe actualizar el estado financiero del pedido.

---

## Regla de Negocio

Al confirmar un pago, debe crearse un evento en:

```text
order_events
```

Valores posibles:

```text
DEPOSIT_CONFIRMED
BALANCE_CONFIRMED
FULL_PAYMENT_CONFIRMED
PAYMENT_CONFIRMED
```

---

# Reject Payment

## Endpoint

```http
PUT /api/v1/admin/payments/{payment_id}/reject/
```

---

## Request

```json
{
  "reason": "Comprobante no válido."
}
```

---

## Response

```json
{
  "success": true,
  "message": "Payment rejected"
}
```

---

# Manual Payment Confirmation

## Endpoint

```http
POST /api/v1/admin/orders/{order_id}/payments/manual-confirmation/
```

---

## Request

```json
{
  "payment_type": "DEPOSIT",
  "payment_method": "BANK_TRANSFER",
  "amount": 500.00,
  "notes": "Cliente envió comprobante por WhatsApp."
}
```

---

## Response

```json
{
  "success": true,
  "message": "Manual payment registered"
}
```

---

## Regla de Negocio

Este endpoint debe crear un pago con:

```text
manual_confirmation = true
payment_status = CONFIRMED
```

---

# Admin Refunds Module

Base Path:

```http
/api/v1/admin/refunds/
```

---

# Process Refund

## Endpoint

```http
POST /api/v1/admin/orders/{order_id}/refund/
```

---

## Request

```json
{
  "amount": 500.00,
  "reason": "Cancelación antes de impresión."
}
```

---

## Response

```json
{
  "success": true,
  "message": "Refund registered"
}
```

---

## Regla de Negocio

El reembolso se registra como:

```text
payment_type = REFUND
```

---

## Regla de Negocio

El reembolso debe crear evento:

```text
REFUND_PROCESSED
```

---

# Admin Shipments Module

Base Path:

```http
/api/v1/admin/shipments/
```

---

# Create Shipment

## Endpoint

```http
POST /api/v1/admin/orders/{order_id}/shipment/
```

---

## Request

```json
{
  "carrier_name": "Estafeta",
  "tracking_number": "123456789",
  "shipping_cost": 120.00,
  "shipping_notes": "Envío local confirmado por WhatsApp."
}
```

---

## Response

```json
{
  "success": true,
  "message": "Shipment created"
}
```

---

# Mark Shipment as Delivered

## Endpoint

```http
PUT /api/v1/admin/shipments/{shipment_id}/delivered/
```

---

## Response

```json
{
  "success": true,
  "message": "Shipment marked as delivered"
}
```

---

# Admin Business Configuration Module

Base Path:

```http
/api/v1/admin/business-config/
```

---

# Get Business Configuration

## Endpoint

```http
GET /api/v1/admin/business-config/
```

---

## Response

```json
{
  "material_cost_per_kg": 25.00,
  "electricity_rate_kwh": 1.50,
  "labor_cost_per_hour": 15.00,
  "post_processing_cost_per_gram": 0.05,
  "packaging_cost": 2.00,
  "failure_percentage": 10.00,
  "profit_margin_percentage": 30.00,
  "urgent_multiplier": 1.30,
  "express_multiplier": 1.50,
  "full_payment_discount_percentage": 5.00,
  "tax_percentage": 16.00,
  "deposit_deadline_hours": 72,
  "balance_deadline_days": 7
}
```

---

# Update Business Configuration

## Endpoint

```http
PUT /api/v1/admin/business-config/
```

---

## Request

```json
{
  "material_cost_per_kg": 25.00,
  "electricity_rate_kwh": 1.50,
  "labor_cost_per_hour": 15.00,
  "post_processing_cost_per_gram": 0.05,
  "packaging_cost": 2.00,
  "failure_percentage": 10.00,
  "profit_margin_percentage": 30.00,
  "urgent_multiplier": 1.30,
  "express_multiplier": 1.50,
  "full_payment_discount_percentage": 5.00,
  "tax_percentage": 16.00,
  "deposit_deadline_hours": 72,
  "balance_deadline_days": 7
}
```

---

# Admin Business Hours Module

Base Path:

```http
/api/v1/admin/business-hours/
```

---

# List Business Hours

## Endpoint

```http
GET /api/v1/admin/business-hours/
```

---

# Update Business Hours

## Endpoint

```http
PUT /api/v1/admin/business-hours/
```

---

## Request

```json
{
  "weekday": 1,
  "is_open": true,
  "opening_time": "09:00",
  "closing_time": "18:00",
  "notes": "Horario normal."
}
```

---

# Admin Holidays Module

Base Path:

```http
/api/v1/admin/holidays/
```

---

# List Holidays

## Endpoint

```http
GET /api/v1/admin/holidays/
```

---

# Create Holiday

## Endpoint

```http
POST /api/v1/admin/holidays/
```

---

## Request

```json
{
  "holiday_date": "2026-12-25",
  "holiday_name": "Christmas",
  "affects_shipping": true,
  "affects_pickup": true
}
```

---

# Delete Holiday

## Endpoint

```http
DELETE /api/v1/admin/holidays/{holiday_id}/
```

---

# Admin Payment Instructions Module

Base Path:

```http
/api/v1/admin/payment-instructions/
```

---

# Get Payment Instructions

## Endpoint

```http
GET /api/v1/admin/payment-instructions/
```

---

# Update Payment Instructions

## Endpoint

```http
PUT /api/v1/admin/payment-instructions/
```

---

## Request

```json
{
  "bank_name": "BBVA",
  "account_holder": "Imprint Studio",
  "account_number": "1234567890",
  "clabe": "012345678901234567",
  "card_number": "1234567890123456",
  "additional_notes": "Enviar comprobante después de realizar la transferencia."
}
```

---

# Admin Dashboard Module

Base Path:

```http
/api/v1/admin/dashboard/
```

---

# Get Dashboard Metrics

## Endpoint

```http
GET /api/v1/admin/dashboard/
```

---

## Response

```json
{
  "pending_orders": 10,
  "quoted_orders": 5,
  "printing_orders": 3,
  "ready_orders": 2,
  "pending_payments": 4,
  "monthly_revenue": 25000.00
}
```

---

# Permissions

## CUSTOMER

Puede:

* Crear pedidos.
* Ver sus pedidos.
* Ver sus cotizaciones.
* Subir archivos.
* Subir comprobantes.
* Ver sus pagos.
* Gestionar sus direcciones.
* Solicitar cancelación.

---

## CUSTOMER no puede

* Ver pedidos de otros clientes.
* Confirmar pagos.
* Crear cotizaciones.
* Cambiar estados.
* Procesar reembolsos.
* Modificar configuración.

---

## ADMIN

Puede:

* Ver todos los pedidos.
* Crear cotizaciones.
* Confirmar pagos.
* Rechazar pagos.
* Procesar reembolsos.
* Cambiar estados.
* Gestionar envíos.
* Modificar configuración.
* Ver dashboard.

---

# Rate Limiting

Aplicar límites a:

```http
POST /api/v1/auth/register/

POST /api/v1/auth/otp/send/

POST /api/v1/auth/otp/verify/
```

---

# Rate Limits Recomendados

```text
OTP send:
5 solicitudes por hora por teléfono

OTP verify:
5 intentos por OTP

Register:
10 solicitudes por hora por IP
```

---

# Seguridad

## Regla

Toda ruta debe validar autenticación y permisos.

---

## Regla

Un cliente solo puede acceder a recursos propios.

---

## Regla

Un administrador puede acceder a recursos globales.

---

# Auditoría

Las siguientes acciones deben crear eventos en:

```text
order_events
```

---

## Eventos Obligatorios

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

# Códigos HTTP Esperados

| Código | Uso                   |
| ------ | --------------------- |
| 200    | Operación exitosa     |
| 201    | Recurso creado        |
| 204    | Eliminación exitosa   |
| 400    | Error de validación   |
| 401    | No autenticado        |
| 403    | Sin permisos          |
| 404    | Recurso no encontrado |
| 409    | Conflicto de estado   |
| 429    | Rate limit            |
| 500    | Error interno         |

---

# Reglas Finales

La API debe ser:

* Consistente.
* Versionada.
* Segura.
* Documentable.
* Compatible con Swagger/OpenAPI.
* Fácil de consumir desde Vue 3.
* Preparada para futuras integraciones.

---

# Estado del Documento

Versión: 2.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* Django REST Framework
* Serializers
* Views
* ViewSets
* Routers
* Frontend Vue
* Pruebas QA
* Futuras integraciones

---

# Admin Printers Module

Base Path:

```http
/api/v1/admin/printers/
```

Permiso requerido: `IsAdmin`

---

# List Printers

## Endpoint

```http
GET /api/v1/admin/printers/
```

---

## Query Params

```text
active_only=true   (default: false — devuelve todas)
```

---

## Response

```json
{
  "success": true,
  "message": "OK",
  "data": [
    {
      "id": "uuid",
      "name": "X1 Carbon",
      "brand": "Bambu Lab",
      "power_watts": 200,
      "max_power_watts": 350,
      "is_active": true
    }
  ]
}
```

---

# Create Printer

## Endpoint

```http
POST /api/v1/admin/printers/
```

---

## Request

```json
{
  "name": "X1 Carbon",
  "brand": "Bambu Lab",
  "power_watts": 200,
  "max_power_watts": 350,
  "is_active": true
}
```

---

## Response

```json
{
  "success": true,
  "message": "Printer created",
  "data": {
    "id": "uuid",
    "name": "X1 Carbon",
    "brand": "Bambu Lab",
    "power_watts": 200,
    "max_power_watts": 350,
    "is_active": true
  }
}
```

---

# Retrieve Printer

## Endpoint

```http
GET /api/v1/admin/printers/{printer_id}/
```

---

# Update Printer

## Endpoint

```http
PUT /api/v1/admin/printers/{printer_id}/
```

---

## Request

```json
{
  "name": "X1 Carbon",
  "brand": "Bambu Lab",
  "power_watts": 200,
  "max_power_watts": 350,
  "is_active": true
}
```

---

# Delete Printer

## Endpoint

```http
DELETE /api/v1/admin/printers/{printer_id}/
```

---

## Response

```json
{
  "success": true,
  "message": "Printer deleted"
}
```

---

# Admin CFE Rate Lookup

## Endpoint

```http
GET /api/v1/admin/electricity-rate-lookup/
```

Permiso requerido: `IsAdmin`

---

## Query Params

```text
postal_code=29000
```

---

## Response

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "postal_code": "29000",
    "cfe_zone": "DAC",
    "reference_rate_kwh": 1.50,
    "notes": "Tarifa de referencia. Verificar recibo CFE para valor exacto."
  }
}
```

---

# Admin Calculator — Calculate

## Endpoint

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
  "printer_id": "uuid-de-la-impresora-o-null",
  "full_payment_selected": false,
  "include_post_processing": true
}
```

---

## Nota sobre `printer_id`

Si se envía `null` o se omite, `energy_cost = 0`.

## Nota sobre `include_post_processing`

Si se envía `false`, `post_processing_cost = 0`. Default: `true`.

---

## Response

```json
{
  "material_cost": 6.25,
  "energy_cost": 0.60,
  "labor_cost": 187.50,
  "post_processing_cost": 12.50,
  "packaging_cost": 2.00,
  "risk_cost": 0.69,
  "base_cost": 209.54,
  "priority_multiplier": 1.00,
  "priority_cost": 209.54,
  "shipping_cost": 120.00,
  "subtotal": 329.54,
  "profit_amount": 98.86,
  "discount_amount": 0.00,
  "tax_amount": 68.54,
  "total_price": 496.94
}
```

---

# Admin Users Module

Base Path:

```http
/api/v1/admin/users/
```

Permiso requerido: `IsAdmin`

---

# List Admin Users

## Endpoint

```http
GET /api/v1/admin/users/
```

---

## Query Params

| Param | Type | Default | Description |
|---|---|---|---|
| page | int | 1 | Número de página |
| page_size | int | 20 | Resultados por página |
| search | string | — | Filtra por teléfono (icontains) |

---

## Response 200

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "count": 42,
    "num_pages": 3,
    "results": [
      {
        "id": "uuid",
        "phone": "+529611234567",
        "email": "user@email.com",
        "first_name": "Ana",
        "last_name": "López",
        "role": "CUSTOMER",
        "is_active": true,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ]
  }
}
```

---

# Retrieve Admin User

## Endpoint

```http
GET /api/v1/admin/users/{user_id}/
```

---

## Response 200

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "id": "uuid",
    "phone": "+529611234567",
    "email": "user@email.com",
    "first_name": "Ana",
    "last_name": "López",
    "role": "CUSTOMER",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

# Update User Role

## Endpoint

```http
PUT /api/v1/admin/users/{user_id}/role/
```

---

## Request Body

```json
{
  "role": "ADMIN"
}
```

Valores válidos: `CUSTOMER`, `ADMIN`.

---

## Regla de Negocio

Un administrador no puede cambiar su propio rol para evitar auto-degradación accidental.

---

## Response 200

```json
{
  "success": true,
  "message": "Rol actualizado.",
  "data": {
    "id": "uuid",
    "phone": "+529611234567",
    "role": "ADMIN",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

## Response 400 (auto-degradación)

```json
{
  "success": false,
  "message": "No puedes cambiar tu propio rol."
}
```

---

# Quote PDF

## Endpoint

```http
GET /api/v1/quotes/{quote_id}/pdf/
```

Permiso requerido: propietario del pedido o `IsAdmin`.

---

## Response 200

```text
Content-Type: application/pdf
Content-Disposition: attachment; filename="cotizacion-{short_id}.pdf"

<binary PDF data>
```

El PDF incluye: datos del pedido, desglose de costos, opciones de pago e instrucciones de transferencia.

---

---

# Repetir Pedido

## Endpoint

```http
POST /api/v1/orders/{order_id}/repeat/
```

Permiso requerido: `IsAuthenticated` (solo el dueño del pedido).

Clona los datos del pedido (título, descripción, color, cantidad, tipo, prioridad, método de entrega) como un pedido nuevo. No clona archivos, pagos ni cotizaciones.

---

## Response 201

```json
{
  "success": true,
  "message": "Order repeated",
  "data": {
    "id": "uuid",
    "status": "RECEIVED"
  }
}
```

---

# Reseñas

## Crear reseña

```http
POST /api/v1/orders/{order_id}/review/
```

Permiso: `IsAuthenticated` (dueño del pedido, solo si `status = DELIVERED`).

### Request Body

```json
{
  "rating": 5,
  "comment": "Excelente trabajo, quedó increíble."
}
```

- `rating`: entero 1-5 (obligatorio)
- `comment`: texto (opcional)

---

## Obtener reseña

```http
GET /api/v1/orders/{order_id}/review/
```

Permiso: `IsAuthenticated` (dueño o admin).

---

# Notas Internas (Admin)

## Endpoint

```http
GET/POST /api/v1/admin/orders/{order_id}/notes/
```

Permiso: `IsAdmin`.

### Request Body (POST)

```json
{
  "content": "El cliente pidió que se use PLA negro mate."
}
```

- `content`: texto, máx 2000 caracteres

---

# Materiales (Público)

## Endpoint

```http
GET /api/v1/materials/
```

Permiso: `IsAuthenticated`.

Retorna lista de materiales activos con colores disponibles.

---

# Admin — Materiales

## Listar / Crear

```http
GET/POST /api/v1/admin/materials/
```

Params: `?active_only=true`, `?low_stock=true`

### Request Body (POST)

```json
{
  "name": "PLA Premium",
  "material_type": "PLA",
  "brand": "eSun",
  "available_colors": ["Negro", "Blanco", "Rojo", "Azul"],
  "price_per_kg": "350.00",
  "stock_grams": "5000.00",
  "min_stock_grams": "500.00",
  "is_active": true
}
```

---

## Detalle / Editar / Eliminar

```http
GET/PUT/DELETE /api/v1/admin/materials/{material_id}/
```

---

## Ajustar Stock

```http
POST /api/v1/admin/materials/{material_id}/stock/
```

### Request Body

```json
{
  "grams": "1000.00",
  "operation": "add"
}
```

- `operation`: `"add"` o `"deduct"`

---

# Admin — Reseñas

## Endpoint

```http
GET /api/v1/admin/reviews/
```

Permiso: `IsAdmin`. Lista todas las reseñas con paginación.

---

# Admin — Descuentos

## Listar / Crear

```http
GET/POST /api/v1/admin/discounts/
```

### Request Body (POST)

```json
{
  "code": "BIENVENIDO10",
  "discount_type": "PERCENTAGE",
  "discount_value": "10.00",
  "min_order_amount": "100.00",
  "max_uses": 50,
  "valid_from": "2026-06-01T00:00:00Z",
  "valid_until": "2026-12-31T23:59:59Z",
  "is_active": true
}
```

---

## Detalle / Editar / Eliminar

```http
GET/PUT/DELETE /api/v1/admin/discounts/{discount_id}/
```

---

## Redemptions

```http
GET /api/v1/admin/discounts/{discount_id}/redemptions/
```

---

# Validar Descuento (Cliente)

```http
POST /api/v1/discounts/validate/
```

Permiso: `IsAuthenticated`.

### Request Body

```json
{
  "code": "BIENVENIDO10"
}
```

### Response 200

```json
{
  "success": true,
  "message": "Discount code valid",
  "data": {
    "discount_type": "PERCENTAGE",
    "discount_value": "10.00"
  }
}
```

---

# Admin — Exportar Reportes CSV

## Pedidos

```http
GET /api/v1/admin/export/orders/
```

Params: `?status=`, `?created_from=`, `?created_to=`

Response: `text/csv` con columnas: id, title, customer_phone, status, priority, request_type, payment_status, created_at.

---

## Pagos

```http
GET /api/v1/admin/export/payments/
```

Params: `?status=`, `?created_from=`, `?created_to=`

Response: `text/csv` con columnas: id, order_id, amount, payment_type, payment_method, payment_status, created_at.

---

# Admin — Historial de Pagos del Cliente

```http
GET /api/v1/admin/users/{user_id}/payments/
```

Permiso: `IsAdmin`.

### Response 200

```json
{
  "success": true,
  "message": "Customer payment history retrieved",
  "data": {
    "total_paid": "5250.00",
    "total_orders": 8,
    "average_ticket": "656.25",
    "payments": [...]
  }
}
```

---

# Cotización Exprés (Pública)

## Endpoint

```http
POST /api/v1/quotes/estimate/
```

Permiso: `AllowAny`.

Acepta un archivo STL (multipart), analiza peso/tiempo y retorna estimado de precio sin guardar nada en BD. Límite: 20MB, solo `.stl`.

### Response 200

```json
{
  "success": true,
  "message": "Estimate calculated",
  "data": {
    "weight_grams": "250.00",
    "print_time_hours": "12.50",
    "material_cost": "6.25",
    "energy_cost": "0.00",
    "labor_cost": "187.50",
    "total_price": "506.31"
  }
}
```

---

Fin del documento.
