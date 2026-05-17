from django.db import models
from Bocar import settings

# Create your models here.
class RFQ_Trimming(models.Model):
    class Roles(models.TextChoices):
        INDUSTRIALIZACION = 'En_Ind', 'En Industrialización'
        COMERCIALIZACION = 'En_Com', 'En Comercialización'
        PROVEEDOR = 'En_Pro', 'En Proveedor'
        
    # Info General
    status       = models.CharField (max_length=10, default= Roles.INDUSTRIALIZACION, choices=Roles.choices)
    created_by      = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True,
                        related_name='rfq_trimmings_created'
                    )
    created_date    = models.DateTimeField(auto_now_add=True, editable=False)
    due_date        = models.DateField()
    complete        = models.BooleanField(default=False)
    logical_delete  = models.BooleanField(default=False)

    # Datos primera parte
    DESC  = models.CharField(max_length=255,default="")
    PPY   = models.FloatField(default=0.0)
    CUST  = models.CharField(max_length=100, default="")
    PNUM  = models.CharField(max_length=100, default="")
    PRLF  = models.FloatField(default=0.0)
    DTQ   = models.DateField(null=True, blank=True)

    press                            = models.CharField(max_length=100, blank=True)
    no_of_cavities                   = models.IntegerField(null=True, blank=True)
    no_of_hydraulic_slides           = models.CharField(max_length=100, blank=True,
                                                        help_text='Defined by toolmaker')
    fully_automatic_process          = models.CharField(max_length=100, blank=True)
    presence_detectors               = models.CharField(max_length=100, blank=True)
    trimming_process_condition       = models.CharField(max_length=100, blank=True)                       
    admissible_residual_burr_mm      = models.FloatField(null=True, blank=True)
    castings_supplied_by_auma        = models.CharField(max_length=100, blank=True)
    adjustments_optimization_at_tool = models.CharField(max_length=100, blank=True)
    gas_springs                      = models.CharField(max_length=100, blank=True,
                                        help_text='Defined by toolmaker')

    # Data Information Required in the price of the Trim Die
    di_design_3d_model                    = models.BooleanField(default=False)
    di_design_3d_model_note               = models.CharField(max_length=250, blank=True,default="")

    di_design_2d_data                     = models.BooleanField(default=False)
    di_design_2d_data_note                = models.CharField(max_length=250, blank=True, default="")

    di_punch_pins_data                    = models.BooleanField(default=False)
    di_punch_pins_data_note               = models.CharField(max_length=250, blank=True, default="")

    di_manufacturing_proposals            = models.BooleanField(default=False)
    di_manufacturing_proposals_note       = models.CharField(max_length=250, blank=True, default="")

    di_latest_trim_die_improvements       = models.BooleanField(default=False)
    di_latest_trim_die_improvements_note  = models.CharField(max_length=250, blank=True, default="")

    di_sketch_trim_die_concept            = models.BooleanField(default=False)
    di_sketch_trim_die_concept_note       = models.CharField(max_length=250, blank=True, default="")

    di_trim_die_no1                       = models.BooleanField(default=False)
    di_trim_die_no1_note                  = models.CharField(max_length=250, blank=True, default="")

    di_trim_die_no2                       = models.BooleanField(default=False)
    di_trim_die_no2_note                  = models.CharField(max_length=250, blank=True, default="")

    di_set_of_spare_parts                 = models.BooleanField(default=False)
    di_set_of_spare_parts_note            = models.CharField(max_length=250, blank=True, default="")

    di_hydraulic_cylinders_limit_sw       = models.BooleanField(default=False)
    di_hydraulic_cylinders_limit_sw_note  = models.CharField(max_length=250, blank=True, default="")

    # Other Information
    oi_frame_refurbishment        = models.BooleanField(default=False)
    oi_set_of_electric_wires      = models.BooleanField(default=False)
    oi_others                     = models.CharField(max_length=255, blank=True, default="")
    oi_delivery_date_imex         = models.DateField(null=True, blank=True)
    oi_ejector_system_fixed_side  = models.CharField(max_length=100, blank=True, default="")
    #Complete shot sketch

    # Part Geometry
    part_name             = models.CharField(max_length=255, blank=True, default="")
    part_number           = models.CharField(max_length=100, blank=True)

    part_dim_length_mm    = models.FloatField(null=True, blank=True)
    part_dim_width_mm     = models.FloatField(null=True, blank=True)
    part_dim_height_mm    = models.FloatField(null=True, blank=True)

    min_wall_thickness_mm = models.FloatField(null=True, blank=True)
    max_wall_thickness_mm = models.FloatField(null=True, blank=True)
    projected_area_cm2    = models.FloatField(null=True, blank=True)
    surface_cm2           = models.FloatField(null=True, blank=True)
    volume_cm3            = models.FloatField(null=True, blank=True)
    gross_weight_g        = models.FloatField(null=True, blank=True)

    # Tool Specification
    press_type                      = models.CharField(max_length=100, blank=True)
    #Number of cavities
    introduction_extraction_process = models.CharField(max_length=100, blank=True)
    biscuit_position                = models.CharField(max_length=100, blank=True)
    #Number of hydraulic slides
    quantity_of_punch_pins          = models.CharField(max_length=100, blank=True,
                                        help_text='Número o Defined by toolmaker')
    #Admisible residual burr (mm)
    temperature_when_trimmed        = models.CharField(max_length=100, blank=True)
    #Gas springs (Defined by toolmaker)
    #Ejectors (Defined by toolmaker)
    #Maximum weight of the part to be trimmed (kg)
    comments = models.TextField(blank=True)
