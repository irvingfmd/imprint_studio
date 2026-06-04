# Imprint Studio

## Sistema de Gestión para Impresión 3D Personalizada

---

# Descripción General

Imprint Studio es una plataforma web diseñada para administrar solicitudes de impresión 3D personalizadas, cotizaciones, producción, pagos, entregas y seguimiento de pedidos.

El sistema está orientado inicialmente a la operación de Imprint Studio en Tuxtla Gutiérrez, Chiapas, pero su arquitectura permite escalar a múltiples operadores o sucursales en el futuro.

---

# Objetivos del Proyecto

## Objetivo Principal

Centralizar y automatizar la operación del negocio de impresión 3D mediante una plataforma web propia.

---

## Objetivos Específicos

* Gestionar clientes.
* Gestionar solicitudes de impresión.
* Gestionar archivos STL, 3MF y OBJ.
* Generar cotizaciones basadas en datos reales.
* Gestionar anticipos y pagos.
* Gestionar producción.
* Gestionar entregas y envíos.
* Automatizar tareas operativas.
* Preparar la arquitectura para futuros agentes de IA.

---

# Filosofía del Proyecto

## Automation First

La automatización basada en reglas de negocio tiene prioridad sobre cualquier integración con inteligencia artificial.

---

## AI Later

La IA es una mejora futura.

El sistema debe funcionar completamente sin depender de:

* ChatGPT
* Claude
* Gemini
* Copilot
* Servicios de terceros basados en IA

---

## Human Approval Required

Las decisiones críticas siempre requieren intervención humana.

Ejemplos:

* Confirmación de pagos.
* Reembolsos.
* Cambios de configuración.
* Aprobación de cotizaciones.
* Entregas.

---

# Alcance del MVP

La primera versión debe permitir:

* Registro de usuarios.
* Autenticación mediante OTP.
* Creación de solicitudes.
* Subida de imágenes.
* Subida de archivos STL.
* Generación de cotizaciones.
* Gestión de pagos.
* Gestión de producción.
* Gestión de entregas.
* Automatizaciones básicas.
* Administración completa mediante panel web.

---

# Stack Tecnológico

## Backend

* Python 3.12+
* Django 5
* Django REST Framework
* SimpleJWT

---

## Frontend

* Vue 3
* Vite
* Pinia
* Vue Router
* Axios
* Tailwind CSS

---

## Base de Datos

### Desarrollo

```text
SQLite
```

### Producción

```text
PostgreSQL
```

---

## Almacenamiento de Archivos

Opciones soportadas:

* Cloudinary
* Supabase Storage

---

## Notificaciones

### Producción

* WhatsApp Business Cloud API
* Brevo SMTP

### Desarrollo

* Consola de Django
* SMTP local

---

# Arquitectura General

```text
Frontend (Vue 3)
        ↓
REST API
        ↓
Backend (Django)
        ↓
PostgreSQL
        ↓
Storage Provider
```

---

# Convenciones de Desarrollo

## Código

Todo el código debe escribirse en inglés.

---

## Variables

Siempre en inglés.

Ejemplo:

```python
material_cost
```

---

## Funciones

Siempre en inglés.

Ejemplo:

```python
calculate_quote()
```

---

## Métodos

Siempre en inglés.

Ejemplo:

```python
confirm_payment()
```

---

## Clases

Siempre en inglés.

Ejemplo:

```python
OrderService
```

---

## Tablas

Siempre en inglés.

Ejemplo:

```text
shipping_addresses
```

---

## Endpoints

Siempre en inglés.

Ejemplo:

```http
POST /api/v1/orders/
```

---

## Comentarios

Todos los comentarios deben escribirse en español mexicano.

Ejemplo:

```python
# Calcula el costo total considerando material,
# energía, mano de obra y margen de ganancia.
```

---

## Type Hints

Obligatorios en todo el backend.

Ejemplo:

```python
def calculate_price(
    weight_grams: Decimal,
    print_time_hours: Decimal
) -> Decimal:
```

---

# Estructura de Documentación

```text
docs/
│
├── README.md
│
├── 01-business-rules.md
├── 02-system-architecture.md
├── 03-database-design.md
├── 04-api-specification.md
├── 05-cost-calculator.md
├── 06-payments-and-refunds.md
├── 07-testing-plan.md
├── 08-ai-roadmap.md
└── 09-deployment.md
```

---

# Documentación

## 01 Business Rules

Define:

* Reglas de negocio.
* Estados.
* Prioridades.
* Flujos operativos.

---

## 02 System Architecture

Define:

* Arquitectura general.
* Servicios.
* Capas.
* Dependencias.

---

## 03 Database Design

Define:

* Modelo de datos.
* Relaciones.
* Índices.
* Restricciones.

---

## 04 API Specification

Define:

* Endpoints.
* Requests.
* Responses.
* Autenticación.

---

## 05 Cost Calculator

Define:

* Fórmulas oficiales.
* Variables configurables.
* Reglas de cálculo.

---

## 06 Payments and Refunds

Define:

* Anticipos.
* Pagos.
* Reembolsos.
* Entregas.

---

## 07 Testing Plan

Define:

* Casos de prueba.
* QA.
* Criterios de aceptación.

---

## 08 AI Roadmap

Define:

* Preparación para IA.
* Fases futuras.
* Restricciones.

---

## 09 Deployment

Define:

* Infraestructura.
* Variables de entorno.
* Producción.
* Seguridad.

---

# Principios de Base de Datos

## Nombres

Todos los nombres utilizan:

```text
snake_case
```

---

## Idioma

Todo el esquema utiliza inglés.

---

## Ejemplo

Correcto:

```text
shipping_addresses
```

Incorrecto:

```text
direcciones_envio
```

---

# Decisión Arquitectónica Importante

Las direcciones de envío NO se almacenan directamente dentro de la tabla:

```text
orders
```

Se almacenan en:

```text
shipping_addresses
```

Esto permite:

* Historial de direcciones.
* Escalabilidad.
* Mejor normalización.
* Menor cantidad de campos nulos.

---

# Zona Horaria

Todo el sistema debe utilizar:

```text
America/Mexico_City
```

---

# Moneda

```text
MXN
```

---

# Formato Telefónico

Todos los números deben almacenarse utilizando:

```text
E.164
```

Ejemplo:

```text
+5219611234567
```

---

# Estado Actual del Proyecto

```text
Planning / Architecture Phase
```

---

# Estado de IA

```text
Disabled
```

La inteligencia artificial únicamente se encuentra contemplada a nivel de arquitectura y modelo de datos.

No forma parte del MVP.

---

# Objetivo Final

Construir una plataforma robusta, mantenible y escalable que permita operar un negocio de impresión 3D sin depender de herramientas externas, manteniendo control total sobre los procesos de cotización, producción, pagos y entregas.
