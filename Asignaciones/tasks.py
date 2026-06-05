from celery import shared_task

from .services import close_expired_assignments


@shared_task
def cerrar_asignaciones_vencidas():
    return close_expired_assignments()
