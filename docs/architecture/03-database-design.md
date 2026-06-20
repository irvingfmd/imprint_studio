# Database Design

## Imprint Studio

Versión: 4.0

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

## Excepción

Las siguientes tablas son inmutables por diseño y solo tienen `created_at`:

```text
otp_codes
quote_snapshots
production_history
order_events
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
    WEB_MODEL = "WEB_MODEL", "Web Model"
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

# OrderPaymentStatus

Campo: `orders.payment_status`

```python
class OrderPaymentStatus(models.TextChoices):
    NO_PAYMENT      = "NO_PAYMENT",      "No Payment"
    DEPOSIT_PENDING = "DEPOSIT_PENDING", "Deposit Pending"
    DEPOSIT_PAID    = "DEPOSIT_PAID",    "Deposit Paid"
    BALANCE_PENDING = "BALANCE_PENDING", "Balance Pending"
    FULLY_PAID      = "FULLY_PAID",      "Fully Paid"
    REFUNDED        = "REFUNDED",        "Refunded"
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

La fuente oficial del grafo de transiciones es:

```text
docs/appendices/status-flow.md
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
├── otp_codes        (sin FK, referencia por phone)
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
     ├── shipments
     │
     ├── internal_notes
     │
     ├── reviews
     │
     └── discount_redemptions

configuration (independiente)
├── business_config
├── business_hours
├── holidays
├── payment_instructions
└── printers

materials (independiente)
└── materials

loyalty (independiente)
├── discount_codes
└── discount_redemptions → orders, users

faq (independiente)
└── faqs
```

---

# Tabla: users

## Propósito

Almacena clientes y administradores.

Se autentica mediante número de teléfono y OTP.

---

## Configuración Django Obligatoria

```python
# settings.py
AUTH_USER_MODEL = "authentication.User"
```

Esta configuración debe estar en su lugar antes de la primera migración.
No puede cambiarse después sin resetear la base de datos.

---

## USERNAME_FIELD

El campo de identificación principal es el teléfono, no un username.

```python
USERNAME_FIELD = "phone"
REQUIRED_FIELDS = ["first_name"]
```

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
| is_staff   | BOOLEAN      | No       |
| last_login | TIMESTAMP    | Sí       |
| is_deleted | BOOLEAN      | No       |
| deleted_at | TIMESTAMP    | Sí       |
| created_at | TIMESTAMP    | No       |
| updated_at | TIMESTAMP    | No       |

---

## Nota sobre is_staff

Requerido por `AbstractBaseUser` de Django para acceso al panel de administración.
No representa el rol de negocio. El rol de negocio se gestiona mediante el campo `role`.

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

## Django Model

```python
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.authentication.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Usuario del sistema. Puede ser cliente o administrador.
    Se autentica mediante número de teléfono y OTP.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    phone = models.CharField(
        max_length=20,
        unique=True,
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
    )

    is_active = models.BooleanField(default=True)

    # Requerido por PermissionsMixin para el admin de Django.
    is_staff = models.BooleanField(default=False)

    last_login = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} ({self.phone})"

    @property
    def is_admin(self) -> bool:
        """
        Verifica si el usuario tiene rol de administrador.
        """
        return self.role == UserRole.ADMIN

    @property
    def is_customer(self) -> bool:
        """
        Verifica si el usuario tiene rol de cliente.
        """
        return self.role == UserRole.CUSTOMER
```

---

## UserManager

```python
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Manager personalizado para el modelo User.
    Usa teléfono en lugar de username.
    """

    def create_user(
        self,
        phone: str,
        first_name: str,
        password: str | None = None,
        **extra_fields,
    ):
        """
        Crea y guarda un usuario con teléfono y nombre.
        Los clientes no usan contraseña.
        """
        if not phone:
            raise ValueError("El teléfono es obligatorio.")

        user = self.model(
            phone=phone,
            first_name=first_name,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        phone: str,
        first_name: str,
        password: str,
        **extra_fields,
    ):
        """
        Crea y guarda un superusuario administrador.
        Usado por: python manage.py createsuperuser
        """
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            phone=phone,
            first_name=first_name,
            password=password,
            **extra_fields,
        )
```

---

# Tabla: otp_codes

## Propósito

Almacenar códigos OTP generados para autenticación de usuarios.

Cada vez que un usuario solicita acceso, se genera un código de 6 dígitos
vinculado a su número de teléfono.

---

## Campos

| Campo      | Tipo        | Nullable |
| ---------- | ----------- | -------- |
| id         | UUID        | No       |
| phone      | VARCHAR(20) | No       |
| code       | VARCHAR(6)  | No       |
| is_used    | BOOLEAN     | No       |
| attempts   | INTEGER     | No       |
| expires_at | TIMESTAMP   | No       |
| used_at    | TIMESTAMP   | Sí       |
| created_at | TIMESTAMP   | No       |

---

## Nota sobre phone

No es clave foránea a `users` porque el OTP puede generarse
antes de que el usuario exista (flujo de registro).

---

## Índices

```text
phone
expires_at
is_used
(phone, is_used, expires_at)   ← índice compuesto para validación activa
```

---

## Reglas de Negocio

Solo puede existir un código activo por número de teléfono.
Al generar uno nuevo, los anteriores del mismo teléfono se invalidan.

Un código expirado no puede usarse aunque `is_used = false`.

Un código con `attempts >= 5` se considera inválido aunque no haya expirado.

Los códigos no deben aparecer en logs del sistema.

Los registros pueden eliminarse físicamente después de 24 horas.
Es la única tabla del sistema donde se permite eliminación física.

---

## Duración del código

```text
10 minutos
```

---

## Límite de intentos

```text
5 intentos
```

---

## Django Model

```python
import uuid
from django.db import models
from django.utils import timezone


class OTPCode(models.Model):
    """
    Código OTP generado para autenticar a un usuario.
    Expira en 10 minutos. Máximo 5 intentos fallidos.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Sin FK a users: puede generarse antes del registro.
    phone = models.CharField(max_length=20)

    code = models.CharField(max_length=6)

    is_used = models.BooleanField(default=False)

    attempts = models.PositiveSmallIntegerField(default=0)

    expires_at = models.DateTimeField()

    used_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_codes"
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["is_used"]),
            models.Index(
                fields=["phone", "is_used", "expires_at"],
                name="idx_otp_active_lookup",
            ),
        ]

    def __str__(self) -> str:
        return f"OTP {self.phone} — {'usado' if self.is_used else 'activo'}"

    @property
    def is_expired(self) -> bool:
        """
        Verifica si el código ha expirado.
        """
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """
        Verifica si el código puede usarse para autenticarse.
        """
        return (
            not self.is_used
            and not self.is_expired
            and self.attempts < 5
        )
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

Solo una dirección puede tener `is_default = true` por usuario.

---

# Tabla: orders

## Propósito

Representa una solicitud de impresión realizada por un cliente.

Es la entidad principal del sistema y concentra el flujo completo
desde la solicitud inicial hasta la entrega final.

---

## Campos

| Campo                   | Tipo         | Nullable |
| ----------------------- | ------------ | -------- |
| id                      | UUID         | No       |
| customer_id             | UUID         | No       |
| shipping_address_id     | UUID         | Sí       |
| request_type            | VARCHAR(30)  | No       |
| title                   | VARCHAR(255) | No       |
| description             | TEXT         | No       |
| color                   | VARCHAR(100) | Sí       |
| quantity                | INTEGER      | No       |
| dimensions_notes        | TEXT         | Sí       |
| priority                | VARCHAR(20)  | No       |
| status                  | VARCHAR(50)  | No       |
| payment_status          | VARCHAR(50)  | No       |
| delivery_method         | VARCHAR(20)  | No       |
| estimated_delivery_date | DATE         | Sí       |
| approved_at             | TIMESTAMP    | Sí       |
| ready_at                | TIMESTAMP    | Sí       |
| delivered_at            | TIMESTAMP    | Sí       |
| cancelled_at            | TIMESTAMP    | Sí       |
| cancellation_reason     | TEXT         | Sí       |
| ai_analysis             | JSONB        | Sí       |
| ai_notes                | TEXT         | Sí       |
| ai_confidence           | DECIMAL(5,2) | Sí       |
| ai_category             | VARCHAR(100) | Sí       |
| is_deleted              | BOOLEAN      | No       |
| deleted_at              | TIMESTAMP    | Sí       |
| created_at              | TIMESTAMP    | No       |
| updated_at              | TIMESTAMP    | No       |

---

## Nota sobre payment_status

El nombre oficial del campo es `payment_status`.

Gestiona el estado financiero del pedido, independiente del estado operativo (`status`).

Valores permitidos definidos en `OrderPaymentStatus`.

---

## Relaciones

```text
customer_id → users.id
shipping_address_id → shipping_addresses.id
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
(status, created_at)
(customer_id, status)
(priority, status)
```

---

## Reglas de Negocio

Si `delivery_method = SHIPPING` entonces `shipping_address_id` es obligatorio.

Si `request_type = REFERENCE` el estado inicial será `RECEIVED`.

Si `request_type = PRINTABLE_FILE` el estado inicial será `PENDING_ANALYSIS`.

Si `request_type = WEB_MODEL` el estado inicial será `RECEIVED`.

Los campos `ai_analysis`, `ai_notes`, `ai_confidence`, `ai_category`
deben permanecer vacíos durante el MVP.

---

# Tabla: request_files

## Propósito

Almacenar archivos relacionados con una solicitud.

Puede contener imágenes de referencia, STL, OBJ, 3MF y comprobantes de pago.

---

## Campos

| Campo             | Tipo         | Nullable |
| ----------------- | ------------ | -------- |
| id                | UUID         | No       |
| order_id          | UUID         | No       |
| file_type         | VARCHAR(30)  | No       |
| file_url          | TEXT         | No       |
| original_filename | VARCHAR(255) | No       |
| mime_type         | VARCHAR(100) | No       |
| file_size_bytes   | BIGINT       | No       |
| uploaded_by       | UUID         | No       |
| uploaded_at       | TIMESTAMP    | No       |

---

## File Types

```text
REFERENCE
PRINTABLE_FILE
WEB_MODEL
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

## Reglas de Negocio

Un pedido puede tener múltiples archivos.

Todos los archivos deben almacenarse fuera del servidor en Cloudinary o Supabase Storage.

---

# Tabla: quotes

## Propósito

Almacena las cotizaciones oficiales generadas por el administrador.

Los datos deben provenir del laminado realizado en Bambu Studio.

---

## Campos

| Campo                | Tipo          | Nullable |
| -------------------- | ------------- | -------- |
| id                   | UUID          | No       |
| order_id             | UUID          | No       |
| weight_grams         | DECIMAL(10,2) | No       |
| print_time_hours     | DECIMAL(10,2) | No       |
| material_cost        | DECIMAL(10,2) | No       |
| energy_cost          | DECIMAL(10,2) | No       |
| labor_cost           | DECIMAL(10,2) | No       |
| post_processing_cost | DECIMAL(10,2) | No       |
| packaging_cost       | DECIMAL(10,2) | No       |
| risk_cost            | DECIMAL(10,2) | No       |
| shipping_cost        | DECIMAL(10,2) | No       |
| subtotal             | DECIMAL(10,2) | No       |
| profit_amount        | DECIMAL(10,2) | No       |
| discount_amount      | DECIMAL(10,2) | No       |
| tax_amount           | DECIMAL(10,2) | No       |
| total_price          | DECIMAL(10,2) | No       |
| quote_status         | VARCHAR(20)   | No       |
| accepted_at          | TIMESTAMP     | Sí       |
| rejected_at          | TIMESTAMP     | Sí       |
| expires_at           | TIMESTAMP     | Sí       |
| created_by           | UUID          | No       |
| is_deleted           | BOOLEAN       | No       |
| deleted_at           | TIMESTAMP     | Sí       |
| created_at           | TIMESTAMP     | No       |
| updated_at           | TIMESTAMP     | No       |

---

## Índices

```text
order_id
quote_status
created_at
expires_at
(order_id, quote_status)
```

---

## Reglas de Negocio

Un pedido puede tener múltiples cotizaciones históricas.

Solo una cotización puede estar activa al mismo tiempo.

Todos los montos monetarios usan `DECIMAL(10,2)`. Nunca `float`.

---

# Tabla: quote_snapshots

## Propósito

Almacenar una copia exacta de la configuración utilizada para generar
una cotización. Permite reconstruir una cotización histórica aunque
la configuración global haya cambiado.

---

## Inmutabilidad

Los snapshots nunca deben modificarse ni eliminarse.

No tienen `updated_at` por diseño.

---

## Campos

| Campo                            | Tipo         | Nullable |
| -------------------------------- | ------------ | -------- |
| id                               | UUID         | No       |
| quote_id                         | UUID         | No       |
| material_cost_per_kg             | DECIMAL(10,2)| No       |
| electricity_rate_kwh             | DECIMAL(10,2)| No       |
| labor_cost_per_hour              | DECIMAL(10,2)| No       |
| post_processing_cost_per_gram    | DECIMAL(10,2)| No       |
| packaging_cost                   | DECIMAL(10,2)| No       |
| failure_percentage               | DECIMAL(5,2) | No       |
| profit_margin_percentage         | DECIMAL(5,2) | No       |
| urgent_multiplier                | DECIMAL(5,2) | No       |
| express_multiplier               | DECIMAL(5,2) | No       |
| full_payment_discount_percentage | DECIMAL(5,2) | No       |
| tax_percentage                   | DECIMAL(5,2) | No       |
| printer_name                     | VARCHAR(255) | Sí       |
| printer_power_watts              | INTEGER      | Sí       |
| created_at                       | TIMESTAMP    | No       |

---

## Regla de Negocio

Cada vez que se genere una cotización se debe crear automáticamente
un snapshot de la configuración vigente.

---

# Tabla: payments

## Propósito

Registrar movimientos financieros asociados a un pedido.

Incluye anticipos, pagos finales, pagos completos y reembolsos.

---

## Campos

| Campo                | Tipo          | Nullable |
| -------------------- | ------------- | -------- |
| id                   | UUID          | No       |
| order_id             | UUID          | No       |
| amount               | DECIMAL(10,2) | No       |
| payment_type         | VARCHAR(30)   | No       |
| payment_method       | VARCHAR(30)   | No       |
| payment_status       | VARCHAR(30)   | No       |
| proof_file_url       | TEXT          | Sí       |
| manual_confirmation  | BOOLEAN       | No       |
| confirmed_by         | UUID          | Sí       |
| confirmed_at         | TIMESTAMP     | Sí       |
| notes                | TEXT          | Sí       |
| is_deleted           | BOOLEAN       | No       |
| deleted_at           | TIMESTAMP     | Sí       |
| created_at           | TIMESTAMP     | No       |

---

## Índices

```text
order_id
payment_type
payment_method
payment_status
created_at
confirmed_at
(order_id, payment_status)
```

---

## Reglas de Negocio

El comprobante es opcional. El administrador puede confirmar manualmente
con `manual_confirmation = true`.

Un pago confirmado no debe modificarse.

Los reembolsos se registran como `payment_type = REFUND`.

No se eliminan registros financieros. Nunca.

---

# Tabla: production_history

## Propósito

Mantener un historial completo y auditable de los cambios de estado.

Funciona como bitácora oficial del sistema. Nunca debe modificarse
ni eliminarse información histórica.

---

## Campos

| Campo           | Tipo        | Nullable |
| --------------- | ----------- | -------- |
| id              | UUID        | No       |
| order_id        | UUID        | No       |
| previous_status | VARCHAR(50) | Sí       |
| new_status      | VARCHAR(50) | No       |
| changed_by      | UUID        | Sí       |
| notes           | TEXT        | Sí       |
| changed_at      | TIMESTAMP   | No       |

---

## Regla de Negocio

`changed_by = NULL` indica que el cambio fue realizado por una acción automática del sistema (scheduler), no por un usuario.

---

## Índices

```text
order_id
changed_at
new_status
(order_id, changed_at)
```

---

# Tabla: order_events

## Propósito

Registrar todos los eventos relevantes de una solicitud.

Complementa a `production_history` ya que no todos los eventos
representan cambios de estado.

---

## Campos

| Campo             | Tipo         | Nullable |
| ----------------- | ------------ | -------- |
| id                | UUID         | No       |
| order_id          | UUID         | No       |
| event_type        | VARCHAR(100) | No       |
| event_description | TEXT         | Sí       |
| metadata          | JSONB        | Sí       |
| created_by        | UUID         | Sí       |
| created_at        | TIMESTAMP    | No       |

---

## Event Types

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
DEPOSIT_REMINDER
```

---

## Índices

```text
order_id
event_type
created_at
(order_id, created_at)
```

---

## Reglas de Negocio

Los eventos nunca deben modificarse ni eliminarse.

---

# Tabla: shipments

## Propósito

Registrar información relacionada con envíos a domicilio.

Solo se utiliza cuando `delivery_method = SHIPPING`.

---

## Campos

| Campo          | Tipo          | Nullable |
| -------------- | ------------- | -------- |
| id             | UUID          | No       |
| order_id       | UUID          | No       |
| carrier_name   | VARCHAR(100)  | Sí       |
| tracking_number| VARCHAR(100)  | Sí       |
| shipping_cost  | DECIMAL(10,2) | No       |
| shipped_at     | TIMESTAMP     | Sí       |
| delivered_at   | TIMESTAMP     | Sí       |
| shipping_notes | TEXT          | Sí       |
| created_at     | TIMESTAMP     | No       |
| updated_at     | TIMESTAMP     | No       |

---

## Índices

```text
order_id
tracking_number
shipped_at
```

---

## Reglas de Negocio

Un pedido puede tener cero o un envío.

El costo registrado aquí debe coincidir con el costo aprobado en la cotización.

---

# Tabla: business_config

## Propósito

Almacenar configuración global del negocio.

Debe existir únicamente un registro activo.

---

## Campos

| Campo                            | Tipo         | Nullable |
| -------------------------------- | ------------ | -------- |
| id                               | UUID         | No       |
| material_cost_per_kg             | DECIMAL(10,2)| No       |
| electricity_rate_kwh             | DECIMAL(10,2)| No       |
| labor_cost_per_hour              | DECIMAL(10,2)| No       |
| post_processing_cost_per_gram    | DECIMAL(10,2)| No       |
| packaging_cost                   | DECIMAL(10,2)| No       |
| failure_percentage               | DECIMAL(5,2) | No       |
| profit_margin_percentage         | DECIMAL(5,2) | No       |
| urgent_multiplier                | DECIMAL(5,2) | No       |
| express_multiplier               | DECIMAL(5,2) | No       |
| full_payment_discount_percentage | DECIMAL(5,2) | No       |
| tax_percentage                   | DECIMAL(5,2) | No       |
| deposit_deadline_hours           | INTEGER      | No       |
| balance_deadline_days            | INTEGER      | No       |
| is_active                        | BOOLEAN      | No       |
| created_at                       | TIMESTAMP    | No       |
| updated_at                       | TIMESTAMP    | No       |

---

## Valores Iniciales Recomendados

| Configuración                    | Valor |
| -------------------------------- | ----- |
| material_cost_per_kg             | 25.00 |
| electricity_rate_kwh             | 1.50  |
| labor_cost_per_hour              | 15.00 |
| post_processing_cost_per_gram    | 0.05  |
| packaging_cost                   | 2.00  |
| failure_percentage               | 10.00 |
| profit_margin_percentage         | 30.00 |
| urgent_multiplier                | 1.30  |
| express_multiplier               | 1.50  |
| full_payment_discount_percentage | 5.00  |
| tax_percentage                   | 16.00 |
| deposit_deadline_hours           | 72    |
| balance_deadline_days            | 7     |

---

## Regla de Negocio

Todas las cotizaciones deben calcularse usando la configuración vigente
al momento de crear la cotización.

---

# Tabla: business_hours

## Propósito

Configurar horarios oficiales del taller.

---

## Campos

| Campo        | Tipo    | Nullable |
| ------------ | ------- | -------- |
| id           | UUID    | No       |
| weekday      | INTEGER | No       |
| is_open      | BOOLEAN | No       |
| opening_time | TIME    | Sí       |
| closing_time | TIME    | Sí       |
| notes        | TEXT    | Sí       |

---

## Valores de weekday

| Valor | Día       |
| ----- | --------- |
| 1     | Monday    |
| 2     | Tuesday   |
| 3     | Wednesday |
| 4     | Thursday  |
| 5     | Friday    |
| 6     | Saturday  |
| 7     | Sunday    |

---

## Regla de Negocio

Si `is_open = false` entonces `opening_time` y `closing_time` deben ser NULL.

---

# Tabla: holidays

## Propósito

Registrar días festivos que afectan la operación.

---

## Campos

| Campo            | Tipo         | Nullable |
| ---------------- | ------------ | -------- |
| id               | UUID         | No       |
| holiday_date     | DATE         | No       |
| holiday_name     | VARCHAR(255) | No       |
| affects_shipping | BOOLEAN      | No       |
| affects_pickup   | BOOLEAN      | No       |
| created_at       | TIMESTAMP    | No       |

---

## Índices

```text
holiday_date
```

---

## Reglas de Negocio

Los días festivos deben excluirse del cálculo de fechas de entrega.

No deben existir fechas duplicadas.

---

# Tabla: payment_instructions

## Propósito

Almacenar información bancaria visible para clientes.

Debe existir únicamente un registro activo.

---

## Campos

| Campo            | Tipo         | Nullable |
| ---------------- | ------------ | -------- |
| id               | UUID         | No       |
| bank_name        | VARCHAR(100) | No       |
| account_holder   | VARCHAR(255) | No       |
| account_number   | VARCHAR(50)  | Sí       |
| clabe            | VARCHAR(30)  | Sí       |
| card_number      | VARCHAR(30)  | Sí       |
| additional_notes | TEXT         | Sí       |
| is_active        | BOOLEAN      | No       |
| updated_at       | TIMESTAMP    | No       |

---

# Tabla: printers

## Propósito

Almacenar el catálogo de impresoras 3D disponibles en el taller.

Se usa para calcular el costo energético real de cada cotización basándose en los watts de la impresora seleccionada.

---

## Campos

| Campo           | Tipo         | Nullable |
| --------------- | ------------ | -------- |
| id              | UUID         | No       |
| name            | VARCHAR(100) | No       |
| brand           | VARCHAR(100) | No       |
| power_watts     | INTEGER      | No       |
| max_power_watts | INTEGER      | Sí       |
| is_active       | BOOLEAN      | No       |
| created_at      | TIMESTAMP    | No       |
| updated_at      | TIMESTAMP    | No       |

---

## Descripción de Campos

| Campo           | Descripción |
| --------------- | ----------- |
| power_watts     | Consumo promedio en operación normal (watts) |
| max_power_watts | Potencia máxima técnica de pico (watts) — referencia, no se usa en cálculos |
| is_active       | Si está disponible para seleccionar en nuevas cotizaciones |

---

## Reglas de Negocio

El campo `power_watts` es el que se usa en el cálculo de costo energético.

Si no se selecciona impresora al cotizar, `energy_cost = 0`.

Las impresoras inactivas no aparecen en el selector del panel admin.

---

# Tabla: internal_notes

## Propósito

Notas internas del equipo asociadas a un pedido. Solo visibles para administradores.

---

## Campos

| Campo      | Tipo   | Nullable |
| ---------- | ------ | -------- |
| id         | UUID   | No       |
| order_id   | UUID   | No       |
| created_by | UUID   | No       |
| content    | TEXT   | No       |
| created_at | TIMESTAMP | No    |

---

## Relaciones

```text
order_id → orders.id
created_by → users.id
```

---

## Índices

```text
order_id
created_at
```

---

## Regla de Negocio

Las notas internas nunca son visibles para el cliente. Solo admins pueden crear y leer.

---

# Tabla: reviews

## Propósito

Almacena calificaciones y comentarios de clientes sobre pedidos entregados.

---

## Campos

| Campo       | Tipo         | Nullable |
| ----------- | ------------ | -------- |
| id          | UUID         | No       |
| order_id    | UUID         | No       |
| customer_id | UUID         | No       |
| rating      | SMALLINT     | No       |
| comment     | TEXT         | Sí       |
| created_at  | TIMESTAMP    | No       |

---

## Relaciones

```text
order_id → orders.id (OneToOne)
customer_id → users.id
```

---

## Restricciones

- `rating` debe estar entre 1 y 5
- Un pedido solo puede tener una reseña (OneToOneField)

---

## Regla de Negocio

Solo se puede crear una reseña si `order.status = DELIVERED` y `order.customer = customer`.

---

# Tabla: materials

## Propósito

Catálogo de materiales de impresión 3D con tracking de inventario.

---

## Campos

| Campo           | Tipo          | Nullable |
| --------------- | ------------- | -------- |
| id              | UUID          | No       |
| name            | VARCHAR(100)  | No       |
| material_type   | VARCHAR(20)   | No       |
| brand           | VARCHAR(100)  | Sí       |
| available_colors| JSONB         | No       |
| price_per_kg    | DECIMAL(10,2) | No       |
| stock_grams     | DECIMAL(10,2) | No       |
| min_stock_grams | DECIMAL(10,2) | No       |
| is_active       | BOOLEAN       | No       |
| created_at      | TIMESTAMP     | No       |
| updated_at      | TIMESTAMP     | No       |

---

## MaterialType

```python
class MaterialType(models.TextChoices):
    PLA = "PLA", "PLA"
    PETG = "PETG", "PETG"
    ABS = "ABS", "ABS"
    TPU = "TPU", "TPU"
    RESIN = "RESIN", "Resin"
    OTHER = "OTHER", "Other"
```

---

## Reglas de Negocio

`available_colors` es una lista JSON de strings (ej: `["Negro", "Blanco", "Rojo"]`).

Si `stock_grams < min_stock_grams`, el material se marca como bajo stock en el panel admin.

---

# Tabla: discount_codes

## Propósito

Almacena códigos de descuento para el programa de lealtad.

---

## Campos

| Campo            | Tipo          | Nullable |
| ---------------- | ------------- | -------- |
| id               | UUID          | No       |
| code             | VARCHAR(50)   | No       |
| discount_type    | VARCHAR(20)   | No       |
| discount_value   | DECIMAL(10,2) | No       |
| min_order_amount | DECIMAL(10,2) | No       |
| max_uses         | INTEGER       | Sí       |
| current_uses     | INTEGER       | No       |
| valid_from       | TIMESTAMP     | No       |
| valid_until      | TIMESTAMP     | Sí       |
| is_active        | BOOLEAN       | No       |
| created_at       | TIMESTAMP     | No       |
| updated_at       | TIMESTAMP     | No       |

---

## DiscountType

```python
class DiscountType(models.TextChoices):
    PERCENTAGE = "PERCENTAGE", "Percentage"
    FIXED_AMOUNT = "FIXED_AMOUNT", "Fixed Amount"
```

---

## Restricciones

- `code` es unique y uppercase
- `max_uses = NULL` significa ilimitado
- `valid_until = NULL` significa sin expiración

---

# Tabla: discount_redemptions

## Propósito

Registra cada uso de un código de descuento.

---

## Campos

| Campo            | Tipo          | Nullable |
| ---------------- | ------------- | -------- |
| id               | UUID          | No       |
| discount_code_id | UUID          | No       |
| order_id         | UUID          | No       |
| customer_id      | UUID          | No       |
| discount_applied | DECIMAL(10,2) | No       |
| redeemed_at      | TIMESTAMP     | No       |

---

## Relaciones

```text
discount_code_id → discount_codes.id
order_id → orders.id
customer_id → users.id
```

---

# Recomendaciones para Django Models

## BaseModel

```python
class BaseModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

---

## SoftDeleteModel

```python
class SoftDeleteModel(BaseModel):

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
```

---

# Orden de Migraciones Sugerido

```text
authentication   ← primero, porque todos dependen de users
configuration
shipping
orders
quotes
payments
production
reviews
materials
loyalty
faq
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

Durante el MVP deben permanecer vacíos.

---

# Objetivo del Diseño

Proporcionar una estructura de datos robusta, escalable y mantenible
que permita operar completamente Imprint Studio utilizando reglas de
negocio claras, automatización controlada y una arquitectura preparada
para futuras expansiones sin requerir rediseños significativos.

---

# Estado del Documento

Versión: 4.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* Django Models
* Migraciones
* PostgreSQL
* DRF
* Servicios
* Automatizaciones
* Futuras integraciones de IA

Fin del documento.