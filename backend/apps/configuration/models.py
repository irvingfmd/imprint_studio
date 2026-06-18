"""
Modelos de la app configuration.

Configuración global del negocio:
- BusinessConfig: costos, márgenes y plazos
- BusinessHours: horarios de atención
- Holiday: días festivos
- PaymentInstructions: datos bancarios
- Printer: catálogo de impresoras con consumo eléctrico
"""

import uuid

from django.db import models


class BusinessConfig(models.Model):
    """
    Configuración financiera y operativa del negocio.
    Debe existir únicamente un registro activo.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Costos de producción
    material_cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    electricity_rate_kwh = models.DecimalField(max_digits=10, decimal_places=4, default="2.0000")
    labor_cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    post_processing_cost_per_gram = models.DecimalField(max_digits=10, decimal_places=2)
    packaging_cost = models.DecimalField(max_digits=10, decimal_places=2)

    # Riesgo y ganancia
    failure_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    profit_margin_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    # Multiplicadores de prioridad
    urgent_multiplier = models.DecimalField(max_digits=5, decimal_places=2)
    express_multiplier = models.DecimalField(max_digits=5, decimal_places=2)

    # Descuentos
    full_payment_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    # Plazos
    deposit_deadline_hours = models.PositiveIntegerField()
    balance_deadline_days = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "business_config"

    def __str__(self) -> str:
        return f"BusinessConfig — activo: {self.is_active}"


class BusinessHours(models.Model):
    """
    Horarios de atención del taller por día de la semana.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # 1=Lunes, 2=Martes, ..., 7=Domingo
    weekday = models.PositiveSmallIntegerField()
    is_open = models.BooleanField(default=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "business_hours"
        ordering = ["weekday"]

    def __str__(self) -> str:
        dias = {
            1: "Lunes",
            2: "Martes",
            3: "Miércoles",
            4: "Jueves",
            5: "Viernes",
            6: "Sábado",
            7: "Domingo",
        }
        return f"{dias.get(self.weekday, self.weekday)} — {'Abierto' if self.is_open else 'Cerrado'}"


class Holiday(models.Model):
    """
    Días festivos que afectan la operación del taller.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    holiday_date = models.DateField(unique=True)
    holiday_name = models.CharField(max_length=255)
    affects_shipping = models.BooleanField(default=True)
    affects_pickup = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "holidays"
        ordering = ["holiday_date"]

    def __str__(self) -> str:
        return f"{self.holiday_name} — {self.holiday_date}"


class PaymentInstructions(models.Model):
    """
    Datos bancarios mostrados al cliente para realizar pagos.
    Debe existir únicamente un registro activo.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    bank_name = models.CharField(max_length=100)
    account_holder = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, blank=True, default="")
    clabe = models.CharField(max_length=30, blank=True, default="")
    card_number = models.CharField(max_length=30, blank=True, default="")
    additional_notes = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_instructions"

    def __str__(self) -> str:
        return f"{self.bank_name} — {self.account_holder}"


class Printer(models.Model):
    """
    Impresora 3D registrada en el catálogo del negocio.
    La potencia en watts se usa para calcular el costo energético de cada cotización.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100, blank=True, default="")
    power_watts = models.PositiveIntegerField()
    max_power_watts = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "printers"
        ordering = ["brand", "name"]

    def __str__(self) -> str:
        return f"{self.brand} {self.name} ({self.power_watts}W)"
