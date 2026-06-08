# Django Setup — Configuración Obligatoria Pre-Migración

## Imprint Studio

Versión: 1.0

Estado: Aprobado para implementación

---

# Propósito

Este documento define la configuración que DEBE estar en su lugar
antes de ejecutar la primera migración de Django.

Si se omite cualquiera de estos pasos y se ejecuta `migrate`,
será necesario un reset completo de la base de datos.

No hay forma de cambiar `AUTH_USER_MODEL` después de la primera migración.

---

# Orden Obligatorio de Implementación

```text
1. Crear app authentication
2. Definir User model con USERNAME_FIELD = "phone"
3. Definir UserManager
4. Configurar AUTH_USER_MODEL en settings.py
5. Registrar app en INSTALLED_APPS
6. Ejecutar makemigrations authentication
7. Ejecutar migrate
8. Nunca antes.
```

---

# 1. Estructura de la App Authentication

```text
backend/
└── apps/
    └── authentication/
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── managers.py      ← UserManager
        ├── models.py        ← User, OTPCode
        ├── serializers.py
        ├── services.py
        ├── views.py
        ├── urls.py
        ├── permissions.py
        ├── tests/
        │   ├── __init__.py
        │   ├── test_register.py
        │   ├── test_otp.py
        │   └── test_jwt.py
        └── migrations/
            └── __init__.py
```

---

# 2. settings.py — Configuración Mínima Requerida

```python
# ============================================================
# apps/authentication debe estar ANTES de django.contrib.auth
# para que Django use nuestro modelo de usuario.
# ============================================================

INSTALLED_APPS = [
    # Apps internas — van primero.
    "apps.authentication",
    "apps.orders",
    "apps.quotes",
    "apps.payments",
    "apps.production",
    "apps.shipping",
    "apps.notifications",
    "apps.configuration",

    # Django core.
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceros.
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
]

# ============================================================
# CRÍTICO: Debe definirse antes de la primera migración.
# No puede cambiarse después sin resetear la base de datos.
# ============================================================
AUTH_USER_MODEL = "authentication.User"

# ============================================================
# Zona horaria oficial del sistema.
# ============================================================
TIME_ZONE = "America/Mexico_City"
USE_TZ = True

# ============================================================
# Configuración de Django REST Framework.
# ============================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Handler global de excepciones para formato estándar de respuestas.
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
}

# ============================================================
# Configuración de SimpleJWT.
# ============================================================
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_MINUTES", 60))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.environ.get("JWT_REFRESH_DAYS", 7))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    # Usar el campo phone como claim de usuario en el token.
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ============================================================
# CORS — Restringido al frontend oficial.
# ============================================================
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173",  # Solo para desarrollo local.
).split(",")

CORS_ALLOW_CREDENTIALS = True

# ============================================================
# Configuración de base de datos.
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "imprint_studio"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# En desarrollo local puede usarse SQLite.
# Nunca en producción.
if os.environ.get("USE_SQLITE") == "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

---

# 3. Custom Exception Handler

Este handler es requerido por `REST_FRAMEWORK["EXCEPTION_HANDLER"]`
definido arriba. Garantiza que todos los errores respondan en el
formato estándar documentado en `04-api-specification.md`.

Archivo:

```text
backend/core/exceptions.py
```

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Handler global de excepciones para Django REST Framework.
    Normaliza todas las respuestas de error al formato estándar:
    {
        "success": false,
        "message": "...",
        "errors": {...}  # opcional
    }
    """
    # Primero llamamos al handler por defecto de DRF.
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "success": False,
            "message": _get_error_message(response),
        }

        # Agregar campo errors solo si hay detalles de validación.
        if isinstance(response.data, dict) and response.data != {}:
            errors = _extract_errors(response.data)
            if errors:
                error_data["errors"] = errors

        response.data = error_data

    return response


def _get_error_message(response) -> str:
    """
    Extrae el mensaje principal del error.
    """
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        return "Validation error"
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return "Authentication required"
    if response.status_code == status.HTTP_403_FORBIDDEN:
        return "Permission denied"
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return "Resource not found"
    if response.status_code == status.HTTP_409_CONFLICT:
        return "Conflict"
    if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        return "Too many requests"
    return "An error occurred"


def _extract_errors(data: dict) -> dict | None:
    """
    Extrae errores de validación para incluirlos en la respuesta.
    Solo cuando el error es 400 con detalles de campo.
    """
    if "detail" in data:
        return None  # Error simple, no de validación por campo.
    return data
```

---

# 4. Checklist Pre-Migración

Antes de ejecutar `python manage.py makemigrations`:

```text
[ ] AUTH_USER_MODEL = "authentication.User" está en settings.py
[ ] apps.authentication está en INSTALLED_APPS
[ ] User model extiende AbstractBaseUser y PermissionsMixin
[ ] User model tiene USERNAME_FIELD = "phone"
[ ] User model tiene REQUIRED_FIELDS = ["first_name"]
[ ] UserManager está implementado con create_user y create_superuser
[ ] UserManager está asignado como objects = UserManager() en el modelo
[ ] OTPCode model está definido en el mismo models.py o importado
[ ] No se ha ejecutado migrate todavía
```

---

# 5. Comandos en Orden Correcto

```bash
# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate      # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Verificar configuración de Django antes de migrar
python manage.py check

# Crear migraciones (solo authentication primero)
python manage.py makemigrations authentication

# Aplicar migraciones
python manage.py migrate

# Crear superusuario administrador
# Pedirá: phone, first_name, password
python manage.py createsuperuser

# Cargar datos iniciales
python manage.py seed_initial_data

# Verificar que todo está bien
python manage.py check --deploy
```

---

# 6. Management Command: seed_initial_data

Este comando reemplaza al `seed.sql` para que sea ejecutable
desde cualquier entorno sin acceso directo a la base de datos.

Archivo:

```text
backend/apps/configuration/management/commands/seed_initial_data.py
```

```python
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    """
    Carga los datos iniciales necesarios para operar el sistema.
    Equivalente a seed.sql pero usando el ORM de Django.
    """

    help = "Carga datos iniciales: business_config, business_hours, holidays, payment_instructions."

    def handle(self, *args, **options):
        self._seed_business_config()
        self._seed_business_hours()
        self._seed_holidays()
        self._seed_payment_instructions()
        self.stdout.write(
            self.style.SUCCESS("Datos iniciales cargados correctamente.")
        )

    def _seed_business_config(self):
        """
        Crea la configuración inicial del negocio si no existe.
        """
        from apps.configuration.models import BusinessConfig

        if BusinessConfig.objects.filter(is_active=True).exists():
            self.stdout.write("business_config: ya existe, omitiendo.")
            return

        BusinessConfig.objects.create(
            material_cost_per_kg="25.00",
            energy_cost_per_hour="0.50",
            labor_cost_per_hour="15.00",
            post_processing_cost_per_gram="0.05",
            packaging_cost="2.00",
            failure_percentage="10.00",
            profit_margin_percentage="30.00",
            urgent_multiplier="1.30",
            express_multiplier="1.50",
            full_payment_discount_percentage="5.00",
            deposit_deadline_hours=72,
            balance_deadline_days=7,
            is_active=True,
        )
        self.stdout.write("business_config: creado.")

    def _seed_business_hours(self):
        """
        Crea los horarios de atención iniciales si no existen.
        """
        from apps.configuration.models import BusinessHours

        if BusinessHours.objects.exists():
            self.stdout.write("business_hours: ya existen, omitiendo.")
            return

        horarios = [
            (1, True, "09:00", "18:00", "Horario normal"),
            (2, True, "09:00", "18:00", "Horario normal"),
            (3, True, "09:00", "18:00", "Horario normal"),
            (4, True, "09:00", "18:00", "Horario normal"),
            (5, True, "09:00", "18:00", "Horario normal"),
            (6, True, "09:00", "14:00", "Horario reducido"),
            (7, False, None, None, "Cerrado"),
        ]

        for weekday, is_open, opening, closing, notes in horarios:
            BusinessHours.objects.create(
                weekday=weekday,
                is_open=is_open,
                opening_time=opening,
                closing_time=closing,
                notes=notes,
            )

        self.stdout.write("business_hours: creados.")

    def _seed_holidays(self):
        """
        Crea los días festivos iniciales de México si no existen.
        """
        from apps.configuration.models import Holiday

        if Holiday.objects.exists():
            self.stdout.write("holidays: ya existen, omitiendo.")
            return

        festivos = [
            ("2026-01-01", "Año Nuevo"),
            ("2026-02-05", "Día de la Constitución Mexicana"),
            ("2026-03-16", "Natalicio de Benito Juárez"),
            ("2026-05-01", "Día del Trabajo"),
            ("2026-09-16", "Día de la Independencia de México"),
            ("2026-11-16", "Día de la Revolución Mexicana"),
            ("2026-12-25", "Navidad"),
        ]

        for fecha, nombre in festivos:
            Holiday.objects.create(
                holiday_date=fecha,
                holiday_name=nombre,
                affects_shipping=True,
                affects_pickup=True,
            )

        self.stdout.write("holidays: creados.")

    def _seed_payment_instructions(self):
        """
        Crea instrucciones de pago placeholder si no existen.
        Deben actualizarse con datos reales antes de producción.
        """
        from apps.configuration.models import PaymentInstructions

        if PaymentInstructions.objects.filter(is_active=True).exists():
            self.stdout.write("payment_instructions: ya existen, omitiendo.")
            return

        PaymentInstructions.objects.create(
            bank_name="BBVA",
            account_holder="Imprint Studio",
            account_number=None,
            clabe=None,
            card_number=None,
            additional_notes=(
                "Configurar datos bancarios reales antes de producción. "
                "El cliente debe enviar comprobante después de realizar la transferencia."
            ),
            is_active=True,
        )
        self.stdout.write(
            "payment_instructions: creadas (datos placeholder, actualizar antes de producción)."
        )
```

---

# 7. apps.py de Authentication

```python
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
    verbose_name = "Authentication"
```

---

# Estado del Documento

Versión: 1.0

Estado:

Aprobado para implementación.

Fuente oficial para:

* Setup inicial del proyecto
* Primera migración
* Configuración de settings.py
* createsuperuser
* seed_initial_data

Fin del documento.