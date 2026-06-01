from django.db import models
from django.core.exceptions import ValidationError
from Bocar.settings import AUTH_USER_MODEL
from Proveedores.models import Proveedor
from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming


class ExtensionStatus(models.TextChoices):
    PENDIENTE = 'Pendiente', 'Pendiente'
    APROBADA  = 'Aprobada',  'Aprobada'
    RECHAZADA = 'Rechazada', 'Rechazada'


class Asignacion_Proveedor_Mold(models.Model):

    id_RFQ_Mold              = models.ForeignKey(RFQ_Mold, on_delete=models.CASCADE, related_name='asignaciones')
    id_Proveedor             = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='asignaciones_mold')
    id_user_comercializacion = models.ForeignKey(
                                AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='asignaciones_mold'
                               )

    fecha_de_asignacion = models.DateField(auto_now_add=True)
    due_date            = models.DateField()
    is_answered         = models.BooleanField(default=False)
    is_closed           = models.BooleanField(default=False)
    logical_delete      = models.BooleanField(default=False)

    def clean(self):
        # Valida que el usuario asignado tenga role='Com'
        # Se ejecuta automáticamente desde el Admin de Django
        if self.id_user_comercializacion.role != 'Com':
            raise ValidationError({
                'id_user_comercializacion': 'Solo se puede asignar a usuarios con rol Comercialización.'
            })

    def save(self, *args, **kwargs):
        # Forzamos clean() también al guardar por código o API
        # para que la validación aplique en todos los casos
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Asignacion Mold {self.id} - {self.id_Proveedor}"

    class Meta:
        db_table            = 'Asignacion_Proveedor_Mold'
        verbose_name        = 'Asignación Proveedor Mold'
        verbose_name_plural = 'Asignaciones Proveedor Mold'


class Asignacion_Proveedor_Trimming(models.Model):

    id_RFQ_Trimming          = models.ForeignKey(RFQ_Trimming, on_delete=models.CASCADE, related_name='asignaciones')
    id_Proveedor             = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='asignaciones_trimming')
    id_user_comercializacion = models.ForeignKey(
                                AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='asignaciones_trimming'
                               )

    fecha_de_asignacion = models.DateField(auto_now_add=True)
    due_date            = models.DateField()
    is_answered         = models.BooleanField(default=False)
    is_closed           = models.BooleanField(default=False)
    logical_delete      = models.BooleanField(default=False)

    def clean(self):
        # Valida que el usuario asignado tenga role='Com'
        # Se ejecuta automáticamente desde el Admin de Django
        if self.id_user_comercializacion.role != 'Com':
            raise ValidationError({
                'id_user_comercializacion': 'Solo se puede asignar a usuarios con rol Comercialización.'
            })

    def save(self, *args, **kwargs):
        # Forzamos clean() también al guardar por código o API
        # para que la validación aplique en todos los casos
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Asignacion Trimming {self.id} - {self.id_Proveedor}"

    class Meta:
        db_table            = 'Asignacion_Proveedor_Trimming'
        verbose_name        = 'Asignación Proveedor Trimming'
        verbose_name_plural = 'Asignaciones Proveedor Trimming'


# ─────────────────────────────────────────────────────────────────────────────
# SOLICITUDES DE EXTENSIÓN DE TIEMPO
# ─────────────────────────────────────────────────────────────────────────────

class SolicitudExtensionMold(models.Model):

    id_asignacion = models.ForeignKey(
        Asignacion_Proveedor_Mold,
        on_delete=models.CASCADE,
        related_name='solicitudes_extension',
    )
    motivo        = models.TextField()
    nueva_fecha   = models.DateField()
    status        = models.CharField(
        max_length=10,
        choices=ExtensionStatus.choices,
        default=ExtensionStatus.PENDIENTE,
    )
    solicitada_at = models.DateTimeField(auto_now_add=True)
    revisada_por  = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='extensiones_mold_revisadas',
    )
    revisada_at   = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'ExtensionMold {self.id} - Asignacion {self.id_asignacion_id} [{self.status}]'

    class Meta:
        db_table            = 'Solicitud_Extension_Mold'
        verbose_name        = 'Solicitud de Extensión Mold'
        verbose_name_plural = 'Solicitudes de Extensión Mold'


class SolicitudExtensionTrimming(models.Model):

    id_asignacion = models.ForeignKey(
        Asignacion_Proveedor_Trimming,
        on_delete=models.CASCADE,
        related_name='solicitudes_extension',
    )
    motivo        = models.TextField()
    nueva_fecha   = models.DateField()
    status        = models.CharField(
        max_length=10,
        choices=ExtensionStatus.choices,
        default=ExtensionStatus.PENDIENTE,
    )
    solicitada_at = models.DateTimeField(auto_now_add=True)
    revisada_por  = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='extensiones_trimming_revisadas',
    )
    revisada_at   = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'ExtensionTrimming {self.id} - Asignacion {self.id_asignacion_id} [{self.status}]'

    class Meta:
        db_table            = 'Solicitud_Extension_Trimming'
        verbose_name        = 'Solicitud de Extensión Trimming'
        verbose_name_plural = 'Solicitudes de Extensión Trimming'