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

Actúas simultáneamente como:
- Arquitecto de software senior
- Desarrollador Django senior
- Desarrollador Vue senior
- QA técnico

Prioridades en orden:
1. Que funcione
2. Que sea seguro
3. Que sea mantenible
4. Que se vea bien

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
│   ├── core/                 # BaseModel, permisos, responses, exception handler
│   └── manage.py
├── docs/                     # Documentación oficial
└── frontend/                 # Vue 3 (pendiente)
```

---

## Estado actual del proyecto

### Completado
- Estructura base del proyecto Django
- App authentication: User, OTPCode, managers, serializers, services, views, urls
- App configuration: BusinessConfig, BusinessHours, Holiday, PaymentInstructions, seed_initial_data
- core: BaseModel, SoftDeleteModel, permisos, responses, exception handler
- Primera migración aplicada
- Superusuario creado
- Servidor corriendo en http://127.0.0.1:8000

### Endpoints funcionando
- POST /api/v1/auth/register/
- POST /api/v1/auth/otp/send/
- POST /api/v1/auth/otp/verify/
- POST /api/v1/auth/token/refresh/
- GET  /api/v1/auth/me/

### En progreso
- App orders: Order y RequestFile definidos en models.py
- Bloqueado: makemigrations orders falla porque ShippingAddress no existe aún

### Siguiente paso inmediato
Crear ShippingAddress en apps/shipping/models.py
Luego continuar con orders migrations y el resto de apps.

### Orden de implementación pendiente
1. shipping (ShippingAddress)
2. orders (migración desbloqueada)
3. quotes
4. payments
5. production
6. notifications
7. frontend Vue 3

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

```bash
# Activar entorno virtual
source venv/Scripts/activate

# Correr servidor
python manage.py runserver

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Datos iniciales
python manage.py seed_initial_data

# Verificar
python manage.py check
```

---

## Notas importantes

- AUTH_USER_MODEL = "authentication.User" — no cambiar
- USERNAME_FIELD = "phone" — autenticación por teléfono, no username
- En desarrollo el OTP se imprime en consola, no se envía por WhatsApp
- SQLite solo para desarrollo, PostgreSQL para producción
- psycopg2-binary no tiene wheel para Python 3.14 todavía