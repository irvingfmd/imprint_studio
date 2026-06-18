"""
Comando para cargar datos iniciales del sistema.
Equivalente a seed.sql pero usando el ORM de Django.
Ejecutar: python manage.py seed_initial_data
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Carga datos iniciales: business_config, business_hours, holidays, payment_instructions."

    def handle(self, *args, **options):
        self._seed_business_config()
        self._seed_business_hours()
        self._seed_holidays()
        self._seed_payment_instructions()
        self._seed_printers()
        self.stdout.write(self.style.SUCCESS("Datos iniciales cargados correctamente."))

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
            electricity_rate_kwh="2.0000",
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
        Actualizar con datos reales antes de producción.
        """
        from apps.configuration.models import PaymentInstructions

        if PaymentInstructions.objects.filter(is_active=True).exists():
            self.stdout.write("payment_instructions: ya existen, omitiendo.")
            return

        PaymentInstructions.objects.create(
            bank_name="BBVA",
            account_holder="Imprint Studio",
            additional_notes=(
                "Configurar datos bancarios reales antes de producción. "
                "El cliente debe enviar comprobante después de realizar la transferencia."
            ),
            is_active=True,
        )
        self.stdout.write("payment_instructions: creadas (datos placeholder, actualizar antes de producción).")

    def _seed_printers(self):
        """
        Crea el catálogo inicial de impresoras si no existe.
        Potencia en vatios según especificaciones oficiales de cada modelo.
        """
        from apps.configuration.models import Printer

        if Printer.objects.exists():
            self.stdout.write("printers: ya existen, omitiendo.")
            return

        # (marca, modelo, potencia promedio W, potencia máxima técnica W)
        impresoras = [
            ("Bambu Lab", "X1 Carbon", 350, 1000),
            ("Bambu Lab", "P1S", 350, 1000),
            ("Bambu Lab", "P1P", 300, 1000),
            ("Bambu Lab", "A1", 250, 800),
            ("Bambu Lab", "A1 Mini", 200, 500),
            ("Creality", "K1", 350, 1000),
            ("Creality", "K1 Max", 400, 1000),
            ("Creality", "Ender-3 V3 SE", 165, 350),
            ("Creality", "Ender-3 S1 Pro", 180, 350),
            ("Prusa", "MK4", 120, 280),
            ("Prusa", "MINI+", 90, 180),
            ("Anycubic", "Kobra 2 Pro", 250, 500),
        ]

        for brand, name, watts, max_watts in impresoras:
            Printer.objects.create(brand=brand, name=name, power_watts=watts, max_power_watts=max_watts)

        self.stdout.write(f"printers: {len(impresoras)} impresoras creadas.")
