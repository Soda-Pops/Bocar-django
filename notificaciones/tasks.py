from celery import shared_task

from . import services


# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _get_rfq(rfq_id, rfq_tipo):
    if rfq_tipo == 'mold':
        from RFQ_Mold.models import RFQ_Mold
        return RFQ_Mold.objects.get(id=rfq_id)
    from RFQ_Trimming.models import RFQ_Trimming
    return RFQ_Trimming.objects.get(id=rfq_id)


def _get_user(user_id):
    from users.models import CustomUser
    return CustomUser.objects.get(id=user_id)


# ─────────────────────────────────────────────────────────────────────────────
# TAREAS CELERY
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notificar_comercializacion(self, rfq_id, rfq_tipo):
    try:
        services.notificar_comercializacion(_get_rfq(rfq_id, rfq_tipo))
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notificar_proveedores(self, rfq_id, rfq_tipo):
    try:
        services.notificar_proveedores(_get_rfq(rfq_id, rfq_tipo))
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notificar_cotizacion_recibida(self, rfq_id, rfq_tipo, proveedor_id):
    try:
        services.notificar_cotizacion_recibida(
            _get_rfq(rfq_id, rfq_tipo),
            _get_user(proveedor_id),
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notificar_cancelacion_solicitada(self, rfq_id, rfq_tipo, solicitante_id, motivo=''):
    try:
        services.notificar_cancelacion_solicitada(
            _get_rfq(rfq_id, rfq_tipo),
            _get_user(solicitante_id),
            motivo,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notificar_cancelacion_confirmada(self, rfq_id, rfq_tipo, cancelado_por_id, motivo=''):
    try:
        services.notificar_cancelacion_confirmada(
            _get_rfq(rfq_id, rfq_tipo),
            _get_user(cancelado_por_id),
            motivo,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notificar_modificacion_rfq(self, rfq_id, rfq_tipo, modificado_por_id, roles_destino):
    try:
        services.notificar_modificacion_rfq(
            _get_rfq(rfq_id, rfq_tipo),
            _get_user(modificado_por_id),
            roles_destino,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
