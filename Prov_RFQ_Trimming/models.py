# Prov_RFQ_Trimming/models.py

from django.db import models
from django.conf import settings
from Asignaciones.models import Asignacion_Proveedor_Trimming


def float_field():
    """Shortcut para campos float con default 0"""
    return models.FloatField(default=0.0)


class List(models.Model):
  razon_social = models.CharField(max_length=100)
  planta = models.CharField(max_length=100)
  modena = models.CharField(max_length=10)
  
  def __str__(self):
     return f'{self.razon_social} - {self.planta} - {self.modena}'
  
  class Meta:
    db_table = 'List'
  
  


class Cost_Breakdown_Trimming(models.Model):

    class Currency(models.TextChoices):
        USD = 'USD', 'USD'
        EUR = 'EUR', 'EUR'

    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Borrador'
        SUBMITTED = 'submitted', 'Enviado'

    id_asignacion = models.OneToOneField(
        Asignacion_Proveedor_Trimming,
        on_delete=models.CASCADE,
        related_name='cost_breakdown',
    )
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cost_breakdowns_trimming',
    )
    last_change                 = models.DateTimeField(auto_now=True)
    status                      = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    base_currency_exchange_rate = models.CharField(
                                    max_length=10,
                                    choices=Currency.choices,
                                    default=Currency.USD
                                  )
    max_weight_for_trim_die     = models.FloatField(null=True, blank=True)
    comments                    = models.TextField(blank=True)

    # MATERIAL COSTS
    mat_raw_materials_unit      = float_field()
    mat_raw_materials_price_unit = float_field()
    mat_raw_materials_total     = float_field()
    mat_raw_materials_weeks     = float_field()

    mat_others_unit             = float_field()
    mat_others_price_unit       = float_field()
    mat_others_total            = float_field()
    mat_others_weeks            = float_field()

    mat_grand_total_unit        = float_field()
    mat_grand_total_price_unit  = float_field()
    mat_grand_total_sum         = float_field()
    mat_grand_total_weeks       = float_field()

    # ACCESSORIES COSTS
    accs_merkle_cylinders_unit        = float_field()
    accs_merkle_cylinders_price_unit  = float_field()
    accs_merkle_cylinders_total       = float_field()
    accs_merkle_cylinders_weeks       = float_field()

    accs_telemecanique_unit           = float_field()
    accs_telemecanique_price_unit     = float_field()
    accs_telemecanique_total          = float_field()
    accs_telemecanique_weeks          = float_field()

    accs_sensores_ifm_unit            = float_field()
    accs_sensores_ifm_price_unit      = float_field()
    accs_sensores_ifm_total           = float_field()
    accs_sensores_ifm_weeks           = float_field()

    accs_air_devices_unit             = float_field()
    accs_air_devices_price_unit       = float_field()
    accs_air_devices_total            = float_field()
    accs_air_devices_weeks            = float_field()

    accs_others_unit                  = float_field()
    accs_others_price_unit            = float_field()
    accs_others_total                 = float_field()
    accs_others_weeks                 = float_field()

    accs_grand_total_unit             = float_field()
    accs_grand_total_price_unit       = float_field()
    accs_grand_total_sum              = float_field()
    accs_grand_total_weeks            = float_field()

    # MANUFACTURING — Machining
    mach_milling_h                    = float_field()
    mach_milling_price_h              = float_field()
    mach_milling_total                = float_field()
    mach_milling_weeks                = float_field()

    mach_turning_h                    = float_field()
    mach_turning_price_h              = float_field()
    mach_turning_total                = float_field()
    mach_turning_weeks                = float_field()

    mach_wire_cutting_h               = float_field()
    mach_wire_cutting_price_h         = float_field()
    mach_wire_cutting_total           = float_field()
    mach_wire_cutting_weeks           = float_field()

    mach_edm_h                        = float_field()
    mach_edm_price_h                  = float_field()
    mach_edm_total                    = float_field()
    mach_edm_weeks                    = float_field()

    mach_grinding_h                   = float_field()
    mach_grinding_price_h             = float_field()
    mach_grinding_total               = float_field()
    mach_grinding_weeks               = float_field()

    mach_drilling_h                   = float_field()
    mach_drilling_price_h             = float_field()
    mach_drilling_total               = float_field()
    mach_drilling_weeks               = float_field()

    mach_others_h                     = float_field()
    mach_others_price_h               = float_field()
    mach_others_total                 = float_field()
    mach_others_weeks                 = float_field()

    mach_grand_total_h                = float_field()
    mach_grand_total_price_h          = float_field()
    mach_grand_total_sum              = float_field()
    mach_grand_total_weeks            = float_field()

    # MANUFACTURING — Manual Work
    man_assembly_h                    = float_field()
    man_assembly_price_h              = float_field()
    man_assembly_total                = float_field()
    man_assembly_weeks                = float_field()

    man_spotting_h                    = float_field()
    man_spotting_price_h              = float_field()
    man_spotting_total                = float_field()
    man_spotting_weeks                = float_field()

    man_stripping_polishing_h         = float_field()
    man_stripping_polishing_price_h   = float_field()
    man_stripping_polishing_total     = float_field()
    man_stripping_polishing_weeks     = float_field()

    man_others_h                      = float_field()
    man_others_price_h                = float_field()
    man_others_total                  = float_field()
    man_others_weeks                  = float_field()

    man_grand_total_h                 = float_field()
    man_grand_total_price_h           = float_field()
    man_grand_total_sum               = float_field()
    man_grand_total_weeks             = float_field()

    # MANUFACTURING — Heat & Surface Treatment
    heat_hardening_h                  = float_field()
    heat_hardening_price_h            = float_field()
    heat_hardening_total              = float_field()
    heat_hardening_weeks              = float_field()

    heat_nitriding_h                  = float_field()
    heat_nitriding_price_h            = float_field()
    heat_nitriding_total              = float_field()
    heat_nitriding_weeks              = float_field()

    heat_coating_h                    = float_field()
    heat_coating_price_h              = float_field()
    heat_coating_total                = float_field()
    heat_coating_weeks                = float_field()

    heat_graining_h                   = float_field()
    heat_graining_price_h             = float_field()
    heat_graining_total               = float_field()
    heat_graining_weeks               = float_field()

    heat_others_h                     = float_field()
    heat_others_price_h               = float_field()
    heat_others_total                 = float_field()
    heat_others_weeks                 = float_field()

    heat_grand_total_h                = float_field()
    heat_grand_total_price_h          = float_field()
    heat_grand_total_sum              = float_field()
    heat_grand_total_weeks            = float_field()

    # MANUFACTURING — Engineering & Design
    eng_design_h                      = float_field()
    eng_design_price_h                = float_field()
    eng_design_total                  = float_field()
    eng_design_weeks                  = float_field()

    eng_cam_nc_h                      = float_field()
    eng_cam_nc_price_h                = float_field()
    eng_cam_nc_total                  = float_field()
    eng_cam_nc_weeks                  = float_field()

    eng_others_h                      = float_field()
    eng_others_price_h                = float_field()
    eng_others_total                  = float_field()
    eng_others_weeks                  = float_field()

    eng_grand_total_h                 = float_field()
    eng_grand_total_price_h           = float_field()
    eng_grand_total_sum               = float_field()
    eng_grand_total_weeks             = float_field()

    # Total Manufacturing
    manuf_grand_total_h               = float_field()
    manuf_grand_total_price_h         = float_field()
    manuf_grand_total_sum             = float_field()
    manuf_grand_total_weeks           = float_field()

    # TRIM DIE ADJUSTMENT
    adj_adjustment_h                  = float_field()
    adj_adjustment_price_h            = float_field()
    adj_adjustment_total              = float_field()
    adj_adjustment_weeks              = float_field()

    adj_others_h                      = float_field()
    adj_others_price_h                = float_field()
    adj_others_total                  = float_field()
    adj_others_weeks                  = float_field()

    adj_grand_total_h                 = float_field()
    adj_grand_total_price_h           = float_field()
    adj_grand_total_sum               = float_field()
    adj_grand_total_weeks             = float_field()

    # LOGISTICS
    log_transport_supplier_to_btc_unit       = float_field()
    log_transport_supplier_to_btc_price_unit = float_field()
    log_transport_supplier_to_btc_total      = float_field()
    log_transport_supplier_to_btc_weeks      = float_field()

    log_transport_btc_to_supplier_unit       = float_field()
    log_transport_btc_to_supplier_price_unit = float_field()
    log_transport_btc_to_supplier_total      = float_field()
    log_transport_btc_to_supplier_weeks      = float_field()

    log_duty_costs_unit               = float_field()
    log_duty_costs_price_unit         = float_field()
    log_duty_costs_total              = float_field()
    log_duty_costs_weeks              = float_field()

    log_cleaning_packaging_unit       = float_field()
    log_cleaning_packaging_price_unit = float_field()
    log_cleaning_packaging_total      = float_field()
    log_cleaning_packaging_weeks      = float_field()

    log_other_costs_unit              = float_field()
    log_other_costs_price_unit        = float_field()
    log_other_costs_total             = float_field()
    log_other_costs_weeks             = float_field()

    log_grand_total_unit              = float_field()
    log_grand_total_price_unit        = float_field()
    log_grand_total_sum               = float_field()
    log_grand_total_weeks             = float_field()

    # TOOL REPLACEMENT
    toolrep_die_improvements_unit       = float_field()
    toolrep_die_improvements_price_unit = float_field()
    toolrep_die_improvements_total      = float_field()
    toolrep_die_improvements_weeks      = float_field()

    toolrep_others_unit               = float_field()
    toolrep_others_price_unit         = float_field()
    toolrep_others_total              = float_field()
    toolrep_others_weeks              = float_field()

    toolrep_grand_total_unit          = float_field()
    toolrep_grand_total_price_unit    = float_field()
    toolrep_grand_total_sum           = float_field()
    toolrep_grand_total_weeks         = float_field()

    # SPARE PARTS
    sp_punch_pins_unit                = float_field()
    sp_punch_pins_price_unit          = float_field()
    sp_punch_pins_total               = float_field()
    sp_punch_pins_weeks               = float_field()

    sp_others_unit                    = float_field()
    sp_others_price_unit              = float_field()
    sp_others_total                   = float_field()
    sp_others_weeks                   = float_field()

    sp_grand_total_unit               = float_field()
    sp_grand_total_price_unit         = float_field()
    sp_grand_total_sum                = float_field()
    sp_grand_total_weeks              = float_field()

    def __str__(self):
        return f'Cost Breakdown Trimming - Asignacion {self.id_asignacion_id}'


    class Meta:
        db_table = 'Cost_Breakdown_Trimming'