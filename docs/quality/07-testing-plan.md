# Testing Plan

## Imprint Studio

Versión: 2.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define el plan oficial de pruebas para Imprint Studio.

Su objetivo es garantizar que el sistema funcione correctamente antes de ser utilizado por clientes reales.

Este documento será utilizado por:

* Desarrollo Backend
* Desarrollo Frontend
* QA
* Pruebas Manuales
* Pruebas Automatizadas
* Futuras validaciones de IA

---

# Objetivos de Prueba

Validar:

* Funcionalidad
* Seguridad
* Integridad de datos
* Flujo de negocio
* API
* UI/UX
* Base de datos
* Pagos
* Cotizaciones
* Producción
* Auditoría

---

# Alcance

## Incluido

* Backend Django
* Frontend Vue
* PostgreSQL
* JWT
* OTP
* Cotizaciones
* Pagos
* Reembolsos
* Envíos
* Dashboard
* Configuración administrativa

---

## Excluido

* IA
* Integraciones futuras
* Aplicación móvil

---

# Entorno de Pruebas

## Backend

```bash
cd backend

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## URLs

Backend:

```text
http://localhost:8000
```

---

Frontend:

```text
http://localhost:5173
```

---

Admin:

```text
http://localhost:8000/admin
```

---

# Datos Iniciales Requeridos

Antes de comenzar pruebas:

* Crear usuario administrador.
* Configurar business_config.
* Configurar payment_instructions.
* Configurar business_hours.
* Configurar holidays.

---

# Fase 1

# Authentication Testing

---

## Caso 1

### Registro Correcto

#### Acción

Registrar usuario válido.

#### Resultado Esperado

```text
201 Created
```

Usuario almacenado.

---

## Caso 2

### Teléfono Duplicado

#### Acción

Registrar teléfono existente.

#### Resultado Esperado

```text
400 Bad Request
```

---

## Caso 3

### Email Duplicado

#### Acción

Registrar email existente.

#### Resultado Esperado

```text
400 Bad Request
```

---

## Caso 4

### Envío OTP

#### Acción

Solicitar OTP.

#### Resultado Esperado

OTP generado.

---

## Caso 5

### OTP Correcto

#### Acción

Verificar código válido.

#### Resultado Esperado

JWT generado.

---

## Caso 6

### OTP Incorrecto

#### Acción

Código inválido.

#### Resultado Esperado

```text
401 Unauthorized
```

---

## Caso 7

### Refresh Token

#### Acción

Solicitar nuevo access token.

#### Resultado Esperado

Nuevo token válido.

---

# Fase 2

# Orders Testing

---

## Caso 8

### Crear Solicitud Tipo A

#### Acción

Crear pedido REFERENCE.

#### Resultado Esperado

Estado:

```text
RECEIVED
```

---

## Caso 9

### Crear Solicitud Tipo B

#### Acción

Crear pedido PRINTABLE_FILE.

#### Resultado Esperado

Estado:

```text
PENDING_ANALYSIS
```

---

## Caso 10

### Cantidad Inválida

#### Acción

quantity = 0

#### Resultado Esperado

Error de validación.

---

## Caso 11

### Prioridad Inválida

#### Acción

Enviar valor inexistente.

#### Resultado Esperado

Error de validación.

---

## Caso 12

### Consultar Pedido

#### Acción

GET order.

#### Resultado Esperado

Información completa.

---

## Caso 13

### Cancelar Pedido

#### Acción

Cliente solicita cancelación.

#### Resultado Esperado

Estado actualizado.

---

# Fase 3

# Files Testing

---

## Caso 14

### Subir Imagen

#### Acción

JPG válido.

#### Resultado Esperado

Archivo almacenado.

---

## Caso 15

### Subir STL

#### Acción

STL válido.

#### Resultado Esperado

Archivo almacenado.

---

## Caso 16

### Subir PDF

#### Acción

Comprobante PDF.

#### Resultado Esperado

Archivo almacenado.

---

## Caso 17

### Archivo No Permitido

#### Acción

EXE.

#### Resultado Esperado

Error.

---

## Caso 18

### Archivo Excesivamente Grande

#### Acción

Archivo > límite.

#### Resultado Esperado

Error.

---

# Fase 4

# Quotes Testing

---

## Caso 19

### Crear Cotización

#### Acción

Admin genera cotización.

#### Resultado Esperado

Registro en:

```text
quotes
```

---

## Caso 20

### Snapshot Creado

#### Acción

Generar cotización.

#### Resultado Esperado

Registro en:

```text
quote_snapshots
```

---

## Caso 21

### Evento Creado

#### Acción

Generar cotización.

#### Resultado Esperado

Evento:

```text
QUOTE_CREATED
```

---

## Caso 22

### Cliente Acepta Cotización

#### Acción

Aceptar.

#### Resultado Esperado

Estado:

```text
PENDING_DEPOSIT
```

o

```text
FULLY_PAID
```

---

## Caso 23

### Cliente Rechaza Cotización

#### Acción

Rechazar.

#### Resultado Esperado

Estado correspondiente.

---

# Fase 5

# Cost Calculator Testing

---

## Caso 24

### Cálculo Normal

Resultado correcto.

---

## Caso 25

### Cálculo Urgente

Multiplicador correcto.

---

## Caso 26

### Cálculo Express

Multiplicador correcto.

---

## Caso 27

### Descuento Pago Completo

5% aplicado correctamente.

---

## Caso 28

### Peso Inválido

Error.

---

## Caso 29

### Tiempo Inválido

Error.

---

## Caso 30

### Redondeo

2 decimales.

---

## Caso 31

### Uso de Decimal

Validar precisión.

---

# Fase 6

# Payments Testing

---

## Caso 32

### Subir Comprobante

Resultado esperado:

Archivo almacenado.

---

## Caso 33

### Confirmar Anticipo

Resultado:

```text
DEPOSIT_PAID
```

---

## Caso 34

### Confirmar Saldo

Resultado:

```text
FULLY_PAID
```

---

## Caso 35

### Confirmación Manual

Resultado:

```text
manual_confirmation = true
```

---

## Caso 36

### Rechazar Pago

Resultado:

```text
REJECTED
```

---

## Caso 37

### Evento de Pago

Evento:

```text
PAYMENT_CONFIRMED
```

---

# Fase 7

# Refund Testing

---

## Caso 38

### Reembolso 100%

Antes de laminar.

---

## Caso 39

### Reembolso 70%

Después de laminar.

---

## Caso 40

### Reembolso 0%

Durante impresión.

---

## Caso 41

### Registro Financiero

Crear:

```text
REFUND
```

---

## Caso 42

### Evento

Generar:

```text
REFUND_PROCESSED
```

---

# Fase 8

# Production Testing

---

## Caso 43

### PRINTING

Cambio válido.

---

## Caso 44

### POST_PROCESSING

Cambio válido.

---

## Caso 45

### READY

Cambio válido.

---

## Caso 46

### DELIVERED

Cambio válido.

---

## Caso 47

### Historial

Registro en:

```text
production_history
```

---

# Fase 9

# Shipping Testing

---

## Caso 48

### Crear Dirección

Resultado esperado.

---

## Caso 49

### Actualizar Dirección

Resultado esperado.

---

## Caso 50

### Crear Envío

Resultado esperado.

---

## Caso 51

### Marcar Entregado

Resultado esperado.

---

# Fase 10

# Events Testing

---

## Caso 52

### ORDER_CREATED

Evento generado.

---

## Caso 53

### FILE_UPLOADED

Evento generado.

---

## Caso 54

### QUOTE_CREATED

Evento generado.

---

## Caso 55

### PAYMENT_CONFIRMED

Evento generado.

---

## Caso 56

### ORDER_DELIVERED

Evento generado.

---

## Caso 57

### REFUND_PROCESSED

Evento generado.

---

# Fase 11

# Security Testing

---

## Caso 58

### Sin JWT

Resultado:

```text
401
```

---

## Caso 59

### JWT Inválido

Resultado:

```text
401
```

---

## Caso 60

### Cliente Accede a Pedido Ajeno

Resultado:

```text
403
```

---

## Caso 61

### Cliente Accede a Admin

Resultado:

```text
403
```

---

## Caso 62

### SQL Injection

Resultado:

Bloqueado.

---

## Caso 63

### XSS

Resultado:

Bloqueado.

---

## Caso 64

### Rate Limit OTP

Resultado:

```text
429
```

---

# Fase 12

# Database Testing

---

## Caso 65

### Migraciones Limpias

```bash
python manage.py makemigrations
```

Resultado:

```text
No changes detected
```

---

## Caso 66

### Foreign Keys

Validar integridad.

---

## Caso 67

### Índices

Validar rendimiento.

---

## Caso 68

### Soft Delete

Validar comportamiento.

---

# Fase 13

# UI Testing

---

## Caso 69

### Responsive Mobile

Correcto.

---

## Caso 70

### Responsive Tablet

Correcto.

---

## Caso 71

### Responsive Desktop

Correcto.

---

## Caso 72

### Formularios

Validación inline.

---

## Caso 73

### Loading States

Spinner visible.

---

## Caso 74

### Mensajes de Error

Claridad adecuada.

---

# Fase 14

# Performance Testing

---

## Caso 75

### Listado de Pedidos

100 registros.

---

## Caso 76

### Listado de Eventos

1000 registros.

---

## Caso 77

### Dashboard

Respuesta < 2 segundos.

---

# Cobertura Mínima

## Backend

```text
80%
```

---

## Services

```text
90%
```

---

## Cost Calculator

```text
100%
```

---

# Checklist MVP

Antes de liberar:

* Registro funciona.
* OTP funciona.
* JWT funciona.
* Crear pedidos funciona.
* Subir archivos funciona.
* Crear cotizaciones funciona.
* Calculadora funciona.
* Pagos funcionan.
* Reembolsos funcionan.
* Producción funciona.
* Envíos funcionan.
* Dashboard funciona.
* Eventos funcionan.
* Auditoría funciona.

---

# Criterio de Aprobación

El MVP se considera aprobado cuando:

* Todas las pruebas críticas pasan.
* No existen errores bloqueantes.
* No existen errores de seguridad.
* La calculadora produce resultados correctos.
* Los flujos de negocio funcionan de extremo a extremo.

---

# Objetivo

Garantizar que Imprint Studio pueda operar con clientes reales de forma segura, estable y predecible.

---

# Estado del Documento

Versión: 2.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* QA
* Testing Manual
* Testing Automatizado
* Validación Pre-Lanzamiento
* CI/CD futuro

Fin del documento.
