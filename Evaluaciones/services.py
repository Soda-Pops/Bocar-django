"""
Lógica de negocio para el módulo de evaluación de proveedores.

Métricas automáticas (derivadas de datos existentes):
  - fue_puntual / dias_diferencia : compara due_date vs fecha de envío del cost breakdown
  - solicito_extension            : ¿hubo alguna SolicitudExtension para esta asignación?
  - cotizacion_enviada            : ¿el cost breakdown llegó a status='submitted'?

Calificación manual (ingresada por Compras):
  - calidad_cotizacion (1–5)
  - comunicacion (1–5)

Fórmula ponderada (escala 0–5):
  puntualidad          40 %
  calidad_cotizacion   30 %
  comunicacion         20 %
  sin_extensiones      10 %
"""

import logging
from datetime import date

from django.db.models import Avg

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# MÉTRICAS AUTOMÁTICAS
# ─────────────────────────────────────────────────────────────────────────────

def calcular_metricas(asignacion_tipo: str, asignacion_id: int) -> dict:
    """
    Devuelve un dict con las métricas objetivas de una asignación.

    {
        'fue_puntual':        bool,
        'dias_diferencia':    int,   # negativo = entregó antes, positivo = tarde
        'solicito_extension': bool,
        'cotizacion_enviada': bool,
    }
    """
    from Asignaciones.models import (
        Asignacion_Proveedor_Mold,
        Asignacion_Proveedor_Trimming,
        SolicitudExtensionMold,
        SolicitudExtensionTrimming,
    )
    from Prov_RFQ_Mold.models import Cost_Breakdown_Mold
    from Prov_RFQ_Trimming.models import Cost_Breakdown_Trimming

    if asignacion_tipo == 'mold':
        asignacion = Asignacion_Proveedor_Mold.objects.get(id=asignacion_id)
        tuvo_extension = SolicitudExtensionMold.objects.filter(
            id_asignacion=asignacion
        ).exists()
        try:
            breakdown = Cost_Breakdown_Mold.objects.get(id_asignacion=asignacion)
            enviada = breakdown.status == Cost_Breakdown_Mold.Status.SUBMITTED
            fecha_envio = breakdown.last_change.date() if enviada else None
        except Cost_Breakdown_Mold.DoesNotExist:
            enviada = False
            fecha_envio = None
    else:
        asignacion = Asignacion_Proveedor_Trimming.objects.get(id=asignacion_id)
        tuvo_extension = SolicitudExtensionTrimming.objects.filter(
            id_asignacion=asignacion
        ).exists()
        try:
            breakdown = Cost_Breakdown_Trimming.objects.get(id_asignacion=asignacion)
            enviada = breakdown.status == Cost_Breakdown_Trimming.Status.SUBMITTED
            fecha_envio = breakdown.last_change.date() if enviada else None
        except Cost_Breakdown_Trimming.DoesNotExist:
            enviada = False
            fecha_envio = None

    due_date = asignacion.due_date

    if enviada and fecha_envio:
        dias_diferencia = (fecha_envio - due_date).days
        fue_puntual = dias_diferencia <= 0
    else:
        # No respondió: se considera completamente tarde
        dias_diferencia = (date.today() - due_date).days
        fue_puntual = False

    return {
        'fue_puntual':        fue_puntual,
        'dias_diferencia':    dias_diferencia,
        'solicito_extension': tuvo_extension,
        'cotizacion_enviada': enviada,
    }


# ─────────────────────────────────────────────────────────────────────────────
# FÓRMULA DE SCORE
# ─────────────────────────────────────────────────────────────────────────────

def calcular_score(
    fue_puntual: bool,
    dias_diferencia: int,
    solicito_extension: bool,
    cotizacion_enviada: bool,
    calidad_cotizacion: int,
    comunicacion: int,
) -> float:
    """
    Calcula el score ponderado de una evaluación en escala 0.0–5.0.

    Puntualidad (40 %):
      - No envió cotización : 0
      - Puntual (dias <= 0) : 5
      - Tardío              : max(0, 5 - dias_diferencia * 0.5)  — pierde 0.5 por día

    Sin extensiones (10 %):
      - No solicitó         : 5
      - Solicitó            : 0

    Calidad cotización (30 %) y comunicación (20 %) : valor directo (1–5).
    """
    if not cotizacion_enviada:
        puntualidad = 0.0
    elif fue_puntual:
        puntualidad = 5.0
    else:
        puntualidad = max(0.0, 5.0 - dias_diferencia * 0.5)

    sin_extension = 0.0 if solicito_extension else 5.0

    score = (
        puntualidad        * 0.40 +
        float(calidad_cotizacion) * 0.30 +
        float(comunicacion)       * 0.20 +
        sin_extension      * 0.10
    )
    return round(min(score, 5.0), 2)


# ─────────────────────────────────────────────────────────────────────────────
# RECALCULAR RATING DEL PROVEEDOR
# ─────────────────────────────────────────────────────────────────────────────

def recalcular_rating_proveedor(proveedor) -> float:
    """
    Actualiza Proveedor.rating con el promedio de todos sus scores.
    Devuelve el nuevo rating.
    """
    from .models import EvaluacionProveedor

    resultado = EvaluacionProveedor.objects.filter(
        id_proveedor=proveedor
    ).aggregate(promedio=Avg('score'))

    nuevo_rating = round(resultado['promedio'] or 0.0, 2)
    proveedor.rating = nuevo_rating
    proveedor.save(update_fields=['rating'])
    return nuevo_rating
