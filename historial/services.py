import logging

from .models import RFQHistorial

logger = logging.getLogger(__name__)


def registrar_historial(*, rfq_tipo, rfq_id, evento, actor=None,
                        status_anterior='', status_nuevo='',
                        cambios=None, detalle=None):
    """Crea una entrada de historial para una RFQ.

    Es defensivo: un fallo al registrar el historial nunca debe romper la acción
    de negocio que lo dispara (se loggea y se continúa).
    """
    try:
        return RFQHistorial.objects.create(
            rfq_tipo        = rfq_tipo,
            rfq_id          = rfq_id,
            evento          = evento,
            actor           = actor,
            status_anterior = status_anterior or '',
            status_nuevo    = status_nuevo or '',
            cambios         = cambios or {},
            detalle         = detalle or {},
        )
    except Exception:
        logger.exception(
            'No se pudo registrar historial (%s) para %s #%s',
            evento, rfq_tipo, rfq_id,
        )
        return None


def diff_campos(instance, validated_data, excluir=('archivos',)):
    """Devuelve {campo: {'antes': x, 'despues': y}} para los campos que cambian.

    Compara los valores actuales de `instance` (antes de guardar) contra los
    nuevos en `validated_data`. Ignora los campos en `excluir` (p.ej. archivos)
    y los valores no serializables se convierten a str.
    """
    cambios = {}
    for campo, nuevo in validated_data.items():
        if campo in excluir:
            continue
        anterior = getattr(instance, campo, None)
        if anterior != nuevo:
            cambios[campo] = {
                'antes':   _serializable(anterior),
                'despues': _serializable(nuevo),
            }
    return cambios


def _serializable(valor):
    """Convierte valores no nativos de JSON (date, Decimal, etc.) a algo serializable."""
    if valor is None or isinstance(valor, (str, int, float, bool)):
        return valor
    return str(valor)
