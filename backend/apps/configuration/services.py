"""
Servicios para la app configuration.
Toda la lógica de actualización de configuración vive aquí.
"""
from django.db import transaction

from . import selectors
from .models import BusinessConfig, BusinessHours, Holiday, PaymentInstructions, Printer


class ConfigurationService:

    @staticmethod
    @transaction.atomic
    def update_business_config(data: dict) -> BusinessConfig:
        """Actualiza la configuración activa del negocio."""
        config = selectors.get_active_business_config()
        if not config:
            raise ValueError("No existe configuración activa.")

        for field, value in data.items():
            setattr(config, field, value)
        config.save()
        return config

    @staticmethod
    @transaction.atomic
    def update_business_hours(weekday: int, data: dict) -> BusinessHours:
        """Actualiza el horario de un día específico de la semana."""
        hours = selectors.get_business_hours_by_weekday(weekday)
        if not hours:
            raise ValueError(f"No existe horario para el día {weekday}.")

        for field, value in data.items():
            setattr(hours, field, value)
        hours.save()
        return hours

    @staticmethod
    @transaction.atomic
    def create_holiday(data: dict) -> Holiday:
        """Crea un día festivo."""
        if Holiday.objects.filter(holiday_date=data["holiday_date"]).exists():
            raise ValueError("Ya existe un día festivo para esa fecha.")
        return Holiday.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def delete_holiday(holiday_id: str) -> None:
        """Elimina un día festivo."""
        holiday = selectors.get_holiday_by_id(holiday_id)
        if not holiday:
            raise ValueError("Día festivo no encontrado.")
        holiday.delete()

    @staticmethod
    @transaction.atomic
    def update_payment_instructions(data: dict) -> PaymentInstructions:
        """Actualiza las instrucciones de pago activas."""
        instructions = selectors.get_active_payment_instructions()
        if not instructions:
            raise ValueError("No existen instrucciones de pago activas.")

        for field, value in data.items():
            setattr(instructions, field, value)
        instructions.save()
        return instructions

    @staticmethod
    @transaction.atomic
    def create_printer(data: dict) -> Printer:
        """Crea una nueva impresora en el catálogo."""
        return Printer.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update_printer(printer_id: str, data: dict) -> Printer:
        """Actualiza los datos de una impresora."""
        printer = selectors.get_printer_by_id(printer_id)
        if not printer:
            raise ValueError("Impresora no encontrada.")
        for field, value in data.items():
            setattr(printer, field, value)
        printer.save()
        return printer

    @staticmethod
    @transaction.atomic
    def delete_printer(printer_id: str) -> None:
        """Elimina una impresora del catálogo."""
        printer = selectors.get_printer_by_id(printer_id)
        if not printer:
            raise ValueError("Impresora no encontrada.")
        printer.delete()
