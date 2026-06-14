"""
Configuración del scheduler de Imprint Studio.

Usa APScheduler con DjangoJobStore para persistir jobs en la base de datos.
Iniciar llamando a start() desde OrdersConfig.ready().
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def start() -> None:
    """Inicia el scheduler y registra todos los jobs. Idempotente."""
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        return

    from apps.orders.jobs import cancel_expired_deposits

    _scheduler = BackgroundScheduler(timezone="America/Mexico_City")
    _scheduler.add_jobstore(DjangoJobStore(), "default")

    _scheduler.add_job(
        cancel_expired_deposits,
        trigger="interval",
        hours=1,
        id="cancel_expired_deposits",
        name="Cancelar anticipos vencidos",
        replace_existing=True,
        jobstore="default",
        max_instances=1,
        coalesce=True,
    )

    _scheduler.start()
    logger.info("Scheduler iniciado — job: cancel_expired_deposits (cada hora).")
