from django.db import models
from Bocar import settings


class RFQ_Trimming(models.Model):

    # Renombrado de Roles a Status — describe estados del registro, no roles de usuario
    class Status(models.TextChoices):
        INDUSTRIALIZACION = 'En_Ind', 'En Industrialización'
        COMERCIALIZACION  = 'En_Com', 'En Comercialización'
        PROVEEDOR         = 'En_Pro', 'En Proveedor'

    # ─── Info General ──────────────────────────────────────────────────────────
    status         = models.CharField(max_length=10, default=Status.INDUSTRIALIZACION, choices=Status.choices)
    created_by     = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True,
                        related_name='rfq_trimmings_created'
                     )
    created_date   = models.DateTimeField(auto_now_add=True, editable=False)
    due_date       = models.DateField()
    complete       = models.BooleanField(default=False)
    logical_delete = models.BooleanField(default=False)

    # ─── Datos primera parte ───────────────────────────────────────────────────
    DESC = models.CharField(max_length=255, blank=True, default="")
    PPY  = models.FloatField(default=0.0)
    CUST = models.CharField(max_length=100, blank=True, default="")
    PNUM = models.CharField(max_length=100, blank=True, default="")
    PRLF = models.FloatField(default=0.0)
    DTQ  = models.DateField(null=True, blank=True)

    # ─── DCM ───────────────────────────────────────────────────────────────────
    press                            = models.CharField(max_length=100, blank=True, default="")
    no_of_cavities                   = models.IntegerField(null=True, blank=True)
    no_of_hydraulic_slides           = models.CharField(max_length=100, blank=True, default="", help_text='Defined by toolmaker')
    fully_automatic_process          = models.CharField(max_length=100, blank=True, default="")
    presence_detectors               = models.CharField(max_length=100, blank=True, default="")
    trimming_process_condition       = models.CharField(max_length=100, blank=True, default="")
    admissible_residual_burr_mm      = models.FloatField(null=True, blank=True)
    castings_supplied_by_auma        = models.CharField(max_length=100, blank=True, default="")
    adjustments_optimization_at_tool = models.CharField(max_length=100, blank=True, default="")
    gas_springs                      = models.CharField(max_length=100, blank=True, default="", help_text='Defined by toolmaker')

    # ─── Data Information Required in the price of the Trim Die ───────────────
    di_design_3d_model                   = models.BooleanField(default=False)
    di_design_3d_model_note              = models.CharField(max_length=250, blank=True, default="")
    di_design_2d_data                    = models.BooleanField(default=False)
    di_design_2d_data_note               = models.CharField(max_length=250, blank=True, default="")
    di_punch_pins_data                   = models.BooleanField(default=False)
    di_punch_pins_data_note              = models.CharField(max_length=250, blank=True, default="")
    di_manufacturing_proposals           = models.BooleanField(default=False)
    di_manufacturing_proposals_note      = models.CharField(max_length=250, blank=True, default="")
    di_latest_trim_die_improvements      = models.BooleanField(default=False)
    di_latest_trim_die_improvements_note = models.CharField(max_length=250, blank=True, default="")
    di_sketch_trim_die_concept           = models.BooleanField(default=False)
    di_sketch_trim_die_concept_note      = models.CharField(max_length=250, blank=True, default="")
    di_trim_die_no1                      = models.BooleanField(default=False)
    di_trim_die_no1_note                 = models.CharField(max_length=250, blank=True, default="")
    di_trim_die_no2                      = models.BooleanField(default=False)
    di_trim_die_no2_note                 = models.CharField(max_length=250, blank=True, default="")
    di_set_of_spare_parts                = models.BooleanField(default=False)
    di_set_of_spare_parts_note           = models.CharField(max_length=250, blank=True, default="")
    di_hydraulic_cylinders_limit_sw      = models.BooleanField(default=False)
    di_hydraulic_cylinders_limit_sw_note = models.CharField(max_length=250, blank=True, default="")

    # ─── Other Information ─────────────────────────────────────────────────────
    oi_frame_refurbishment       = models.BooleanField(default=False)
    oi_set_of_electric_wires     = models.BooleanField(default=False)
    oi_others                    = models.CharField(max_length=255, blank=True, default="")
    oi_delivery_date_imex        = models.DateField(null=True, blank=True)
    oi_ejector_system_fixed_side = models.CharField(max_length=100, blank=True, default="")

    # ─── Part Geometry ─────────────────────────────────────────────────────────
    part_name   = models.CharField(max_length=255, blank=True, default="")
    part_number = models.CharField(max_length=100, blank=True, default="")

    part_dim_length_mm    = models.FloatField(null=True, blank=True)
    part_dim_width_mm     = models.FloatField(null=True, blank=True)
    part_dim_height_mm    = models.FloatField(null=True, blank=True)
    min_wall_thickness_mm = models.FloatField(null=True, blank=True)
    max_wall_thickness_mm = models.FloatField(null=True, blank=True)
    projected_area_cm2    = models.FloatField(null=True, blank=True)
    surface_cm2           = models.FloatField(null=True, blank=True)
    volume_cm3            = models.FloatField(null=True, blank=True)
    gross_weight_g        = models.FloatField(null=True, blank=True)

    # ─── Tool Specification ────────────────────────────────────────────────────
    press_type                      = models.CharField(max_length=100, blank=True, default="")
    introduction_extraction_process = models.CharField(max_length=100, blank=True, default="")
    biscuit_position                = models.CharField(max_length=100, blank=True, default="")
    quantity_of_punch_pins          = models.CharField(max_length=100, blank=True, default="", help_text='Número o Defined by toolmaker')
    temperature_when_trimmed        = models.CharField(max_length=100, blank=True, default="")

    comments = models.TextField(blank=True, default="")

    def __str__(self):
        return f"RFQ Trimming {self.id} - {self.status}"

    class Meta:
        db_table = 'RFQ_Trimming'
        verbose_name = 'RFQ Trimming'
        verbose_name_plural = 'RFQs Trimming'
        ordering = ['-created_date']


# ─────────────────────────────────────────────────────────────────────────────
# Archivos adjuntos al RFQ_Trimming
# ─────────────────────────────────────────────────────────────────────────────
class RFQ_Trimming_File(models.Model):
    rfq_trimming = models.ForeignKey(
        RFQ_Trimming,
        on_delete=models.CASCADE,
        related_name='archivos'         # rfq_trimming.archivos.all()
    )
    archivo     = models.FileField(upload_to='Files/RFQ_Trimming/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Archivo {self.id} de RFQ_Trimming {self.rfq_trimming.id}"

    class Meta:
        verbose_name = 'Archivo RFQ Trimming'
        verbose_name_plural = 'Archivos RFQ Trimming'
        ordering = ['uploaded_at']


# ─────────────────────────────────────────────────────────────────────────────
# Solicitudes de edición (regresar de En_Com a En_Ind)
# ─────────────────────────────────────────────────────────────────────────────
class RFQ_Trimming_EditRequest(models.Model):

    class EditStatus(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        APROBADA  = 'Aprobada',  'Aprobada'
        RECHAZADA = 'Rechazada', 'Rechazada'

    rfq_trimming = models.ForeignKey(
        RFQ_Trimming,
        on_delete=models.CASCADE,
        related_name='edit_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='trimming_edit_requests_made'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=20, choices=EditStatus.choices, default=EditStatus.PENDIENTE)
    reason       = models.TextField(blank=True, default="")

    # Se llena al momento de aprobar/rechazar
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='trimming_edit_requests_reviewed',
        null=True, blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"EditRequest {self.id} - Trimming {self.rfq_trimming.id} - {self.status}"

    class Meta:
        verbose_name = 'Solicitud de Edición Trimming'
        verbose_name_plural = 'Solicitudes de Edición Trimming'
        ordering = ['-requested_at']