# Coding Standards

## Imprint Studio

Versión: 1.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define los estándares oficiales de desarrollo para Imprint Studio.

Debe ser respetado por:

* Desarrolladores humanos.
* Claude Code.
* GitHub Copilot.
* Cursor.
* Continue.dev.
* Cualquier agente de IA utilizado durante el desarrollo.

El objetivo es mantener el código consistente, legible, mantenible y fácil de escalar.

---

# Regla Principal de Idioma

## Código

Todo el código debe escribirse en inglés.

Esto incluye:

* Variables
* Constantes
* Funciones
* Métodos
* Clases
* Interfaces
* Enums
* DTOs
* Serializers
* Models
* Services
* Selectors
* Repositories
* Stores
* Composables
* Componentes
* Archivos
* Carpetas
* Endpoints
* Tablas
* Columnas

---

## Comentarios

Todos los comentarios deben escribirse en español mexicano.

---

## Documentación

Toda la documentación técnica debe escribirse en español mexicano.

---

# Ejemplo Correcto

```python
def calculate_quote_price(
    weight_grams: Decimal,
    print_time_hours: Decimal,
) -> Decimal:
    """
    Calcula el precio de una cotización usando
    el peso y tiempo reales de impresión.
    """
    pass
```

---

# Ejemplo Incorrecto

```python
def calcular_precio_cotizacion(
    peso_gramos,
    tiempo_horas,
):
    """
    Calculate price.
    """
    pass
```

---

# Naming Conventions

## Python

Usar:

```text
snake_case
```

para:

* Variables
* Funciones
* Métodos
* Archivos

---

## Python Classes

Usar:

```text
PascalCase
```

para:

* Clases
* Services
* Exceptions
* TextChoices

---

## Python Constants

Usar:

```text
UPPER_SNAKE_CASE
```

---

## TypeScript / JavaScript

Usar:

```text
camelCase
```

para:

* Variables
* Funciones
* Métodos

---

## Vue Components

Usar:

```text
PascalCase
```

Ejemplo:

```text
OrderCard.vue
PaymentStatusBadge.vue
```

---

## Database

Usar:

```text
snake_case
```

Ejemplo:

```text
shipping_addresses
payment_instructions
created_at
```

---

## API URLs

Usar:

```text
kebab-case
```

Ejemplo:

```http
/api/v1/shipping-addresses/
```

---

# Backend Standards

## Framework

Backend oficial:

```text
Django 5
```

---

## API

API oficial:

```text
Django REST Framework
```

---

## Lenguaje

```text
Python 3.12+
```

---

# Type Hints

Los type hints son obligatorios en servicios, utilidades y lógica de negocio.

---

## Correcto

```python
def calculate_total_price(
    subtotal: Decimal,
    profit_margin_percentage: Decimal,
) -> Decimal:
    """
    Calcula el precio total aplicando margen de ganancia.
    """
    return subtotal * (
        Decimal("1")
        + profit_margin_percentage / Decimal("100")
    )
```

---

## Incorrecto

```python
def calculate_total_price(subtotal, margin):
    return subtotal * margin
```

---

# Decimal

Toda operación financiera debe usar:

```python
Decimal
```

---

## Prohibido

```python
float
```

para precios, costos, pagos, reembolsos o porcentajes financieros.

---

# Redondeo Monetario

Usar:

```python
ROUND_HALF_UP
```

---

## Ejemplo

```python
def round_money(value: Decimal) -> Decimal:
    """
    Redondea importes monetarios a dos decimales.
    """
    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
```

---

# Django Apps

## Estructura Recomendada

```text
backend/
│
├── apps/
│   ├── authentication/
│   ├── orders/
│   ├── quotes/
│   ├── payments/
│   ├── shipping/
│   ├── production/
│   ├── notifications/
│   └── configuration/
│
├── core/
├── config/
└── manage.py
```

---

# Estructura Interna de App

```text
orders/
│
├── models.py
├── serializers.py
├── views.py
├── services.py
├── selectors.py
├── permissions.py
├── urls.py
├── admin.py
├── tests/
└── migrations/
```

---

# Services

Toda lógica de negocio debe vivir en services.

---

## Correcto

```python
class OrderStatusTransitionService:
    """
    Valida y ejecuta cambios de estado de pedidos.
    """

    def transition(
        self,
        order: Order,
        new_status: str,
        changed_by: User,
    ) -> Order:
        pass
```

---

## Incorrecto

```python
class OrderViewSet(ModelViewSet):

    def update_status(self, request):
        # Toda la lógica aquí está mal.
        pass
```

---

# Selectors

Los selectors deben usarse para consultas complejas de lectura.

---

## Ejemplo

```python
def get_customer_orders(
    customer: User,
) -> QuerySet[Order]:
    """
    Obtiene los pedidos visibles para un cliente.
    """
    return Order.objects.filter(
        customer=customer,
        is_deleted=False,
    )
```

---

# Views

Las views deben ser delgadas.

Solo deben:

* Recibir request.
* Validar serializer.
* Llamar service.
* Devolver response.

---

# Prohibido en Views

* Cálculos financieros.
* Reglas de negocio complejas.
* Transiciones de estado.
* Confirmaciones de pago.
* Validaciones repetidas.
* Queries complejas.

---

# Serializers

Los serializers deben encargarse de:

* Validación de entrada.
* Serialización de salida.
* Validaciones simples.

---

# Models

Los models deben contener:

* Campos.
* Relaciones.
* Constraints.
* Métodos simples.

---

# Prohibido en Models

Evitar fat models.

No colocar lógica compleja en models.

---

# TextChoices

Todas las enumeraciones deben implementarse con:

```python
models.TextChoices
```

---

## Ejemplo

```python
class OrderStatus(models.TextChoices):
    RECEIVED = "RECEIVED", "Received"
    PRINTING = "PRINTING", "Printing"
    DELIVERED = "DELIVERED", "Delivered"
```

---

# Logging

Usar logging estándar de Python.

---

## Correcto

```python
logger.info(
    "Order status updated",
    extra={
        "order_id": str(order.id),
        "new_status": new_status,
    },
)
```

---

# Prohibido

```python
print("debug")
```

en producción.

---

# Frontend Standards

## Framework

```text
Vue 3
```

---

## Build Tool

```text
Vite
```

---

## State Management

```text
Pinia
```

---

## Styling

```text
Tailwind CSS
```

---

# Estructura Frontend Recomendada

```text
frontend/
│
├── src/
│   ├── modules/
│   │   ├── auth/
│   │   ├── orders/
│   │   ├── quotes/
│   │   ├── payments/
│   │   └── admin/
│   │
│   ├── components/
│   ├── layouts/
│   ├── router/
│   ├── stores/
│   ├── services/
│   ├── utils/
│   └── main.ts
```

---

# Vue Components

Los componentes deben ser pequeños y reutilizables.

---

## Correcto

```text
OrderCard.vue
QuoteSummary.vue
PaymentStatusBadge.vue
```

---

## Incorrecto

```text
BigPageWithEverything.vue
```

---

# API Services

Toda comunicación con backend debe ir en services.

---

## Ejemplo

```ts
export async function getOrders(): Promise<Order[]> {
  /**
   * Obtiene los pedidos del usuario autenticado.
   */
  const response = await api.get("/orders/");
  return response.data.results;
}
```

---

# Pinia Stores

Los stores no deben tener lógica de negocio pesada.

---

## Permitido

* Estado de autenticación.
* Usuario actual.
* Tokens.
* Datos compartidos.

---

## No permitido

* Cálculos de cotización.
* Reglas de negocio.
* Validaciones complejas.

---

# API Standards

## Base URL

```text
/api/v1/
```

---

## Admin Namespace

Todo lo administrativo debe vivir bajo:

```text
/api/v1/admin/
```

---

## JSON

Campos en:

```text
snake_case
```

---

# Testing Standards

## Backend

Usar:

```text
pytest
```

---

## Pruebas mínimas

* Services
* Calculadora
* Pagos
* Estados
* Serializers
* Permissions

---

## Cobertura mínima

```text
80%
```

---

## Servicios críticos

```text
90%
```

---

## Calculadora de costos

```text
100%
```

---

# Git Standards

## Ramas

```text
main
develop
feature/*
fix/*
hotfix/*
```

---

# Conventional Commits

Usar:

```text
feat:
fix:
docs:
refactor:
test:
chore:
```

---

## Ejemplos

```text
feat: add order creation endpoint

fix: validate payment amount

docs: update database design
```

---

# Prohibiciones Generales

No se permite:

* Código en español.
* Variables ambiguas.
* Magic numbers.
* Código duplicado.
* Lógica de negocio en views.
* Uso de float para dinero.
* Secretos en repositorio.
* print en producción.
* Archivos sin usar.
* Comentarios muertos.
* Funciones enormes.
* Componentes gigantes.
* Queries sin índices en módulos críticos.

---

# Buenas Prácticas Obligatorias

Se debe:

* Usar type hints.
* Usar Decimal para dinero.
* Usar services.
* Usar selectors para consultas complejas.
* Usar serializers para validación.
* Usar TextChoices.
* Registrar eventos importantes.
* Escribir pruebas para lógica crítica.
* Documentar decisiones importantes.
* Mantener código simple.

---

# Reglas para IA Generadora de Código

Cuando Claude, Copilot, Cursor o Continue generen código:

Deben respetar:

* Este documento.
* 01-business-rules.md.
* 02-system-architecture.md.
* 03-database-design.md.
* 04-api-specification.md.
* 05-cost-calculator.md.
* 06-payments-and-refunds.md.
* 07-testing-plan.md.

---

# La IA No Debe

* Inventar reglas de negocio.
* Cambiar nombres de tablas.
* Usar español en identificadores.
* Crear endpoints no documentados sin aprobación.
* Cambiar fórmulas.
* Saltarse services.
* Confirmar pagos automáticamente.
* Aprobar reembolsos automáticamente.

---

# Objetivo

Mantener Imprint Studio como un proyecto:

* Limpio.
* Predecible.
* Escalable.
* Fácil de mantener.
* Fácil de probar.
* Fácil de extender.

---

# Estado del Documento

Versión: 1.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* Desarrollo Backend
* Desarrollo Frontend
* Claude Code
* Copilot
* Cursor
* Continue.dev
* QA

Fin del documento.
