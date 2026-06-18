import logging
import os
import sys

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"
    verbose_name = "Orders"

    def ready(self) -> None:
        """Inicia el scheduler cuando el servidor está corriendo."""
        # No arrancar durante tests, migraciones, u otros comandos de gestión
        skip_commands = {
            "test",
            "makemigrations",
            "migrate",
            "shell",
            "createsuperuser",
            "seed_initial_data",
            "check",
            "collectstatic",
            "showmigrations",
            "sqlmigrate",
        }
        if any(arg in skip_commands for arg in sys.argv):
            return

        # En el dev server, Django inicia dos procesos: reloader (padre) y worker (hijo).
        # RUN_MAIN='true' identifica el proceso worker real — solo ahí debe arrancar el scheduler.
        is_dev_server = "runserver" in sys.argv
        if is_dev_server and os.environ.get("RUN_MAIN") != "true":
            return

        # En producción (gunicorn/uvicorn), activar explícitamente con SCHEDULER_AUTOSTART=true.
        is_production_server = os.environ.get("SCHEDULER_AUTOSTART") == "true"
        if not is_dev_server and not is_production_server:
            return

        try:
            import scheduler as sched

            sched.start()
        except Exception as exc:
            logger.warning("No se pudo iniciar el scheduler: %s", exc)
