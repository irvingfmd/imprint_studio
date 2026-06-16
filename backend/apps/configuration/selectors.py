"""
Selectores para la app configuration.
Encapsulan las consultas a la base de datos.
"""
from django.db.models import QuerySet

from .models import BusinessConfig, BusinessHours, Holiday, PaymentInstructions, Printer


def get_active_business_config() -> BusinessConfig | None:
    """Retorna la configuración activa del negocio."""
    return BusinessConfig.objects.filter(is_active=True).first()


def get_all_business_hours() -> QuerySet:
    """Retorna todos los horarios ordenados por día de semana."""
    return BusinessHours.objects.all().order_by("weekday")


def get_business_hours_by_weekday(weekday: int) -> BusinessHours | None:
    """Retorna el horario de un día específico."""
    return BusinessHours.objects.filter(weekday=weekday).first()


def get_all_holidays() -> QuerySet:
    """Retorna todos los días festivos ordenados por fecha."""
    return Holiday.objects.all().order_by("holiday_date")


def get_holiday_by_id(holiday_id: str) -> Holiday | None:
    """Retorna un día festivo por su ID."""
    return Holiday.objects.filter(id=holiday_id).first()


def get_active_payment_instructions() -> PaymentInstructions | None:
    """Retorna las instrucciones de pago activas."""
    return PaymentInstructions.objects.filter(is_active=True).first()


def get_all_printers(active_only: bool = False) -> QuerySet:
    """Retorna todas las impresoras del catálogo."""
    qs = Printer.objects.all()
    if active_only:
        qs = qs.filter(is_active=True)
    return qs


def get_printer_by_id(printer_id: str) -> "Printer | None":
    """Retorna una impresora por su ID."""
    return Printer.objects.filter(id=printer_id).first()
