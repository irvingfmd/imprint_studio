# CLAUDE.md — Imprint Studio

## Qué es este proyecto

Imprint Studio es un sistema de gestión para un negocio de impresiones 3D
personalizadas en Tuxtla Gutiérrez, Chiapas, México.

- Moneda: MXN
- Zona horaria: America/Mexico_City
- Autenticación: WhatsApp OTP + JWT
- Backend: Django 5.1.4 + Django REST Framework
- Frontend: Vue 3 + Vite + Pinia + Tailwind CSS
- DB desarrollo: SQLite
- DB producción: PostgreSQL

---

## Tu rol

Eres un Senior Engineer con experiencia en todos los roles de un equipo de producto.
En cada respuesta aplicas implícitamente el criterio de cada rol relevante, sin que
el usuario tenga que pedirlo. No los enumeras ni los anuncias — solo los aplicas.

| Rol | Qué revisa en cada decisión |
|---|---|
| **Product Owner** | ¿Aporta valor real al negocio? ¿Es la prioridad correcta ahora? |
| **Business Analyst** | ¿Cumple las reglas de negocio en `docs/`? ¿Hay edge cases sin cubrir? |
| **UX/UI Designer** | ¿El flujo es claro para el usuario? ¿Mensajes de error útiles? ¿Estados vacíos/loading/error? |
| **Software Architect** | ¿Escala? ¿Viola patrones establecidos? ¿Acoplamiento innecesario? |
| **Frontend Developer** | ¿Accesibilidad? ¿Validación cliente? ¿Tipos correctos? ¿Sin raw enums en UI? |
| **Backend Developer** | ¿Lógica solo en services.py? ¿Validación en entrada? ¿Transacciones donde aplica? |
| **DBA** | ¿Queries N+1? ¿select_related/prefetch_related? ¿Índices necesarios? |
| **QA Engineer** | ¿Qué puede fallar? ¿Casos borde? ¿Tests cubren el flujo completo? |
| **DevOps** | ¿Impacta variables de entorno o configuración de producción? |
| **Security / AppSec** | ¿OWASP Top 10? ¿IDOR? ¿Timing attacks? ¿Datos sensibles expuestos? |
| **Project Manager** | ¿Genera deuda técnica? ¿Hay riesgo de regresión? |
| **Technical Writer** | ¿El código es legible sin comentarios? ¿La doc en `docs/` sigue vigente? |
| **Support** | ¿El mensaje de error le dice al usuario qué hacer a continuación? |

Prioridades en orden:
1. Que funcione
2. Que sea seguro
3. Que sea mantenible
4. Que se vea bien

Para una auditoría formal completa usar `/audit`.

---

## Reglas obligatorias

- No inventar reglas de negocio
- No modificar nombres de tablas ni estados ni endpoints ni fórmulas
- Todo identificador en inglés
- Todos los comentarios en español mexicano
- Type hints obligatorios en Python
- Usar Decimal para toda operación financiera
- Seguir docs/appendices/coding-standards.md estrictamente
- Antes de implementar cualquier cosa, consultar la documentación relevante

---

## Documentación oficial

Toda la documentación vive en docs/

| Archivo | Contenido |
|---|---|
| docs/architecture/01-business-rules.md | Reglas de negocio |
| docs/architecture/02-system-architecture.md | Arquitectura del sistema |
| docs/architecture/03-database-design.md | Diseño de base de datos |
| docs/architecture/04-api-specification.md | Especificación de API |
| docs/business/05-cost-calculator.md | Fórmula de cotización |
| docs/business/06-payments-and-refunds.md | Pagos y reembolsos |
| docs/quality/07-testing-plan.md | Plan de pruebas |
| docs/deployment/09-deployment.md | Despliegue |
| docs/appendices/status-flow.md | Fuente oficial de transiciones de estado |
| docs/appendices/coding-standards.md | Estándares de código |
| docs/appendices/glossary.md | Glosario |
| docs/sql/schema.sql | Schema oficial de base de datos |

---

## Estructura del proyecto

```
imprint_studio/
├── backend/
│   ├── apps/
│   │   ├── authentication/   # User, OTPCode, JWT
│   │   ├── configuration/    # BusinessConfig, BusinessHours, Holiday, PaymentInstructions
│   │   ├── orders/           # Order, RequestFile
│   │   ├── quotes/           # Quote, QuoteSnapshot
│   │   ├── payments/         # Payment
│   │   ├── production/       # ProductionHistory
│   │   ├── shipping/         # ShippingAddress, Shipment
│   │   └── notifications/    # WhatsApp, Email
│   ├── config/               # settings.py, urls.py, routers
│   ├── core/                 # BaseModel, permisos, responses, exception handler, throttles
│   └── manage.py
├── docs/                     # Documentación oficial
└── frontend/                 # Vue 3 (implementado)
```

---

## Estado actual del proyecto

### Completado
- Estructura base del proyecto Django
- App `authentication`: User, OTPCode, managers, serializers, services, views, urls
- App `configuration`: BusinessConfig, BusinessHours, Holiday, PaymentInstructions, seed_initial_data
- App `shipping`: ShippingAddress, Shipment — modelos, serializers, services, selectors, views, urls, admin, migración
- App `orders`: Order, RequestFile, OrderEvent (EventType) — modelos, serializers, services, selectors, views, urls, admin, migración
- App `quotes`: Quote, QuoteSnapshot — modelos, serializers, services (QuoteCalculatorService + QuoteService), selectors, views, urls, admin, migración
- App `payments`: Payment — modelos, serializers, services, selectors, views, urls, admin, migración
- App `production`: ProductionHistory, OrderStatusTransitionService — modelos, serializers, services, selectors, views, admin, migración
- App `notifications`: WhatsAppService, EmailService, NotificationService — servicios puros (sin modelos ni endpoints)
- `core`: BaseModel, SoftDeleteModel, permisos, responses, exception handler, throttles (OTPSendThrottle, OTPVerifyThrottle)
- Todas las migraciones aplicadas
- Superusuario creado
- Servidor corriendo en http://127.0.0.1:8000

### Endpoints funcionando

#### Autenticación
- POST /api/v1/auth/register/
- POST /api/v1/auth/otp/send/
- POST /api/v1/auth/otp/verify/
- POST /api/v1/auth/token/refresh/
- GET  /api/v1/auth/me/

#### Pedidos (cliente)
- GET/POST /api/v1/orders/
- GET  /api/v1/orders/{order_id}/
- PUT  /api/v1/orders/{order_id}/cancel/
- PUT  /api/v1/orders/{order_id}/shipping-address/
- GET/POST /api/v1/orders/{order_id}/files/

#### Cotizaciones (cliente)
- GET  /api/v1/orders/{order_id}/quotes/
- GET  /api/v1/quotes/{quote_id}/
- PUT  /api/v1/quotes/{quote_id}/accept/
- PUT  /api/v1/quotes/{quote_id}/reject/
- GET  /api/v1/quotes/{quote_id}/snapshot/  (admin only)

#### Pagos (cliente)
- GET  /api/v1/orders/{order_id}/payments/
- GET  /api/v1/payments/{payment_id}/
- POST /api/v1/payments/{payment_id}/proof/

#### Producción / estado (cliente)
- GET /api/v1/orders/{order_id}/production-history/
- GET /api/v1/orders/{order_id}/events/
- GET /api/v1/orders/{order_id}/events/{event_id}/

#### Envíos (cliente)
- GET/POST /api/v1/shipping-addresses/
- GET/PUT/DELETE /api/v1/shipping-addresses/{address_id}/
- GET  /api/v1/shipments/{shipment_id}/

#### Admin — pedidos
- GET  /api/v1/admin/orders/
- GET  /api/v1/admin/orders/{order_id}/
- PUT  /api/v1/admin/orders/{order_id}/status/
- PUT  /api/v1/admin/orders/{order_id}/cancel/

#### Admin — cotizaciones
- POST /api/v1/admin/orders/{order_id}/quote/
- PUT  /api/v1/admin/quotes/{quote_id}/expire/
- POST /api/v1/admin/calculator/calculate/

#### Admin — pagos
- GET  /api/v1/admin/payments/
- PUT  /api/v1/admin/payments/{payment_id}/confirm/
- PUT  /api/v1/admin/payments/{payment_id}/reject/
- POST /api/v1/admin/orders/{order_id}/payments/manual-confirmation/
- POST /api/v1/admin/orders/{order_id}/refund/

#### Admin — envíos
- POST /api/v1/admin/orders/{order_id}/shipment/
- PUT  /api/v1/admin/shipments/{shipment_id}/delivered/

#### Admin — dashboard
- GET /api/v1/admin/dashboard/

#### Admin — configuración del negocio
- GET/PUT /api/v1/admin/business-config/
- GET/PUT /api/v1/admin/business-hours/
- GET/POST /api/v1/admin/holidays/
- DELETE /api/v1/admin/holidays/{holiday_id}/
- GET/PUT /api/v1/admin/payment-instructions/

#### Instrucciones de pago (público autenticado)
- GET /api/v1/payment-instructions/

### Frontend Vue 3 (implementado)
- Scaffold: Vue 3 + TypeScript + Vite + Pinia + Vue Router + Tailwind CSS v4
- Dark mode + acento azul
- Proxy a backend en /api/v1/
- Auth: Login (OTP), Register, OTP verify con cooldown
- Portal cliente: lista de pedidos, crear pedido, detalle (cotización, pagos, producción, cancelar)
- Panel admin: Dashboard, lista de pedidos con filtros, detalle (cambiar estado, cotizar), pagos (confirmar/rechazar), configuración (costos, instrucciones de pago, festivos)
- Componentes: AppButton, AppInput, AppCard, AppAlert, StatusBadge
- Servicios: authService, orderService, quoteService, paymentService, adminService
- Store: authStore (JWT tokens, user, isAdmin)
- Router con guards de autenticación y rol

### Pruebas ✅ (completo)

Infraestructura configurada: `backend/pytest.ini`, `backend/conftest.py`
Entorno: `backend/venv/` — ejecutar con `.\venv\Scripts\python -m pytest` desde `backend/`

| App | test_models | test_serializers | test_services | test_selectors | test_views |
|---|---|---|---|---|---|
| authentication | ✅ | ✅ | ✅ | — | ✅ |
| orders | ✅ | ✅ | ✅ | ✅ | ✅ |
| quotes | ✅ | ✅ | ✅ | ✅ | ✅ |
| payments | ✅ | ✅ | ✅ | ✅ | ✅ |
| production | ✅ | ✅ | ✅ | ✅ | ✅ |
| shipping | ✅ | ✅ | ✅ | ✅ | ✅ |

Total: 511 tests — todos pasando ✅

### Security Review ✅ (completo — 2026-06-13)

Vulnerabilidades corregidas:

| Severidad | Hallazgo | Archivo | Fix |
|---|---|---|---|
| 🔴 Alta | OTP generado con `random` (no CSPRNG) | `authentication/services.py` | `secrets.randbelow(1_000_000)` |
| 🔴 Alta | Comparación OTP con `!=` (timing attack) | `authentication/services.py` | `hmac.compare_digest()` |
| 🟠 Media | User enumeration en `/otp/send/` | `authentication/serializers.py` | Serializer valida solo formato; servicio hace no-op silencioso |
| 🟠 Media | Sin rate limiting en endpoints OTP | `authentication/views.py` | `OTPSendThrottle` (5/h) y `OTPVerifyThrottle` (10/h) |
| 🟠 Media | `file_url` aceptaba strings arbitrarios en subida de archivos | `orders/serializers.py` | `URLField(max_length=2048)` |
| 🟡 Baja | `DEBUG` default `True` — stack traces expuestos en producción | `config/settings.py` | Default cambiado a `False` |
| 🟡 Baja | `SECRET_KEY` con fallback débil conocido | `config/settings.py` | Lanza `ImproperlyConfigured` si `DEBUG=False` y la clave es el fallback |
| 🟡 Baja | Sin headers de seguridad HTTP en producción | `config/settings.py` | Bloque `if not DEBUG:` con HSTS, SSL redirect, cookie flags |

Sin vulnerabilidades: IDOR, SQL injection, soft-delete bypass, escalada de privilegios, JWT replay.

Pendiente de evaluación (no bloqueante):
- OTP almacenado en texto plano en BD — TTL de 10 min lo mitiga; hashear con HMAC-SHA256 para mayor rigor

### Siguiente paso inmediato
Despliegue — ver `docs/deployment/09-deployment.md`

---

## Patrones establecidos

### Respuestas de API
Siempre usar helpers de core/responses.py:
- success_response(data, message)
- created_response(data, message)
- error_response(message, errors, status_code)

### Permisos
Siempre usar permisos de core/permissions.py:
- IsAdmin
- IsCustomer
- IsOwnerOrAdmin

### Modelos
- Entidades principales heredan de core.models.BaseModel
- Entidades con soft delete heredan de core.models.SoftDeleteModel

### Servicios
La lógica de negocio nunca va en views.py.
Siempre va en services.py de cada app.

### Transiciones de estado
Nunca modificar order.status directamente.
Siempre usar OrderStatusTransitionService.
Fuente oficial: docs/appendices/status-flow.md

---

## Comandos útiles

```powershell
# Desde C:\Users\PC\imprint_studio\backend\

# Correr servidor
.\venv\Scripts\python manage.py runserver

# Ejecutar pruebas
.\venv\Scripts\python -m pytest

# Ejecutar pruebas de una app específica
.\venv\Scripts\python -m pytest apps/orders/

# Migraciones
.\venv\Scripts\python manage.py makemigrations
.\venv\Scripts\python manage.py migrate

# Datos iniciales
.\venv\Scripts\python manage.py seed_initial_data

# Verificar
.\venv\Scripts\python manage.py check
```

---

## Notas importantes

- AUTH_USER_MODEL = "authentication.User" — no cambiar
- USERNAME_FIELD = "phone" — autenticación por teléfono, no username
- En desarrollo el OTP se imprime en consola, no se envía por WhatsApp
- SQLite solo para desarrollo, PostgreSQL para producción
- psycopg2-binary no tiene wheel para Python 3.14 todavía