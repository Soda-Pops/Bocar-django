from django.db import models
from Bocar import settings


# ─────────────────────────────────────────────────────────────────────────────
# MODELO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
class RFQ_Mold(models.Model):

    class Status(models.TextChoices):
        INDUSTRIALIZACION = 'En_Ind', 'En Industrialización'
        COMERCIALIZACION  = 'En_Com', 'En Comercialización'
        PROVEEDOR         = 'En_Pro', 'En Proveedor'

    # ─── Info general ──────────────────────────────────────────────────────────
    status         = models.CharField(max_length=10, default=Status.INDUSTRIALIZACION, choices=Status.choices)
    created_by     = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.PROTECT,
                        related_name='rfq_molds_created',
                    )
    created_date   = models.DateTimeField(auto_now_add=True, editable=False)
    due_date       = models.DateField()
    complete       = models.BooleanField(default=False)
    logical_delete = models.BooleanField(default=False)

    # ─── Cierre formal ────────────────────────────────────────────────────────
    closed_at      = models.DateTimeField(null=True, blank=True)
    closed_by      = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='rfq_molds_closed',
                    )
    closure_reason = models.TextField(blank=True, default='')

    # ─── Datos primera parte ───────────────────────────────────────────────────
    DESC  = models.CharField(max_length=255, blank=True, default="")
    PPY   = models.FloatField(default=0.0)
    CUST  = models.CharField(max_length=100, blank=True, default="")
    PT    = models.CharField(max_length=100, blank=True, default="")
    PNUM  = models.CharField(max_length=100, blank=True, default="")
    PRLF  = models.FloatField(default=0.0)
    TT    = models.CharField(max_length=100, blank=True, default="")
    DTQ   = models.DateField(blank=True, null=True)
    ELAB  = models.CharField(max_length=255, blank=True, default="")

    # ─── DCM ───────────────────────────────────────────────────────────────────
    SMACH         = models.CharField(max_length=100, blank=True, default="")
    No_CAV        = models.CharField(max_length=100, blank=True, default="")
    No_ofHS       = models.FloatField(blank=True, default=0.0)
    No_ofMS       = models.FloatField(blank=True, default=0.0)
    ThirdPSupp    = models.CharField(max_length=100, blank=True, default="")
    No_subc       = models.CharField(max_length=100, blank=True, default="")
    Jco           = models.CharField(max_length=100, blank=True, default="")
    QcSys         = models.CharField(max_length=100, blank=True, default="")
    Ihtcs         = models.CharField(max_length=100, blank=True, default="")
    Spin          = models.CharField(max_length=100, blank=True, default="")
    HICS          = models.CharField(max_length=100, blank=True, default="")
    CMGOM         = models.CharField(max_length=100, blank=True, default="")
    SPforThermoR  = models.CharField(max_length=100, blank=True, default="")
    NReturnV      = models.CharField(max_length=100, blank=True, default="")
    VacV          = models.CharField(max_length=100, blank=True, default="")
    ChillBl       = models.CharField(max_length=100, blank=True, default="")
    No_Pl_Jco_sys = models.CharField(max_length=100, blank=True, default="")
    Oth           = models.CharField(max_length=100, blank=True, default="")

    # ─── DATA INFORMATION REQUIRED IN THE PRICE OF THE DIE ────────────────────
    D_3D                         = models.BooleanField(default=False)
    D_3D_note                    = models.CharField(max_length=250, blank=True, default="")
    FlAn                         = models.BooleanField(default=False)
    FlAn_note                    = models.CharField(max_length=250, blank=True, default="")
    Run_des                      = models.BooleanField(default=False)
    Run_des_note                 = models.CharField(max_length=250, blank=True, default="")
    Run_and_over_mod             = models.BooleanField(default=False)
    Run_and_over_mod_note        = models.CharField(max_length=250, blank=True, default="")
    ManProp                      = models.BooleanField(default=False)
    ManProp_note                 = models.CharField(max_length=250, blank=True, default="")
    Ldi                          = models.BooleanField(default=False)
    Ldi_note                     = models.CharField(max_length=250, blank=True, default="")
    Add_of_mach_st               = models.BooleanField(default=False)
    Add_of_mach_st_note          = models.CharField(max_length=250, blank=True, default="")
    Sketch_d_conc_inc_s_dim      = models.BooleanField(default=False)
    Sketch_d_conc_inc_s_dim_note = models.CharField(max_length=250, blank=True, default="")
    D2_Dr_Des_PDF_CNF            = models.BooleanField(default=False)
    D2_Dr_Des_PDF_CNF_note       = models.CharField(max_length=250, blank=True, default="")
    D3_Mod_solid_Native          = models.BooleanField(default=False)
    D3_Mod_solid_Native_note     = models.CharField(max_length=250, blank=True, default="")

    # ─── OT INF ────────────────────────────────────────────────────────────────
    Comp_Die             = models.BooleanField(default=False)
    Comp_Die_note        = models.CharField(max_length=250, blank=True, default="")
    Subseq_D             = models.BooleanField(default=False)
    Subseq_D_note        = models.CharField(max_length=250, blank=True, default="")
    Set_of_repl_H13      = models.BooleanField(default=False)
    Set_of_repl_H13_note = models.CharField(max_length=250, blank=True, default="")
    Sp_set_of_EI         = models.BooleanField(default=False)
    Sp_set_of_EI_note    = models.CharField(max_length=250, blank=True, default="")
    FICF                 = models.BooleanField(default=False)
    FICF_note            = models.CharField(max_length=250, blank=True, default="")
    HCLS                 = models.BooleanField(default=False)
    HCLS_note            = models.CharField(max_length=250, blank=True, default="")
    Fr_Refur             = models.BooleanField(default=False)
    Fr_Refur_note        = models.CharField(max_length=250, blank=True, default="")

    # ─── OTHER Information ─────────────────────────────────────────────────────
    Eyeb                 = models.BooleanField(default=False)
    Eyeb_note            = models.CharField(max_length=250, blank=True, default="")
    Oil_Water_Conn       = models.BooleanField(default=False)
    Oil_Water_Conn_note  = models.CharField(max_length=250, blank=True, default="")
    STM_1and2            = models.BooleanField(default=False)
    STM_1and2_note       = models.CharField(max_length=250, blank=True, default="")
    CMM_dim_rep_cai      = models.BooleanField(default=False)
    CMM_dim_rep_cai_note = models.CharField(max_length=250, blank=True, default="")
    GOM_rep_ass          = models.BooleanField(default=False)
    GOM_rep_ass_note     = models.CharField(max_length=250, blank=True, default="")
    H_val_subc_in        = models.BooleanField(default=False)
    H_val_subc_in_note   = models.CharField(max_length=250, blank=True, default="")
    Dim_corr_opt         = models.BooleanField(default=False)
    Dim_corr_opt_note    = models.CharField(max_length=250, blank=True, default="")
    Sp_Pt                = models.BooleanField(default=False)
    Sp_Pt_note           = models.CharField(max_length=250, blank=True, default="")

    # ─── Part Geometry ─────────────────────────────────────────────────────────
    alloy                 = models.CharField(max_length=100, blank=True, default="")
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
    number_of_gates_per_part   = models.IntegerField(null=True, blank=True)
    number_of_parts_per_stroke = models.IntegerField(null=True, blank=True)
    number_of_tools            = models.IntegerField(null=True, blank=True)

    comments = models.TextField(blank=True, default="")

    def __str__(self):
        return f"RFQ_Mold {self.id} - {self.status}"

    class Meta:
        verbose_name        = 'RFQ Mold'
        verbose_name_plural = 'RFQ Molds'
        ordering            = ['-created_date']


# ─────────────────────────────────────────────────────────────────────────────
# ARCHIVOS ADJUNTOS
# ─────────────────────────────────────────────────────────────────────────────
class RFQ_Mold_File(models.Model):
    rfq_mold    = models.ForeignKey(
                    RFQ_Mold,
                    on_delete=models.CASCADE,
                    related_name='archivos'     # rfq_mold.archivos.all()
                  )
    archivo     = models.FileField(upload_to='Files/RFQ_Mold/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Archivo {self.id} de RFQ_Mold {self.rfq_mold.id}"

    class Meta:
        verbose_name        = 'Archivo RFQ Mold'
        verbose_name_plural = 'Archivos RFQ Mold'
        ordering            = ['uploaded_at']


# ─────────────────────────────────────────────────────────────────────────────
# SOLICITUDES DE EDICIÓN
# Guarda cada vez que alguien pide regresar el RFQ de En_Com a En_Ind
# ─────────────────────────────────────────────────────────────────────────────
class RFQ_Mold_EditRequest(models.Model):

    class EditStatus(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        APROBADA  = 'Aprobada',  'Aprobada'
        RECHAZADA = 'Rechazada', 'Rechazada'

    rfq_mold     = models.ForeignKey(
                    RFQ_Mold,
                    on_delete=models.CASCADE,
                    related_name='edit_requests'
                   )
    requested_by = models.ForeignKey(
                    settings.AUTH_USER_MODEL,
                    on_delete=models.PROTECT,
                    related_name='mold_edit_requests_made'
                   )
    requested_at = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=20, choices=EditStatus.choices, default=EditStatus.PENDIENTE)
    reason       = models.TextField(blank=True, default="")

    # Se llena al aprobar — null mientras esté pendiente
    reviewed_by  = models.ForeignKey(
                    settings.AUTH_USER_MODEL,
                    on_delete=models.PROTECT,
                    related_name='mold_edit_requests_reviewed',
                    null=True, blank=True
                   )
    reviewed_at  = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"EditRequest {self.id} - Mold {self.rfq_mold.id} - {self.status}"

    class Meta:
        verbose_name        = 'Solicitud de Edición Mold'
        verbose_name_plural = 'Solicitudes de Edición Mold'
        ordering            = ['-requested_at']