from django.db import  models
from Bocar import settings
# Create your  models.FloatField(default= 0.0)here.
class Cost_Breakdown_Mold( models.Model):

    ##LO QUE ESTA COMENTADO ME LO DIO CLAUDE EN BASE A LO QUE PUSIMOS EN LA BASE JAJAJAJ

    #id_asignacion =  models.FloatField(default= 0.0)ForeignKey(
        #Asignacion_Proveedores,
        #on_delete= models.FloatField(default= 0.0)CASCADE,
      # related_name='cost_breakdowns'
   # default= 0.0)
    #id_set_of_cavities =  models.FloatField(default= 0.0)ForeignKey(
      #  Set_of_Cavities_Mold,
      #  on_delete= models.FloatField(default= 0.0)SET_NULL,
      #  null=True, blank=True,
       # related_name='cost_breakdowns'
   # default= 0.0)
  #  last_edited_by =  models.FloatField(default= 0.0)ForeignKey(
      #  settings.AUTH_USER_MODEL,
     #   on_delete= models.FloatField(default= 0.0)SET_NULL,
        #null=True, blank=True
   # default= 0.0)
  #  last_change =  models.FloatField(default= 0.0)DateTimeField(auto_now=Truedefault= 0.0)

   # class Currency( models.FloatField(default= 0.0)TextChoicesdefault= 0.0):
     #   USD = 'USD', 'USD'
      #  EUR = 'EUR', 'EUR'

   # base_currency_exchange_rate =  models.FloatField(default= 0.0)CharField(
      #  max_length=10,
      #  choices=Currency.choices,
       # default=Currency.USD
    #default= 0.0)

    # ----------------------------------
    # ACCESSORIES COSTS
    # ----------------------------------
    accs_parker_hydraulic_unit        =  models.FloatField(default= 0.0)
    accs_parker_hydraulic_price_unit  =  models.FloatField(default= 0.0)
    accs_parker_hydraulic_total       =  models.FloatField(default= 0.0)
    accs_parker_hydraulic_weeks       =  models.FloatField(default= 0.0)

    accs_jet_cooling_unit             =  models.FloatField(default= 0.0)
    accs_jet_cooling_price_unit       =  models.FloatField(default= 0.0)
    accs_jet_cooling_total            =  models.FloatField(default= 0.0)
    accs_jet_cooling_weeks            =  models.FloatField(default= 0.0)

    accs_squeeze_pin_unit             =  models.FloatField(default= 0.0)
    accs_squeeze_pin_price_unit       =  models.FloatField(default= 0.0)
    accs_squeeze_pin_total            =  models.FloatField(default= 0.0)
    accs_squeeze_pin_weeks            =  models.FloatField(default= 0.0)

    accs_interchangeable_inserts_unit        =  models.FloatField(default= 0.0)
    accs_interchangeable_inserts_price_unit  =  models.FloatField(default= 0.0)
    accs_interchangeable_inserts_total       =  models.FloatField(default= 0.0)
    accs_interchangeable_inserts_weeks       =  models.FloatField(default= 0.0)

    accs_chill_blocks_vacuum_unit        =  models.FloatField(default= 0.0)
    accs_chill_blocks_vacuum_price_unit  =  models.FloatField(default= 0.0)
    accs_chill_blocks_vacuum_total       =  models.FloatField(default= 0.0)
    accs_chill_blocks_vacuum_weeks       =  models.FloatField(default= 0.0)

    accs_eyebolts_unit             =  models.FloatField(default= 0.0)
    accs_eyebolts_price_unit       =  models.FloatField(default= 0.0)
    accs_eyebolts_total            =  models.FloatField(default= 0.0)
    accs_eyebolts_weeks            =  models.FloatField(default= 0.0)

    accs_oil_water_conn_unit       =  models.FloatField(default= 0.0)
    accs_oil_water_conn_price_unit =  models.FloatField(default= 0.0)
    accs_oil_water_conn_total      =  models.FloatField(default= 0.0)
    accs_oil_water_conn_weeks      =  models.FloatField(default= 0.0)

    accs_lethiguel_dist_unit       =  models.FloatField(default= 0.0)
    accs_lethiguel_dist_price_unit =  models.FloatField(default= 0.0)
    accs_lethiguel_dist_total      =  models.FloatField(default= 0.0)
    accs_lethiguel_dist_weeks      =  models.FloatField(default= 0.0)

    accs_others_unit               =  models.FloatField(default= 0.0)
    accs_others_price_unit         =  models.FloatField(default= 0.0)
    accs_others_total              =  models.FloatField(default= 0.0)
    accs_others_weeks              =  models.FloatField(default= 0.0)

    accs_grand_total_unit          =  models.FloatField(default= 0.0)
    accs_grand_total_price_unit    =  models.FloatField(default= 0.0)
    accs_grand_total_sum           =  models.FloatField(default= 0.0)
    accs_grand_total_weeks         =  models.FloatField(default= 0.0)

    # ----------------------------------
    # MATERIAL COSTS
    # ----------------------------------
    mat_die_frame_unit          =  models.FloatField(default= 0.0)
    mat_die_frame_price_unit    =  models.FloatField(default= 0.0)
    mat_die_frame_total         =  models.FloatField(default= 0.0)
    mat_die_frame_weeks         =  models.FloatField(default= 0.0)

    mat_cavity_unit             =  models.FloatField(default= 0.0)
    mat_cavity_price_unit       =  models.FloatField(default= 0.0)
    mat_cavity_total            =  models.FloatField(default= 0.0)
    mat_cavity_weeks            =  models.FloatField(default= 0.0)

    mat_steel_pipes_unit        =  models.FloatField(default= 0.0)
    mat_steel_pipes_price_unit  =  models.FloatField(default= 0.0)
    mat_steel_pipes_total       =  models.FloatField(default= 0.0)
    mat_steel_pipes_weeks       =  models.FloatField(default= 0.0)

    mat_others_unit             =  models.FloatField(default= 0.0)
    mat_others_price_unit       =  models.FloatField(default= 0.0)
    mat_others_total            =  models.FloatField(default= 0.0)
    mat_others_weeks            =  models.FloatField(default= 0.0)

    mat_grand_total_unit        =  models.FloatField(default= 0.0)
    mat_grand_total_price_unit  =  models.FloatField(default= 0.0)
    mat_grand_total_sum         =  models.FloatField(default= 0.0)
    mat_grand_total_weeks       =  models.FloatField(default= 0.0)

    # ----------------------------------
    # MANUFACTURING COSTS - Machining
    # ----------------------------------
    mach_milling_h              =  models.FloatField(default= 0.0)
    mach_milling_price_h        =  models.FloatField(default= 0.0)
    mach_milling_total          =  models.FloatField(default= 0.0)
    mach_milling_weeks          =  models.FloatField(default= 0.0)

    mach_turning_h              =  models.FloatField(default= 0.0)
    mach_turning_price_h        =  models.FloatField(default= 0.0)
    mach_turning_total          =  models.FloatField(default= 0.0)
    mach_turning_weeks          =  models.FloatField(default= 0.0)

    mach_wire_cutting_h         =  models.FloatField(default= 0.0)
    mach_wire_cutting_price_h   =  models.FloatField(default= 0.0)
    mach_wire_cutting_total     =  models.FloatField(default= 0.0)
    mach_wire_cutting_weeks     =  models.FloatField(default= 0.0)

    mach_edm_h                  =  models.FloatField(default= 0.0)
    mach_edm_price_h            =  models.FloatField(default= 0.0)
    mach_edm_total              =  models.FloatField(default= 0.0)
    mach_edm_weeks              =  models.FloatField(default= 0.0)

    mach_grinding_h             =  models.FloatField(default= 0.0)
    mach_grinding_price_h       =  models.FloatField(default= 0.0)
    mach_grinding_total         =  models.FloatField(default= 0.0)
    mach_grinding_weeks         =  models.FloatField(default= 0.0)

    mach_drilling_h             =  models.FloatField(default= 0.0)
    mach_drilling_price_h       =  models.FloatField(default= 0.0)
    mach_drilling_total         =  models.FloatField(default= 0.0)
    mach_drilling_weeks         =  models.FloatField(default= 0.0)

    mach_others_h               =  models.FloatField(default= 0.0)
    mach_others_price_h         =  models.FloatField(default= 0.0)
    mach_others_total           =  models.FloatField(default= 0.0)
    mach_others_weeks           =  models.FloatField(default= 0.0)

    mach_grand_total_h          =  models.FloatField(default= 0.0)
    mach_grand_total_price_h    =  models.FloatField(default= 0.0)
    mach_grand_total_sum        =  models.FloatField(default= 0.0)
    mach_grand_total_weeks      =  models.FloatField(default= 0.0)

    # Manual Work
    man_assembly_h              =  models.FloatField(default= 0.0)
    man_assembly_price_h        =  models.FloatField(default= 0.0)
    man_assembly_total          =  models.FloatField(default= 0.0)
    man_assembly_weeks          =  models.FloatField(default= 0.0)

    man_spotting_h              =  models.FloatField(default= 0.0)
    man_spotting_price_h        =  models.FloatField(default= 0.0)
    man_spotting_total          =  models.FloatField(default= 0.0)
    man_spotting_weeks          =  models.FloatField(default= 0.0)

    man_stripping_polishing_h         =  models.FloatField(default= 0.0)
    man_stripping_polishing_price_h   =  models.FloatField(default= 0.0)
    man_stripping_polishing_total     =  models.FloatField(default= 0.0)
    man_stripping_polishing_weeks     =  models.FloatField(default= 0.0)

    man_others_h                =  models.FloatField(default= 0.0)
    man_others_price_h          =  models.FloatField(default= 0.0)
    man_others_total            =  models.FloatField(default= 0.0)
    man_others_weeks            =  models.FloatField(default= 0.0)

    man_grand_total_h           =  models.FloatField(default= 0.0)
    man_grand_total_price_h     =  models.FloatField(default= 0.0)
    man_grand_total_sum         =  models.FloatField(default= 0.0)
    man_grand_total_weeks       =  models.FloatField(default= 0.0)

    # Heat & Surface Treatment
    heat_hardening_h            =  models.FloatField(default= 0.0)
    heat_hardening_price_h      =  models.FloatField(default= 0.0)
    heat_hardening_total        =  models.FloatField(default= 0.0)
    heat_hardening_weeks        =  models.FloatField(default= 0.0)

    heat_nitriding_h            =  models.FloatField(default= 0.0)
    heat_nitriding_price_h      =  models.FloatField(default= 0.0)
    heat_nitriding_total        =  models.FloatField(default= 0.0)
    heat_nitriding_weeks        =  models.FloatField(default= 0.0)

    heat_coating_h              =  models.FloatField(default= 0.0)
    heat_coating_price_h        =  models.FloatField(default= 0.0)
    heat_coating_total          =  models.FloatField(default= 0.0)
    heat_coating_weeks          =  models.FloatField(default= 0.0)

    heat_graining_h             =  models.FloatField(default= 0.0)
    heat_graining_price_h       =  models.FloatField(default= 0.0)
    heat_graining_total         =  models.FloatField(default= 0.0)
    heat_graining_weeks         =  models.FloatField(default= 0.0)

    heat_others_h               =  models.FloatField(default= 0.0)
    heat_others_price_h         =  models.FloatField(default= 0.0)
    heat_others_total           =  models.FloatField(default= 0.0)
    heat_others_weeks           =  models.FloatField(default= 0.0)

    heat_grand_total_h          =  models.FloatField(default= 0.0)
    heat_grand_total_price_h    =  models.FloatField(default= 0.0)
    heat_grand_total_sum        =  models.FloatField(default= 0.0)
    heat_grand_total_weeks      =  models.FloatField(default= 0.0)

    # Engineering & Design
    eng_design_h                =  models.FloatField(default= 0.0)
    eng_design_price_h          =  models.FloatField(default= 0.0)
    eng_design_total            =  models.FloatField(default= 0.0)
    eng_design_weeks            =  models.FloatField(default= 0.0)

    eng_cam_nc_h                =  models.FloatField(default= 0.0)
    eng_cam_nc_price_h          =  models.FloatField(default= 0.0)
    eng_cam_nc_total            =  models.FloatField(default= 0.0)
    eng_cam_nc_weeks            =  models.FloatField(default= 0.0)

    eng_simulation_h            =  models.FloatField(default= 0.0)
    eng_simulation_price_h      =  models.FloatField(default= 0.0)
    eng_simulation_total        =  models.FloatField(default= 0.0)
    eng_simulation_weeks        =  models.FloatField(default= 0.0)

    eng_others_h                =  models.FloatField(default= 0.0)
    eng_others_price_h          =  models.FloatField(default= 0.0)
    eng_others_total            =  models.FloatField(default= 0.0)
    eng_others_weeks            =  models.FloatField(default= 0.0)

    eng_grand_total_h           =  models.FloatField(default= 0.0)
    eng_grand_total_price_h     =  models.FloatField(default= 0.0)
    eng_grand_total_sum         =  models.FloatField(default= 0.0)
    eng_grand_total_weeks       =  models.FloatField(default= 0.0)

    # Total Manufacturing Final
    grand_total_h               =  models.FloatField(default= 0.0)
    grand_total_price_h         =  models.FloatField(default= 0.0)
    grand_total_sum             =  models.FloatField(default= 0.0)
    grand_total_weeks           =  models.FloatField(default= 0.0)

    # ----------------------------------
    # CORRECTIONS & OPTIMIZATIONS
    # ----------------------------------
    corr_mold_measurement_h         =  models.FloatField(default= 0.0)
    corr_mold_measurement_price_h   =  models.FloatField(default= 0.0)
    corr_mold_measurement_total     =  models.FloatField(default= 0.0)
    corr_mold_measurement_weeks     =  models.FloatField(default= 0.0)

    corr_dim_corrections_h          =  models.FloatField(default= 0.0)
    corr_dim_corrections_price_h    =  models.FloatField(default= 0.0)
    corr_dim_corrections_total      =  models.FloatField(default= 0.0)
    corr_dim_corrections_weeks      =  models.FloatField(default= 0.0)

    corr_optimizations_h            =  models.FloatField(default= 0.0)
    corr_optimizations_price_h      =  models.FloatField(default= 0.0)
    corr_optimizations_total        =  models.FloatField(default= 0.0)
    corr_optimizations_weeks        =  models.FloatField(default= 0.0)

    corr_others_h                   =  models.FloatField(default= 0.0)
    corr_others_price_h             =  models.FloatField(default= 0.0)
    corr_others_total               =  models.FloatField(default= 0.0)
    corr_others_weeks               =  models.FloatField(default= 0.0)

    corr_grand_total_h              =  models.FloatField(default= 0.0)
    corr_grand_total_price_h        =  models.FloatField(default= 0.0)
    corr_grand_total_sum            =  models.FloatField(default= 0.0)
    corr_grand_total_weeks          =  models.FloatField(default= 0.0)

    # ----------------------------------
    # LOGISTICS COSTS
    # ----------------------------------
    log_transport_supplier_to_btc       =  models.FloatField(default= 0.0)
    log_transport_supplier_to_btc_price =  models.FloatField(default= 0.0)
    log_transport_supplier_to_btc_total =  models.FloatField(default= 0.0)
    log_transport_supplier_to_btc_weeks =  models.FloatField(default= 0.0)

    log_transport_btc_to_supplier       =  models.FloatField(default= 0.0)
    log_transport_btc_to_supplier_price =  models.FloatField(default= 0.0)
    log_transport_btc_to_supplier_total =  models.FloatField(default= 0.0)
    log_transport_btc_to_supplier_weeks =  models.FloatField(default= 0.0)

    log_duty_costs_unit                 =  models.FloatField(default= 0.0)
    log_duty_costs_price                =  models.FloatField(default= 0.0)
    log_duty_costs_total                =  models.FloatField(default= 0.0)
    log_duty_costs_weeks                =  models.FloatField(default= 0.0)

    log_cleaning_packaging_unit         =  models.FloatField(default= 0.0)
    log_cleaning_packaging_price        =  models.FloatField(default= 0.0)
    log_cleaning_packaging_total        =  models.FloatField(default= 0.0)
    log_cleaning_packaging_weeks        =  models.FloatField(default= 0.0)

    log_others_unit                     =  models.FloatField(default= 0.0)
    log_others_price                    =  models.FloatField(default= 0.0)
    log_others_total                    =  models.FloatField(default= 0.0)
    log_others_weeks                    =  models.FloatField(default= 0.0)

    log_grand_total_unit                =  models.FloatField(default= 0.0)
    log_grand_total_price               =  models.FloatField(default= 0.0)
    log_grand_total_sum                 =  models.FloatField(default= 0.0)
    log_grand_total_weeks               =  models.FloatField(default= 0.0)

    # ----------------------------------
    # TOOL REPLACEMENT
    # ----------------------------------
    toolrep_die_improvements_unit       =  models.FloatField(default= 0.0)
    toolrep_die_improvements_price_unit =  models.FloatField(default= 0.0)
    toolrep_die_improvements_total      =  models.FloatField(default= 0.0)
    toolrep_die_improvements_weeks      =  models.FloatField(default= 0.0)

    toolrep_others_unit                 =  models.FloatField(default= 0.0)
    toolrep_others_price_unit           =  models.FloatField(default= 0.0)
    toolrep_others_total                =  models.FloatField(default= 0.0)
    toolrep_others_weeks                =  models.FloatField(default= 0.0)

    toolrep_grand_total_unit            =  models.FloatField(default= 0.0)
    toolrep_grand_total_price_unit      =  models.FloatField(default= 0.0)
    toolrep_grand_total_sum             =  models.FloatField(default= 0.0)
    toolrep_grand_total_weeks           =  models.FloatField(default= 0.0)

    # ----------------------------------
    # SAMPLING
    # ----------------------------------
    samp_tryout_q                       =  models.FloatField(default= 0.0)
    samp_tryout_price_q                 =  models.FloatField(default= 0.0)
    samp_tryout_total                   =  models.FloatField(default= 0.0)
    samp_tryout_weeks                   =  models.FloatField(default= 0.0)

    samp_measurement_q                  =  models.FloatField(default= 0.0)
    samp_measurement_price_q            =  models.FloatField(default= 0.0)
    samp_measurement_total              =  models.FloatField(default= 0.0)
    samp_measurement_weeks              =  models.FloatField(default= 0.0)

    samp_others_q                       =  models.FloatField(default= 0.0)
    samp_others_price_q                 =  models.FloatField(default= 0.0)
    samp_others_total                   =  models.FloatField(default= 0.0)
    samp_others_weeks                   =  models.FloatField(default= 0.0)

    samp_grand_total_q                  =  models.FloatField(default= 0.0)
    samp_grand_total_price_q            =  models.FloatField(default= 0.0)
    samp_grand_total_sum                =  models.FloatField(default= 0.0)
    samp_grand_total_weeks              =  models.FloatField(default= 0.0)

    # ----------------------------------
    # SPARE PARTS
    # ----------------------------------
    sp_interchangeable_inserts_unit       =  models.FloatField(default= 0.0)
    sp_interchangeable_inserts_price_unit =  models.FloatField(default= 0.0)
    sp_interchangeable_inserts_total      =  models.FloatField(default= 0.0)
    sp_interchangeable_inserts_weeks      =  models.FloatField(default= 0.0)

    sp_core_pins_unit                     =  models.FloatField(default= 0.0)
    sp_core_pins_price_unit               =  models.FloatField(default= 0.0)
    sp_core_pins_total                    =  models.FloatField(default= 0.0)
    sp_core_pins_weeks                    =  models.FloatField(default= 0.0)

    sp_inserts_as_spare_unit              =  models.FloatField(default= 0.0)
    sp_inserts_as_spare_price_unit        =  models.FloatField(default= 0.0)
    sp_inserts_as_spare_total             =  models.FloatField(default= 0.0)
    sp_inserts_as_spare_weeks             =  models.FloatField(default= 0.0)

    sp_others_unit                        =  models.FloatField(default= 0.0)
    sp_others_price_unit                  =  models.FloatField(default= 0.0)
    sp_others_total                       =  models.FloatField(default= 0.0)
    sp_others_weeks                       =  models.FloatField(default= 0.0)

    sp_grand_total_unit                   =  models.FloatField(default= 0.0)
    sp_grand_total_price_unit             =  models.FloatField(default= 0.0)
    sp_grand_total_sum                    =  models.FloatField(default= 0.0)
    sp_grand_total_weeks                  =  models.FloatField(default= 0.0)

    def __str__(self):
        return f'Cost Breakdown Mold - Asignacion {self.id_asignacion_id}'

    class Meta:
        db_table = 'Cost_Breakdown_Mold'


class Set_of_Cavities_Mold(models.Model):

    #id_asignacion = models.ForeignKey(
      #  Asignacion_Proveedores,
       # on_delete=models.CASCADE,
      #  related_name='set_of_cavities'
  #  default= 0.0)
  #  last_edited_by = models.ForeignKey(
      #  settings.AUTH_USER_MODEL,
      #  on_delete=models.SET_NULL,
      #  null=True, blank=True
  #  default= 0.0)
   # last_change = models.DateTimeField(auto_now=Truedefault= 0.0)

    # 13.- ACCESSORIES COSTS
    soc_accs_jet_cooling_unit             = models.FloatField(default= 0.0)
    soc_accs_jet_cooling_total            = models.FloatField(default= 0.0)
    soc_accs_jet_cooling_weeks            = models.FloatField(default= 0.0)

    soc_accs_squeeze_pin_unit             = models.FloatField(default= 0.0)
    soc_accs_squeeze_pin_price_unit       = models.FloatField(default= 0.0)
    soc_accs_squeeze_pin_total            = models.FloatField(default= 0.0)
    soc_accs_squeeze_pin_weeks            = models.FloatField(default= 0.0)

    soc_accs_interchangeable_inserts_unit       = models.FloatField(default= 0.0)
    soc_accs_interchangeable_inserts_price_unit = models.FloatField(default= 0.0)
    soc_accs_interchangeable_inserts_total      = models.FloatField(default= 0.0)
    soc_accs_interchangeable_inserts_weeks      = models.FloatField(default= 0.0)

    soc_accs_inserts_spare_unit           = models.FloatField(default= 0.0)
    soc_accs_inserts_spare_price_unit     = models.FloatField(default= 0.0)
    soc_accs_inserts_spare_total          = models.FloatField(default= 0.0)
    soc_accs_inserts_spare_weeks          = models.FloatField(default= 0.0)

    soc_accs_chill_blocks_unit            = models.FloatField(default= 0.0)
    soc_accs_chill_blocks_price_unit      = models.FloatField(default= 0.0)
    soc_accs_chill_blocks_total           = models.FloatField(default= 0.0)
    soc_accs_chill_blocks_weeks           = models.FloatField(default= 0.0)

    soc_accs_others_unit                  = models.FloatField(default= 0.0)
    soc_accs_others_price_unit            = models.FloatField(default= 0.0)
    soc_accs_others_total                 = models.FloatField(default= 0.0)
    soc_accs_others_weeks                 = models.FloatField(default= 0.0)

    soc_accs_grand_total_unit             = models.FloatField(default= 0.0)
    soc_accs_grand_total_price_unit       = models.FloatField(default= 0.0)
    soc_accs_grand_total_sum              = models.FloatField(default= 0.0)
    soc_accs_grand_total_weeks            = models.FloatField(default= 0.0)

    # 14.- MATERIAL COSTS
    soc_mat_raw_materials_unit            = models.FloatField(default= 0.0)
    soc_mat_raw_materials_price_unit      = models.FloatField(default= 0.0)
    soc_mat_raw_materials_total           = models.FloatField(default= 0.0)
    soc_mat_raw_materials_weeks           = models.FloatField(default= 0.0)

    soc_mat_others_unit                   = models.FloatField(default= 0.0)
    soc_mat_others_price_unit             = models.FloatField(default= 0.0)
    soc_mat_others_total                  = models.FloatField(default= 0.0)
    soc_mat_others_weeks                  = models.FloatField(default= 0.0)

    soc_mat_grand_total_unit              = models.FloatField(default= 0.0)
    soc_mat_grand_total_price_unit        = models.FloatField(default= 0.0)
    soc_mat_grand_total_sum               = models.FloatField(default= 0.0)
    soc_mat_grand_total_weeks             = models.FloatField(default= 0.0)

    # 15.- MANUFACTURING COSTS — Machining
    soc_mach_milling_h                    = models.FloatField(default= 0.0)
    soc_mach_milling_price_h              = models.FloatField(default= 0.0)
    soc_mach_milling_total                = models.FloatField(default= 0.0)
    soc_mach_milling_weeks                = models.FloatField(default= 0.0)

    soc_mach_turning_h                    = models.FloatField(default= 0.0)
    soc_mach_turning_price_h              = models.FloatField(default= 0.0)
    soc_mach_turning_total                = models.FloatField(default= 0.0)
    soc_mach_turning_weeks                = models.FloatField(default= 0.0)

    soc_mach_wire_cutting_h               = models.FloatField(default= 0.0)
    soc_mach_wire_cutting_price_h         = models.FloatField(default= 0.0)
    soc_mach_wire_cutting_total           = models.FloatField(default= 0.0)
    soc_mach_wire_cutting_weeks           = models.FloatField(default= 0.0)

    soc_mach_edm_h                        = models.FloatField(default= 0.0)
    soc_mach_edm_price_h                  = models.FloatField(default= 0.0)
    soc_mach_edm_total                    = models.FloatField(default= 0.0)
    soc_mach_edm_weeks                    = models.FloatField(default= 0.0)

    soc_mach_grinding_h                   = models.FloatField(default= 0.0)
    soc_mach_grinding_price_h             = models.FloatField(default= 0.0)
    soc_mach_grinding_total               = models.FloatField(default= 0.0)
    soc_mach_grinding_weeks               = models.FloatField(default= 0.0)

    soc_mach_drilling_h                   = models.FloatField(default= 0.0)
    soc_mach_drilling_price_h             = models.FloatField(default= 0.0)
    soc_mach_drilling_total               = models.FloatField(default= 0.0)
    soc_mach_drilling_weeks               = models.FloatField(default= 0.0)

    soc_mach_others_h                     = models.FloatField(default= 0.0)
    soc_mach_others_price_h               = models.FloatField(default= 0.0)
    soc_mach_others_total                 = models.FloatField(default= 0.0)
    soc_mach_others_weeks                 = models.FloatField(default= 0.0)

    soc_mach_grand_total_h                = models.FloatField(default= 0.0)
    soc_mach_grand_total_price_h          = models.FloatField(default= 0.0)
    soc_mach_grand_total_sum              = models.FloatField(default= 0.0)
    soc_mach_grand_total_weeks            = models.FloatField(default= 0.0)

    # 15.- MANUFACTURING COSTS — Manual Work
    soc_man_assembly_h                    = models.FloatField(default= 0.0)
    soc_man_assembly_price_h              = models.FloatField(default= 0.0)
    soc_man_assembly_total                = models.FloatField(default= 0.0)
    soc_man_assembly_weeks                = models.FloatField(default= 0.0)

    soc_man_spotting_h                    = models.FloatField(default= 0.0)
    soc_man_spotting_price_h              = models.FloatField(default= 0.0)
    soc_man_spotting_total                = models.FloatField(default= 0.0)
    soc_man_spotting_weeks                = models.FloatField(default= 0.0)

    soc_man_stripping_polishing_h         = models.FloatField(default= 0.0)
    soc_man_stripping_polishing_price_h   = models.FloatField(default= 0.0)
    soc_man_stripping_polishing_total     = models.FloatField(default= 0.0)
    soc_man_stripping_polishing_weeks     = models.FloatField(default= 0.0)

    soc_man_others_h                      = models.FloatField(default= 0.0)
    soc_man_others_price_h                = models.FloatField(default= 0.0)
    soc_man_others_total                  = models.FloatField(default= 0.0)
    soc_man_others_weeks                  = models.FloatField(default= 0.0)

    soc_man_grand_total_h                 = models.FloatField(default= 0.0)
    soc_man_grand_total_price_h           = models.FloatField(default= 0.0)
    soc_man_grand_total_sum               = models.FloatField(default= 0.0)
    soc_man_grand_total_weeks             = models.FloatField(default= 0.0)

    # 15.- MANUFACTURING COSTS — Heat & Surface Treatment
    soc_heat_hardening_h                  = models.FloatField(default= 0.0)
    soc_heat_hardening_price_h            = models.FloatField(default= 0.0)
    soc_heat_hardening_total              = models.FloatField(default= 0.0)
    soc_heat_hardening_weeks              = models.FloatField(default= 0.0)

    soc_heat_nitriding_h                  = models.FloatField(default= 0.0)
    soc_heat_nitriding_price_h            = models.FloatField(default= 0.0)
    soc_heat_nitriding_total              = models.FloatField(default= 0.0)
    soc_heat_nitriding_weeks              = models.FloatField(default= 0.0)

    soc_heat_coating_h                    = models.FloatField(default= 0.0)
    soc_heat_coating_price_h              = models.FloatField(default= 0.0)
    soc_heat_coating_total                = models.FloatField(default= 0.0)
    soc_heat_coating_weeks                = models.FloatField(default= 0.0)

    soc_heat_graining_h                   = models.FloatField(default= 0.0)
    soc_heat_graining_price_h             = models.FloatField(default= 0.0)
    soc_heat_graining_total               = models.FloatField(default= 0.0)
    soc_heat_graining_weeks               = models.FloatField(default= 0.0)

    soc_heat_others_h                     = models.FloatField(default= 0.0)
    soc_heat_others_price_h               = models.FloatField(default= 0.0)
    soc_heat_others_total                 = models.FloatField(default= 0.0)
    soc_heat_others_weeks                 = models.FloatField(default= 0.0)

    soc_heat_grand_total_h                = models.FloatField(default= 0.0)
    soc_heat_grand_total_price_h          = models.FloatField(default= 0.0)
    soc_heat_grand_total_sum              = models.FloatField(default= 0.0)
    soc_heat_grand_total_weeks            = models.FloatField(default= 0.0)

    # 15.- MANUFACTURING COSTS — Engineering & Design
    soc_eng_design_h                      = models.FloatField(default= 0.0)
    soc_eng_design_price_h                = models.FloatField(default= 0.0)
    soc_eng_design_total                  = models.FloatField(default= 0.0)
    soc_eng_design_weeks                  = models.FloatField(default= 0.0)

    soc_eng_cam_nc_h                      = models.FloatField(default= 0.0)
    soc_eng_cam_nc_price_h                = models.FloatField(default= 0.0)
    soc_eng_cam_nc_total                  = models.FloatField(default= 0.0)
    soc_eng_cam_nc_weeks                  = models.FloatField(default= 0.0)

    soc_eng_others_h                      = models.FloatField(default= 0.0)
    soc_eng_others_price_h                = models.FloatField(default= 0.0)
    soc_eng_others_total                  = models.FloatField(default= 0.0)
    soc_eng_others_weeks                  = models.FloatField(default= 0.0)

    soc_eng_grand_total_h                 = models.FloatField(default= 0.0)
    soc_eng_grand_total_price_h           = models.FloatField(default= 0.0)
    soc_eng_grand_total_sum               = models.FloatField(default= 0.0)
    soc_eng_grand_total_weeks             = models.FloatField(default= 0.0)

    soc_manuf_grand_total_sum             = models.FloatField(default= 0.0)
    soc_manuf_grand_total_weeks           = models.FloatField(default= 0.0)

    # 16.- CORRECTIONS & OPTIMIZATIONS
    soc_corr_measurement_cavities_h       = models.FloatField(default= 0.0)
    soc_corr_measurement_cavities_price_h = models.FloatField(default= 0.0)
    soc_corr_measurement_cavities_total   = models.FloatField(default= 0.0)
    soc_corr_measurement_cavities_weeks   = models.FloatField(default= 0.0)

    soc_corr_others_h                     = models.FloatField(default= 0.0)
    soc_corr_others_price_h               = models.FloatField(default= 0.0)
    soc_corr_others_total                 = models.FloatField(default= 0.0)
    soc_corr_others_weeks                 = models.FloatField(default= 0.0)

    soc_corr_grand_total_h                = models.FloatField(default= 0.0)
    soc_corr_grand_total_price_h          = models.FloatField(default= 0.0)
    soc_corr_grand_total_sum              = models.FloatField(default= 0.0)
    soc_corr_grand_total_weeks            = models.FloatField(default= 0.0)

    # 17.- LOGISTICS
    soc_log_cleaning_packaging_unit       = models.FloatField(default= 0.0)
    soc_log_cleaning_packaging_price_unit = models.FloatField(default= 0.0)
    soc_log_cleaning_packaging_total      = models.FloatField(default= 0.0)
    soc_log_cleaning_packaging_weeks      = models.FloatField(default= 0.0)

    soc_log_other_costs_unit              = models.FloatField(default= 0.0)
    soc_log_other_costs_price_unit        = models.FloatField(default= 0.0)
    soc_log_other_costs_total             = models.FloatField(default= 0.0)
    soc_log_other_costs_weeks             = models.FloatField(default= 0.0)

    soc_log_grand_total_unit              = models.FloatField(default= 0.0)
    soc_log_grand_total_price_unit        = models.FloatField(default= 0.0)
    soc_log_grand_total_sum               = models.FloatField(default= 0.0)
    soc_log_grand_total_weeks             = models.FloatField(default= 0.0)

    # 18.- SPARE PARTS
    soc_sp_interchangeable_inserts_unit       = models.FloatField(default= 0.0)
    soc_sp_interchangeable_inserts_price_unit = models.FloatField(default= 0.0)
    soc_sp_interchangeable_inserts_total      = models.FloatField(default= 0.0)
    soc_sp_interchangeable_inserts_weeks      = models.FloatField(default= 0.0)

    soc_sp_core_pins_unit                     = models.FloatField(default= 0.0)
    soc_sp_core_pins_price_unit               = models.FloatField(default= 0.0)
    soc_sp_core_pins_total                    = models.FloatField(default= 0.0)
    soc_sp_core_pins_weeks                    = models.FloatField(default= 0.0)

    soc_sp_others_unit                        = models.FloatField(default= 0.0)
    soc_sp_others_price_unit                  = models.FloatField(default= 0.0)
    soc_sp_others_total                       = models.FloatField(default= 0.0)
    soc_sp_others_weeks                       = models.FloatField(default= 0.0)

    soc_sp_grand_total_unit                   = models.FloatField(default= 0.0)
    soc_sp_grand_total_price_unit             = models.FloatField(default=0.0)
    soc_sp_grand_total_sum                    = models.FloatField(default= 0.0)
    soc_sp_grand_total_weeks                  = models.FloatField(default= 0.0)

    def __str__(self):
        return f'Set of Cavities - Asignacion {self.id_asignacion_id}'

    class Meta:
        db_table = 'Set_of_Cavities_Mold'