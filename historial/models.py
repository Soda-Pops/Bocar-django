from django.conf import settings
from django.db import models


class RFQHistorial(models.Model):
    """Registro de auditoría del ciclo de vida de una RFQ (Mold o Trimming).

    No usa FK directa al RFQ porque apunta a dos modelos distintos; se guarda
    el par (rfq_tipo, rfq_id). Cada fila es un evento del flujo.
    """

    class Tipo(models.TextChoices):
        MOLD     = 'mold',     'Mold'
        TRIMMING = 'trimming', 'Trimming'

    class Evento(models.TextChoices):
        CREACION              = 'CREACION',              'RFQ creada'
        EDICION               = 'EDICION',               'RFQ editada'
        ENVIO_COMERCIALIZACION = 'ENVIO_COMERCIALIZACION', 'Enviada a Comercialización'
        ENVIO_PROVEEDORES     = 'ENVIO_PROVEEDORES',     'Enviada a Proveedores'
        ASIGNACION_PROVEEDORES = 'ASIGNACION_PROVEEDORES', 'Proveedores asignados'
        SOLICITUD_EDICION     = 'SOLICITUD_EDICION',     'Solicitud de edición'
        EDICION_APROBADA      = 'EDICION_APROBADA',      'Solicitud de edición aprobada'
        EDICION_RECHAZADA     = 'EDICION_RECHAZADA',     'Solicitud de edición rechazada'
        COTIZACION_RECIBIDA   = 'COTIZACION_RECIBIDA',   'Cotización recibida'
        CANCELACION           = 'CANCELACION',           'RFQ cancelada'
        EXTENSION_SOLICITADA  = 'EXTENSION_SOLICITADA',  'Extensión de tiempo solicitada'
        EXTENSION_APROBADA    = 'EXTENSION_APROBADA',    'Extensión de tiempo aprobada'
        EXTENSION_RECHAZADA   = 'EXTENSION_RECHAZADA',   'Extensión de tiempo rechazada'
        EVALUACION_PROVEEDOR  = 'EVALUACION_PROVEEDOR',  'Proveedor evaluado por Compras'
        CIERRE_RFQ            = 'CIERRE_RFQ',            'RFQ cerrada formalmente'

    rfq_tipo = models.CharField(max_length=10, choices=Tipo.choices)
    rfq_id   = models.PositiveIntegerField()
    evento   = models.CharField(max_length=30, choices=Evento.choices)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='eventos_historial',
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    status_anterior = models.CharField(max_length=20, blank=True, default='')
    status_nuevo    = models.CharField(max_length=20, blank=True, default='')

    # Diff de campos en ediciones: {campo: {'antes': x, 'despues': y}}
    cambios = models.JSONField(default=dict, blank=True)
    # Contexto extra: motivo, proveedores, nueva_fecha, proveedor, etc.
    detalle = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.rfq_tipo} #{self.rfq_id} - {self.evento} - {self.timestamp:%Y-%m-%d %H:%M}'

    class Meta:
        db_table            = 'RFQ_Historial'
        verbose_name        = 'Evento de historial RFQ'
        verbose_name_plural = 'Historial de RFQs'
        ordering            = ['-timestamp']
        indexes = [
            models.Index(fields=['rfq_tipo', 'rfq_id']),
        ]
