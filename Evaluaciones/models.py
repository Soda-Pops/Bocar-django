from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from Proveedores.models import Proveedor


class EvaluacionProveedor(models.Model):

    class TipoAsignacion(models.TextChoices):
        MOLD     = 'mold',     'Mold'
        TRIMMING = 'trimming', 'Trimming'

    # Apunta a Asignacion_Proveedor_Mold o Trimming sin FK directa
    # (mismo patrón que RFQHistorial)
    asignacion_tipo = models.CharField(max_length=10, choices=TipoAsignacion.choices)
    asignacion_id   = models.PositiveIntegerField()

    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='evaluaciones',
    )
    evaluado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evaluaciones_realizadas',
    )
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)

    # ── Métricas automáticas ───────────────────────────────────────────────
    fue_puntual        = models.BooleanField(default=False)
    # Negativo = entregó antes, positivo = entregó tarde (en días)
    dias_diferencia    = models.IntegerField(default=0)
    solicito_extension = models.BooleanField(default=False)
    cotizacion_enviada = models.BooleanField(default=False)

    # ── Calificación manual de Compras (1–5) ──────────────────────────────
    calidad_cotizacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comunicacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentarios = models.TextField(blank=True, default='')

    # ── Score ponderado final (0.0–5.0) ───────────────────────────────────
    score = models.FloatField(default=0.0)

    class Meta:
        db_table        = 'Evaluacion_Proveedor'
        verbose_name    = 'Evaluación de Proveedor'
        verbose_name_plural = 'Evaluaciones de Proveedores'
        # Una sola evaluación por asignación
        unique_together = [('asignacion_tipo', 'asignacion_id')]
        ordering        = ['-fecha_evaluacion']

    def __str__(self):
        return (
            f'Evaluación #{self.id} — {self.id_proveedor} '
            f'({self.asignacion_tipo} #{self.asignacion_id}) score={self.score:.2f}'
        )
