# System Architecture

## Imprint Studio

Versión: 1.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define la arquitectura oficial del sistema Imprint Studio.

Establece:

* Estructura general del sistema.
* Capas de aplicación.
* Responsabilidades de cada módulo.
* Flujo de datos.
* Principios arquitectónicos.
* Convenciones de implementación.

Toda nueva funcionalidad deberá respetar la arquitectura definida en este documento.

---

# Objetivos Arquitectónicos

La arquitectura debe cumplir los siguientes objetivos:

* Simplicidad.
* Escalabilidad.
* Mantenibilidad.
* Seguridad.
* Modularidad.
* Facilidad de pruebas.
* Preparación para futuras integraciones de IA.

---

# Principios Fundamentales

## Automation First

La automatización mediante reglas de negocio tiene prioridad sobre cualquier integración de inteligencia artificial.

---

## AI Later

La arquitectura debe estar preparada para IA futura.

Sin embargo, el MVP debe funcionar completamente sin IA.

---

## Human Approval Required

Las decisiones financieras y operativas críticas siempre requieren validación humana.

---

## Separation of Concerns

Cada módulo debe tener una única responsabilidad claramente definida.

---

## Single Source of Truth

Toda la información debe tener una única fuente oficial.

Ejemplos:

### Costos

Fuente oficial:

```text
Bambu Studio
```

---

### Usuarios

Fuente oficial:

```text
users
```

---

### Cotizaciones

Fuente oficial:

```text
quotes
```

---

# Arquitectura General

```text
┌─────────────────────┐
│     Vue Frontend    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      REST API       │
│ Django REST Framework │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Django Core     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    PostgreSQL DB    │
└─────────────────────┘
```

---

# Capas del Sistema

---

# Frontend Layer

Responsable de:

* Interfaz de usuario.
* Navegación.
* Validaciones visuales.
* Consumo de API.
* Manejo de estado.

---

## Tecnología

```text
Vue 3
Vite
Pinia
Vue Router
Axios
Tailwind CSS
```

---

# API Layer

Responsable de:

* Exponer endpoints.
* Validar requests.
* Autorización.
* Serialización.

---

## Tecnología

```text
Django REST Framework
```

---

# Business Layer

Responsable de:

* Reglas de negocio.
* Validaciones.
* Procesos.
* Automatizaciones.

---

Esta capa NO debe vivir dentro de los views.

---

Correcto:

```text
views
↓
services
↓
repositories
```

---

Incorrecto:

```text
views
↓
1000 líneas de lógica
```

---

# Persistence Layer

Responsable de:

* Acceso a datos.
* Consultas.
* Escritura.
* Lectura.

---

## Tecnología

```text
PostgreSQL
```

---

# Storage Layer

Responsable de:

* Imágenes.
* STL.
* OBJ.
* 3MF.
* Comprobantes.

---

## Proveedores Soportados

```text
Cloudinary
Supabase Storage
```

---

# Notification Layer

Responsable de:

* WhatsApp.
* Correo electrónico.
* Recordatorios.

---

## Canales

### Producción

```text
WhatsApp Business Cloud API
Brevo SMTP
```

---

### Desarrollo

```text
Console Backend
Local SMTP
```

---

# Módulos Principales

---

# Authentication Module

Responsabilidades:

* Registro.
* OTP.
* JWT.
* Sesiones.

---

## Entidades

```text
users
otp_codes
```

---

# Orders Module

Responsabilidades:

* Solicitudes.
* Archivos.
* Estados.

---

## Entidades

```text
orders
request_files
```

---

# Quotes Module

Responsabilidades:

* Cotizaciones.
* Costos.
* Aprobaciones.

---

## Entidades

```text
quotes
```

---

# Payments Module

Responsabilidades:

* Anticipos.
* Pagos.
* Confirmaciones.
* Reembolsos.

---

## Entidades

```text
payments
```

---

# Production Module

Responsabilidades:

* Producción.
* Seguimiento.
* Historial.

---

## Entidades

```text
production_history
```

---

# Shipping Module

Responsabilidades:

* Direcciones.
* Envíos.
* Entregas.

---

## Entidades

```text
shipping_addresses
shipments
```

---

# Configuration Module

Responsabilidades:

* Costos.
* Horarios.
* Festivos.
* Configuración general.

---

## Entidades

```text
business_config
business_hours
holidays
payment_instructions
```

---

# Estructura Backend

## Organización Principal

```text
backend/
│
├── apps/
│
│   ├── authentication/
│   ├── orders/
│   ├── quotes/
│   ├── payments/
│   ├── production/
│   ├── shipping/
│   ├── notifications/
│   └── configuration/
│
├── core/
├── config/
└── manage.py
```

---

# Estructura de un Módulo

Ejemplo:

```text
orders/
│
├── models/
├── serializers/
├── services/
├── selectors/
├── api/
├── tests/
├── admin/
└── migrations/
```

---

# Responsabilidades por Carpeta

## models

Define entidades.

---

## serializers

Valida y serializa datos.

---

## services

Contiene lógica de negocio.

---

## selectors

Consultas complejas.

Solo lectura.

---

## api

Views y endpoints.

---

## tests

Pruebas.

---

# Estructura Frontend

```text
frontend/
│
├── src/
│
├── modules/
│   ├── auth/
│   ├── orders/
│   ├── quotes/
│   ├── payments/
│   └── admin/
│
├── router/
├── stores/
├── layouts/
├── components/
├── services/
└── utils/
```

---

# Estado Global

Tecnología:

```text
Pinia
```

---

## Permitido en Store

* Usuario autenticado.
* JWT.
* Configuración global.

---

## No Permitido

Guardar formularios enormes o lógica de negocio.

---

# Convenciones de Código

## Idioma

Todo el código debe escribirse en inglés.

---

## Variables

Correcto:

```python
material_cost
```

Incorrecto:

```python
costo_material
```

---

## Funciones

Correcto:

```python
calculate_quote()
```

Incorrecto:

```python
calcular_cotizacion()
```

---

## Clases

Correcto:

```python
QuoteCalculatorService
```

Incorrecto:

```python
CalculadoraCotizacion
```

---

# Comentarios

Todos los comentarios deben escribirse en español mexicano.

---

Ejemplo:

```python
# Calcula el costo total basado en el peso y tiempo reales.
```

---

# Type Hints

Obligatorios.

---

Ejemplo:

```python
def calculate_quote(
    weight_grams: Decimal,
    print_time_hours: Decimal
) -> Decimal:
```

---

# Flujo de Datos

## Creación de Pedido

```text
Frontend
↓
API
↓
Order Service
↓
Database
↓
Response
```

---

## Generación de Cotización

```text
Admin
↓
Quote Service
↓
Cost Calculator
↓
Database
↓
Cliente
```

---

# Automatizaciones

Las tareas automáticas deben ejecutarse fuera del request principal.

---

## MVP

Tecnología:

```text
django-cron
```

---

## Escalamiento

Tecnología:

```text
Celery + Redis
```

---

# Seguridad

---

# Autenticación

```text
JWT
```

---

# Contraseñas

Hash obligatorio.

---

## Algoritmo

Configuración por defecto de Django.

---

# Rate Limiting

Obligatorio para:

* OTP
* Login
* Endpoints públicos

---

# CORS

Restringido.

---

# Secrets

Nunca almacenar:

```text
SECRET_KEY
API_KEYS
TOKENS
PASSWORDS
```

en el repositorio.

---

# Variables de Entorno

Uso obligatorio de:

```text
.env
```

---

# Preparación para IA

La arquitectura contempla futuras integraciones.

---

## Campos Reservados

```text
ai_analysis
ai_notes
ai_confidence
ai_category
```

---

## Futuras Capas

```text
AI Classification Service

AI Quote Recommendation Service

AI Production Optimization Service
```

---

# Restricción MVP

Todos los módulos de IA deben permanecer deshabilitados.

---

# Escalabilidad

## Fase 1

```text
Monolito Django
```

---

## Fase 2

```text
Django + Celery
```

---

## Fase 3

```text
Servicios desacoplados
```

---

# Objetivo Arquitectónico

Construir una plataforma modular, mantenible y escalable que permita gestionar completamente la operación de Imprint Studio mediante reglas de negocio claras, automatización controlada y una arquitectura preparada para evolucionar sin requerir rediseños importantes.
