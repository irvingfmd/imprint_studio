# Payments and Refunds

## Imprint Studio

Versión: 2.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define las reglas oficiales relacionadas con:

* Pagos
* Anticipos
* Pagos finales
* Pagos completos
* Confirmaciones
* Reembolsos
* Comprobantes
* Vencimientos
* Cancelaciones

Este documento es la fuente oficial para implementar:

* PaymentService
* RefundService
* PaymentValidationService
* PaymentExpirationService
* Cron Jobs de pagos
* Endpoints administrativos de pagos

---

# Filosofía del Sistema

Imprint Studio trabaja bajo un modelo de fabricación bajo pedido.

Cada impresión es producida específicamente para un cliente.

Por esta razón existen reglas estrictas sobre:

* Anticipos
* Cancelaciones
* Reembolsos

---

# Modalidades de Pago

## Opción 1

### Anticipo + Saldo

```text
50% al aprobar la cotización

50% al entregar
```

---

## Opción 2

### Pago Completo

```text
100% al aprobar la cotización
```

---

## Beneficio

El cliente recibe:

```text
5% de descuento
```

configurable desde:

```text
business_config
```

Campo:

```text
full_payment_discount_percentage
```

---

# Flujo General

```text
Cliente acepta cotización
            ↓
Selecciona modalidad de pago
            ↓
Sistema genera obligación financiera
            ↓
Cliente realiza pago
            ↓
Cliente sube comprobante (opcional)
            ↓
Administrador confirma pago
            ↓
Sistema actualiza estado financiero
            ↓
Producción continúa
```

---

# Estados de Pago

## NO_PAYMENT

Todavía no existe pago registrado.

---

## DEPOSIT_PENDING

Se requiere anticipo.

---

## DEPOSIT_PAID

Anticipo confirmado.

---

## BALANCE_PENDING

Se requiere pago restante.

---

## FULLY_PAID

Pedido completamente liquidado.

---

## REFUNDED

Pedido reembolsado.

---

# Tabla Payments

Todos los movimientos financieros deben registrarse en:

```text
payments
```

---

# Payment Types

## DEPOSIT

Anticipo inicial.

---

## BALANCE

Pago restante.

---

## FULL_PAYMENT

Pago total.

---

## REFUND

Reembolso.

---

# Payment Methods

## BANK_TRANSFER

Transferencia bancaria.

---

## CASH

Pago en efectivo.

---

# Payment Status

## PENDING

Esperando validación.

---

## CONFIRMED

Confirmado por administrador.

---

## REJECTED

Rechazado.

---

# Datos Bancarios

Los datos bancarios se almacenan en:

```text
payment_instructions
```

---

## Campos

```text
bank_name

account_holder

account_number

clabe

card_number

additional_notes
```

---

# Obtención de Datos Bancarios

Endpoint:

```http
GET /api/v1/payment-instructions/
```

---

# Confirmación de Pagos

Los pagos nunca deben confirmarse automáticamente durante el MVP.

---

## Regla

Toda confirmación debe realizarla un administrador.

---

# Métodos de Confirmación

## Método 1

Comprobante cargado en plataforma.

---

## Método 2

Confirmación manual.

Ejemplo:

```text
Cliente envía comprobante por WhatsApp.
```

---

# Confirmación Manual

Campo:

```text
manual_confirmation
```

Valor:

```text
true
```

---

# Endpoint

```http
POST /api/v1/admin/orders/{order_id}/payments/manual-confirmation/
```

---

# Comprobantes de Pago

## Formatos Permitidos

```text
JPG

JPEG

PNG

PDF
```

---

# Tamaño Máximo

Recomendado:

```text
10 MB
```

---

# Almacenamiento

Los comprobantes deben almacenarse en:

```text
Cloudinary

o

Supabase Storage
```

---

# Endpoint

```http
POST /api/v1/payments/{payment_id}/proof/
```

---

# Flujo de Anticipo

## Paso 1

Cliente acepta cotización.

---

## Paso 2

Sistema genera obligación:

```text
DEPOSIT_PENDING
```

---

## Paso 3

Cliente realiza transferencia.

---

## Paso 4

Cliente carga comprobante.

---

## Paso 5

Administrador confirma.

---

## Resultado

Estado:

```text
DEPOSIT_PAID
```

---

# Flujo de Pago Completo

## Paso 1

Cliente acepta cotización.

---

## Paso 2

Selecciona:

```text
FULL_PAYMENT
```

---

## Paso 3

Sistema aplica descuento.

---

## Paso 4

Cliente realiza pago.

---

## Paso 5

Administrador confirma.

---

## Resultado

Estado:

```text
FULLY_PAID
```

---

# Flujo de Saldo Final

## Paso 1

Producción finaliza.

---

Estado:

```text
READY
```

---

## Paso 2

Sistema verifica:

```text
¿Existe saldo pendiente?
```

---

## Si existe

Estado:

```text
PENDING_BALANCE
```

---

## Paso 3

Cliente realiza pago.

---

## Paso 4

Administrador confirma.

---

## Resultado

Estado:

```text
FULLY_PAID
```

---

# Pago Contra Entrega

Permitido únicamente cuando:

```text
delivery_method = PICKUP
```

o

```text
delivery_method = SHIPPING_LOCAL
```

---

## Flujo

```text
Pedido listo
↓
Cliente acude
↓
Paga efectivo
↓
Administrador confirma
↓
FULLY_PAID
↓
DELIVERED
```

---

# Vencimiento de Anticipos

Configuración:

```text
deposit_deadline_hours
```

---

## Valor Inicial

```text
72
```

horas.

---

# Regla

Si el anticipo no se confirma dentro del plazo:

```text
PENDING_DEPOSIT
```

↓

```text
CANCELLED
```

---

# Cron Job

Frecuencia:

```text
Cada hora
```

---

# Acción

Buscar pedidos:

```text
PENDING_DEPOSIT
```

con más de:

```text
72 horas
```

---

# Resultado

Cancelar automáticamente.

---

# Evento Generado

```text
ORDER_CANCELLED
```

---

# Vencimiento de Saldo

Configuración:

```text
balance_deadline_days
```

---

## Valor Inicial

```text
7
```

días.

---

# Regla

Si el cliente no liquida el saldo:

```text
PENDING_BALANCE
```

después del plazo:

El administrador será notificado.

---

## Importante

No cancelar automáticamente.

Debe existir intervención humana.

---

# Política de Reembolsos

La política depende de la etapa de producción.

---

# Antes de Laminar

## Reembolso

```text
100%
```

---

## Justificación

No existe inversión significativa.

---

# Después de Laminar

## Reembolso

```text
70%
```

---

## Justificación

Existe tiempo invertido.

---

# Durante Impresión

## Reembolso

```text
0%
```

---

## Justificación

Ya existe consumo de material.

---

# Pedido Terminado

Estados:

```text
READY

PENDING_BALANCE

FULLY_PAID

DELIVERED
```

---

## Reembolso

```text
0%
```

---

## Justificación

El producto ya fue fabricado.

---

# Cancelación por Falta de Anticipo

## Reembolso

```text
100%
```

---

## Justificación

No inició producción.

---

# Tabla de Reembolsos

| Etapa                  | Reembolso |
| ---------------------- | --------- |
| Antes de laminar       | 100%      |
| Después de laminar     | 70%       |
| Durante impresión      | 0%        |
| Pedido terminado       | 0%        |
| Cancelación automática | 100%      |

---

# Flujo de Reembolso

## Paso 1

Cliente solicita cancelación.

---

## Paso 2

Administrador revisa etapa.

---

## Paso 3

Sistema sugiere porcentaje.

---

## Paso 4

Administrador puede modificar.

---

## Paso 5

Administrador realiza transferencia fuera del sistema.

---

## Paso 6

Registrar reembolso.

---

# Endpoint

```http
POST /api/v1/admin/orders/{order_id}/refund/
```

---

# Request

```json
{
  "amount": 500.00,
  "reason": "Cancelación antes de impresión."
}
```

---

# Resultado

Crear registro:

```text
payment_type = REFUND
```

---

# Evento Generado

```text
REFUND_PROCESSED
```

---

# Auditoría

Toda operación financiera debe generar:

```text
order_events
```

---

# Eventos Obligatorios

```text
PAYMENT_PROOF_UPLOADED

PAYMENT_CONFIRMED

PAYMENT_REJECTED

DEPOSIT_CONFIRMED

BALANCE_CONFIRMED

FULL_PAYMENT_CONFIRMED

REFUND_REQUESTED

REFUND_PROCESSED
```

---

# Restricciones

## Nunca eliminar pagos

Los pagos son registros históricos.

---

## Nunca modificar montos confirmados

Se debe crear un nuevo movimiento.

---

## Nunca eliminar reembolsos

Deben permanecer auditables.

---

# Validaciones

## amount

Debe ser mayor que:

```text
0
```

---

## payment_type

Debe existir.

---

## payment_method

Debe existir.

---

## payment_status

Debe existir.

---

# Pruebas Requeridas

* Confirmación de anticipo.
* Confirmación de saldo.
* Confirmación de pago completo.
* Confirmación manual.
* Subida de comprobante.
* Rechazo de pago.
* Reembolso 100%.
* Reembolso 70%.
* Reembolso 0%.
* Cancelación automática.
* Expiración de anticipo.
* Notificación de saldo pendiente.

---

# Integración Futura con IA

La IA podrá:

* Detectar comprobantes duplicados.
* Detectar pagos sospechosos.
* Sugerir validaciones.

---

# Restricción

La IA nunca podrá:

* Confirmar pagos.
* Autorizar reembolsos.
* Modificar montos.

---

# Objetivo

Garantizar que todos los movimientos financieros de Imprint Studio sean:

* Auditables.
* Seguros.
* Reproducibles.
* Transparentes.
* Compatibles con futuras automatizaciones.

---

# Estado del Documento

Versión: 2.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* PaymentService
* RefundService
* Cron Jobs Financieros
* Administración
* Auditoría

Fin del documento.
