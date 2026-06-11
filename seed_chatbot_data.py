"""
seed_chatbot_data.py
Llena la base de datos con datos sintéticos para pruebas generales del sistema.

Prerequisito: los usuarios deben existir en la BD (créalos desde /admin/).

Usuarios requeridos:
    ind.usuario@bocar-test.mx  (rol Ind)
    com.usuario@bocar-test.mx  (rol Com)
    prov.alpha@bocar-test.mx   (rol Pro)

Uso:
    python seed_chatbot_data.py

Crea:
    - 1 perfil Proveedor para prov.alpha
    - 5 RFQ Mold   con todos los campos llenos (M1-M3 En_Com, M4-M5 En_Ind)
    - 3 RFQ Trimming con todos los campos llenos (T1-T2 En_Com, T3 En_Ind)
    - 2 asignaciones (M1 y T1 → prov.alpha)
"""

import os
import sys
import django
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Bocar'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import transaction
from users.models import CustomUser
from Proveedores.models import Proveedor
from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming
from Asignaciones.models import Asignacion_Proveedor_Mold, Asignacion_Proveedor_Trimming
from historial.models import RFQHistorial
from historial.services import registrar_historial

EMAIL_U1 = 'ind.usuario@bocar-test.mx'
EMAIL_U3 = 'com.usuario@bocar-test.mx'
EMAIL_U5 = 'prov.alpha@bocar-test.mx'

# ─── Datos completos RFQ Mold ────────────────────────────────────────────────

RFQS_MOLD = [
    dict(
        # Info general
        DESC='Soporte de transmision automatica - aleacion ADC12',
        PPY=45000, CUST='MAGNA Powertrain', PT='Transmission Bracket',
        PNUM='TXB-2026-001', PRLF=1.08, TT='High Pressure Die Casting',
        DTQ=date(2026, 8, 1), ELAB='Bocar Engineering Dept.',
        due_date=date(2026, 9, 15),
        # DCM
        SMACH='Buhler 900T', No_CAV='1', No_ofHS=2.0, No_ofMS=4.0,
        ThirdPSupp='N/A', No_subc='2', Jco='Yes', QcSys='IATF 16949',
        Ihtcs='Yes', Spin='No', HICS='Yes', CMGOM='No',
        SPforThermoR='Yes', NReturnV='4', VacV='Yes', ChillBl='2',
        No_Pl_Jco_sys='1', Oth='Slide unit required',
        # Data info (booleans + notas)
        D_3D=True,  D_3D_note='NX format required',
        FlAn=True,  FlAn_note='Moldflow report included',
        Run_des=True, Run_des_note='Runner balanced design',
        Run_and_over_mod=False, Run_and_over_mod_note='',
        ManProp=True, ManProp_note='Two proposals minimum',
        Ldi=True, Ldi_note='',
        Add_of_mach_st=False, Add_of_mach_st_note='',
        Sketch_d_conc_inc_s_dim=True, Sketch_d_conc_inc_s_dim_note='Include slide dimensions',
        D2_Dr_Des_PDF_CNF=True, D2_Dr_Des_PDF_CNF_note='PDF + CATIA V5',
        D3_Mod_solid_Native=True, D3_Mod_solid_Native_note='NX 12 or higher',
        # OT INF
        Comp_Die=True,  Comp_Die_note='Complete die set',
        Subseq_D=False, Subseq_D_note='',
        Set_of_repl_H13=True,  Set_of_repl_H13_note='H13 inserts x2',
        Sp_set_of_EI=True,  Sp_set_of_EI_note='Ejector pins included',
        FICF=True,  FICF_note='Fire and ice cooling channels',
        HCLS=False, HCLS_note='',
        Fr_Refur=False, Fr_Refur_note='',
        # OTHER Information
        Eyeb=True,  Eyeb_note='4 eyebolts M20',
        Oil_Water_Conn=True,  Oil_Water_Conn_note='Quick connect fittings',
        STM_1and2=True, STM_1and2_note='Shot to mold stages 1 and 2',
        CMM_dim_rep_cai=True,  CMM_dim_rep_cai_note='100% dimensional report',
        GOM_rep_ass=False, GOM_rep_ass_note='',
        H_val_subc_in=True,  H_val_subc_in_note='Subcontract validation included',
        Dim_corr_opt=True,  Dim_corr_opt_note='3 correction rounds included',
        Sp_Pt=True,  Sp_Pt_note='Spare part list required',
        # Part Geometry
        alloy='ADC12', part_dim_length_mm=385.0, part_dim_width_mm=210.0,
        part_dim_height_mm=95.0, min_wall_thickness_mm=2.8,
        max_wall_thickness_mm=12.0, projected_area_cm2=480.0,
        surface_cm2=1250.0, volume_cm3=820.0, gross_weight_g=2214.0,
        # Tool Specification
        number_of_gates_per_part=2, number_of_parts_per_stroke=1,
        number_of_tools=1,
        comments='Pieza estructural, tolerancias criticas en zona de montaje. Requiere certificacion IATF.',
    ),
    dict(
        DESC='Carcasa bomba de aceite motor V6 - zinc ZA8',
        PPY=120000, CUST='NEMAK', PT='Oil Pump Housing',
        PNUM='OPH-2026-002', PRLF=1.05, TT='High Pressure Die Casting',
        DTQ=date(2026, 9, 1), ELAB='NEMAK Engineering',
        due_date=date(2026, 10, 1),
        SMACH='Frech 630T', No_CAV='2', No_ofHS=0.0, No_ofMS=6.0,
        ThirdPSupp='N/A', No_subc='0', Jco='No', QcSys='IATF 16949',
        Ihtcs='No', Spin='Yes', HICS='No', CMGOM='Yes',
        SPforThermoR='No', NReturnV='6', VacV='No', ChillBl='4',
        No_Pl_Jco_sys='0', Oth='',
        D_3D=True,  D_3D_note='CATIA V5 format',
        FlAn=False, FlAn_note='',
        Run_des=True, Run_des_note='',
        Run_and_over_mod=True, Run_and_over_mod_note='Runner modification allowed',
        ManProp=True, ManProp_note='Single proposal accepted',
        Ldi=False, Ldi_note='',
        Add_of_mach_st=True, Add_of_mach_st_note='2 additional machining stations',
        Sketch_d_conc_inc_s_dim=True, Sketch_d_conc_inc_s_dim_note='',
        D2_Dr_Des_PDF_CNF=True, D2_Dr_Des_PDF_CNF_note='',
        D3_Mod_solid_Native=True, D3_Mod_solid_Native_note='CATIA V5 native',
        Comp_Die=True, Comp_Die_note='',
        Subseq_D=True, Subseq_D_note='Sequential die included',
        Set_of_repl_H13=True, Set_of_repl_H13_note='',
        Sp_set_of_EI=False, Sp_set_of_EI_note='',
        FICF=False, FICF_note='',
        HCLS=True, HCLS_note='Hot chamber lubrication system',
        Fr_Refur=True, Fr_Refur_note='Frame refurbishment after 100k shots',
        Eyeb=True, Eyeb_note='6 eyebolts M16',
        Oil_Water_Conn=True, Oil_Water_Conn_note='',
        STM_1and2=False, STM_1and2_note='',
        CMM_dim_rep_cai=True, CMM_dim_rep_cai_note='',
        GOM_rep_ass=True, GOM_rep_ass_note='GOM scan full assembly',
        H_val_subc_in=False, H_val_subc_in_note='',
        Dim_corr_opt=True, Dim_corr_opt_note='2 correction rounds',
        Sp_Pt=True, Sp_Pt_note='',
        alloy='ZA8', part_dim_length_mm=220.0, part_dim_width_mm=185.0,
        part_dim_height_mm=60.0, min_wall_thickness_mm=2.0,
        max_wall_thickness_mm=8.5, projected_area_cm2=280.0,
        surface_cm2=760.0, volume_cm3=310.0, gross_weight_g=2108.0,
        number_of_gates_per_part=1, number_of_parts_per_stroke=2,
        number_of_tools=1,
        comments='Acabado interno clase A, sin porosidad admisible. Alta cadencia.',
    ),
    dict(
        DESC='Bracket suspension delantera - aluminio A380',
        PPY=80000, CUST='Stellantis Mexico', PT='Front Suspension Bracket',
        PNUM='FSB-2026-003', PRLF=1.10, TT='High Pressure Die Casting',
        DTQ=date(2026, 7, 15), ELAB='Stellantis Tooling Dept.',
        due_date=date(2026, 8, 20),
        SMACH='Buhler 1250T', No_CAV='1', No_ofHS=4.0, No_ofMS=2.0,
        ThirdPSupp='ABC Tooling', No_subc='1', Jco='Yes', QcSys='IATF 16949 + AIAG',
        Ihtcs='Yes', Spin='No', HICS='Yes', CMGOM='Yes',
        SPforThermoR='Yes', NReturnV='2', VacV='Yes', ChillBl='6',
        No_Pl_Jco_sys='2', Oth='Special slide locking required',
        D_3D=True, D_3D_note='STEP + NX format',
        FlAn=True, FlAn_note='Magmasoft simulation required',
        Run_des=True, Run_des_note='Balanced runner mandatory',
        Run_and_over_mod=False, Run_and_over_mod_note='',
        ManProp=True, ManProp_note='Min 3 proposals',
        Ldi=True, Ldi_note='LDPC report required',
        Add_of_mach_st=True, Add_of_mach_st_note='4 CNC stations',
        Sketch_d_conc_inc_s_dim=True, Sketch_d_conc_inc_s_dim_note='All slide dims required',
        D2_Dr_Des_PDF_CNF=True, D2_Dr_Des_PDF_CNF_note='',
        D3_Mod_solid_Native=True, D3_Mod_solid_Native_note='',
        Comp_Die=True, Comp_Die_note='Full die set with spares',
        Subseq_D=False, Subseq_D_note='',
        Set_of_repl_H13=True, Set_of_repl_H13_note='H13 cores x4',
        Sp_set_of_EI=True, Sp_set_of_EI_note='',
        FICF=True, FICF_note='Conformal cooling channels',
        HCLS=False, HCLS_note='',
        Fr_Refur=False, Fr_Refur_note='',
        Eyeb=True, Eyeb_note='8 eyebolts M24',
        Oil_Water_Conn=True, Oil_Water_Conn_note='Manifold required',
        STM_1and2=True, STM_1and2_note='',
        CMM_dim_rep_cai=True, CMM_dim_rep_cai_note='200% first article inspection',
        GOM_rep_ass=True, GOM_rep_ass_note='',
        H_val_subc_in=True, H_val_subc_in_note='',
        Dim_corr_opt=True, Dim_corr_opt_note='4 rounds included',
        Sp_Pt=True, Sp_Pt_note='Complete BOM required',
        alloy='A380', part_dim_length_mm=520.0, part_dim_width_mm=310.0,
        part_dim_height_mm=140.0, min_wall_thickness_mm=3.5,
        max_wall_thickness_mm=18.0, projected_area_cm2=920.0,
        surface_cm2=2800.0, volume_cm3=1650.0, gross_weight_g=4455.0,
        number_of_gates_per_part=3, number_of_parts_per_stroke=1,
        number_of_tools=1,
        comments='Pieza de seguridad, requiere certificacion IATF y FMEA nivel alto.',
    ),
    dict(
        DESC='Tapa de valvulas motor 4 cilindros - aluminio A360',
        PPY=200000, CUST='Toyota Motor de Mexico', PT='Valve Cover',
        PNUM='VCV-2026-004', PRLF=1.06, TT='High Pressure Die Casting',
        DTQ=date(2026, 10, 1), ELAB='Toyota Supplier Portal',
        due_date=date(2026, 11, 30),
        SMACH='Buhler 530T', No_CAV='2', No_ofHS=0.0, No_ofMS=8.0,
        ThirdPSupp='N/A', No_subc='0', Jco='No', QcSys='IATF 16949 + Toyota SQAM',
        Ihtcs='No', Spin='No', HICS='No', CMGOM='No',
        SPforThermoR='No', NReturnV='8', VacV='No', ChillBl='0',
        No_Pl_Jco_sys='0', Oth='',
        D_3D=True, D_3D_note='',
        FlAn=False, FlAn_note='',
        Run_des=True, Run_des_note='',
        Run_and_over_mod=False, Run_and_over_mod_note='',
        ManProp=True, ManProp_note='',
        Ldi=False, Ldi_note='',
        Add_of_mach_st=False, Add_of_mach_st_note='',
        Sketch_d_conc_inc_s_dim=True, Sketch_d_conc_inc_s_dim_note='',
        D2_Dr_Des_PDF_CNF=True, D2_Dr_Des_PDF_CNF_note='',
        D3_Mod_solid_Native=True, D3_Mod_solid_Native_note='CATIA V5',
        Comp_Die=True, Comp_Die_note='',
        Subseq_D=False, Subseq_D_note='',
        Set_of_repl_H13=False, Set_of_repl_H13_note='',
        Sp_set_of_EI=True, Sp_set_of_EI_note='',
        FICF=False, FICF_note='',
        HCLS=False, HCLS_note='',
        Fr_Refur=False, Fr_Refur_note='',
        Eyeb=True, Eyeb_note='4 eyebolts M16',
        Oil_Water_Conn=True, Oil_Water_Conn_note='',
        STM_1and2=False, STM_1and2_note='',
        CMM_dim_rep_cai=True, CMM_dim_rep_cai_note='',
        GOM_rep_ass=False, GOM_rep_ass_note='',
        H_val_subc_in=False, H_val_subc_in_note='',
        Dim_corr_opt=True, Dim_corr_opt_note='2 rounds',
        Sp_Pt=False, Sp_Pt_note='',
        alloy='A360', part_dim_length_mm=460.0, part_dim_width_mm=180.0,
        part_dim_height_mm=55.0, min_wall_thickness_mm=2.5,
        max_wall_thickness_mm=7.0, projected_area_cm2=560.0,
        surface_cm2=1480.0, volume_cm3=640.0, gross_weight_g=1728.0,
        number_of_gates_per_part=2, number_of_parts_per_stroke=2,
        number_of_tools=1,
        comments='Alta cadencia, herramienta de 4 cavidades. Proceso automatizado.',
    ),
    dict(
        DESC='Pedal de freno aluminio die cast - vehiculo electrico',
        PPY=60000, CUST='Continental Automotive', PT='Brake Pedal Arm',
        PNUM='BPA-2026-005', PRLF=1.12, TT='High Pressure Die Casting',
        DTQ=date(2026, 11, 1), ELAB='Continental Sourcing Team',
        due_date=date(2026, 12, 15),
        SMACH='Idra 800T', No_CAV='1', No_ofHS=2.0, No_ofMS=3.0,
        ThirdPSupp='EV Parts MX', No_subc='1', Jco='Yes', QcSys='IATF 16949',
        Ihtcs='Yes', Spin='No', HICS='Yes', CMGOM='No',
        SPforThermoR='Yes', NReturnV='3', VacV='Yes', ChillBl='2',
        No_Pl_Jco_sys='1', Oth='EV specific requirements apply',
        D_3D=True, D_3D_note='NX format, EV platform',
        FlAn=True, FlAn_note='Moldflow mandatory for EV',
        Run_des=True, Run_des_note='',
        Run_and_over_mod=False, Run_and_over_mod_note='',
        ManProp=True, ManProp_note='',
        Ldi=True, Ldi_note='',
        Add_of_mach_st=False, Add_of_mach_st_note='',
        Sketch_d_conc_inc_s_dim=True, Sketch_d_conc_inc_s_dim_note='',
        D2_Dr_Des_PDF_CNF=True, D2_Dr_Des_PDF_CNF_note='',
        D3_Mod_solid_Native=True, D3_Mod_solid_Native_note='',
        Comp_Die=True, Comp_Die_note='',
        Subseq_D=False, Subseq_D_note='',
        Set_of_repl_H13=True, Set_of_repl_H13_note='H13 x2',
        Sp_set_of_EI=True, Sp_set_of_EI_note='',
        FICF=True, FICF_note='',
        HCLS=False, HCLS_note='',
        Fr_Refur=False, Fr_Refur_note='',
        Eyeb=True, Eyeb_note='',
        Oil_Water_Conn=True, Oil_Water_Conn_note='',
        STM_1and2=True, STM_1and2_note='',
        CMM_dim_rep_cai=True, CMM_dim_rep_cai_note='',
        GOM_rep_ass=False, GOM_rep_ass_note='',
        H_val_subc_in=True, H_val_subc_in_note='',
        Dim_corr_opt=True, Dim_corr_opt_note='3 rounds',
        Sp_Pt=True, Sp_Pt_note='',
        alloy='A380', part_dim_length_mm=310.0, part_dim_width_mm=95.0,
        part_dim_height_mm=75.0, min_wall_thickness_mm=3.0,
        max_wall_thickness_mm=14.0, projected_area_cm2=195.0,
        surface_cm2=580.0, volume_cm3=360.0, gross_weight_g=972.0,
        number_of_gates_per_part=1, number_of_parts_per_stroke=1,
        number_of_tools=1,
        comments='Nuevo proyecto EV, geometria en revision con cliente. Pieza de seguridad.',
    ),
]

# ─── Datos completos RFQ Trimming ────────────────────────────────────────────

RFQS_TRIMMING = [
    dict(
        DESC='Herramental de trim para soporte de motor - ADC12',
        PPY=95000, CUST='MAGNA Powertrain', PNUM='TRM-2026-101',
        PRLF=1.07, DTQ=date(2026, 9, 1),
        due_date=date(2026, 9, 30),
        # DCM
        press='200T Hydraulic Press',
        no_of_cavities=1,
        no_of_hydraulic_slides='2',
        fully_automatic_process='Yes',
        presence_detectors='Yes - inductive sensors',
        trimming_process_condition='Hot trimming 280°C',
        admissible_residual_burr_mm=0.3,
        castings_supplied_by_auma='Yes',
        adjustments_optimization_at_tool='3 rounds included',
        gas_springs='4 x 40kN',
        # Data info
        di_design_3d_model=True,  di_design_3d_model_note='NX format',
        di_design_2d_data=True,   di_design_2d_data_note='PDF + DXF',
        di_punch_pins_data=True,  di_punch_pins_data_note='Complete punch pin layout',
        di_manufacturing_proposals=True, di_manufacturing_proposals_note='2 proposals min',
        di_latest_trim_die_improvements=False, di_latest_trim_die_improvements_note='',
        di_sketch_trim_die_concept=True, di_sketch_trim_die_concept_note='',
        di_trim_die_no1=True,  di_trim_die_no1_note='',
        di_trim_die_no2=False, di_trim_die_no2_note='',
        di_set_of_spare_parts=True, di_set_of_spare_parts_note='Wear parts x2',
        di_hydraulic_cylinders_limit_sw=True, di_hydraulic_cylinders_limit_sw_note='Proximity sensors',
        # Other info
        oi_frame_refurbishment=False,
        oi_set_of_electric_wires=True,
        oi_others='Pneumatic blow-off included',
        oi_delivery_date_imex=date(2026, 8, 15),
        oi_ejector_system_fixed_side='Spring return ejectors',
        # Part geometry
        part_name='Engine Mount Trim', part_number='EMT-101',
        part_dim_length_mm=385.0, part_dim_width_mm=210.0,
        part_dim_height_mm=95.0, min_wall_thickness_mm=2.8,
        max_wall_thickness_mm=12.0, projected_area_cm2=480.0,
        surface_cm2=1250.0, volume_cm3=820.0, gross_weight_g=2214.0,
        # Tool spec
        press_type='Hydraulic vertical',
        introduction_extraction_process='Robot arm extraction',
        biscuit_position='Bottom center',
        quantity_of_punch_pins='12',
        temperature_when_trimmed='280',
        comments='Proceso completamente automatico, detectores de presencia requeridos.',
    ),
    dict(
        DESC='Trim de carcasa diferencial trasero - aluminio A380',
        PPY=55000, CUST='ZF Mexico', PNUM='TRM-2026-102',
        PRLF=1.09, DTQ=date(2026, 9, 20),
        due_date=date(2026, 10, 20),
        press='160T Mechanical Press',
        no_of_cavities=1,
        no_of_hydraulic_slides='1',
        fully_automatic_process='Semi-automatic',
        presence_detectors='Yes - capacitive sensors',
        trimming_process_condition='Cold trimming',
        admissible_residual_burr_mm=0.5,
        castings_supplied_by_auma='No',
        adjustments_optimization_at_tool='2 rounds',
        gas_springs='2 x 25kN',
        di_design_3d_model=True,  di_design_3d_model_note='CATIA V5',
        di_design_2d_data=True,   di_design_2d_data_note='',
        di_punch_pins_data=True,  di_punch_pins_data_note='',
        di_manufacturing_proposals=False, di_manufacturing_proposals_note='',
        di_latest_trim_die_improvements=True, di_latest_trim_die_improvements_note='Previous tool #TRM-2024-087 improvements',
        di_sketch_trim_die_concept=True, di_sketch_trim_die_concept_note='',
        di_trim_die_no1=True,  di_trim_die_no1_note='',
        di_trim_die_no2=True,  di_trim_die_no2_note='Secondary trim die',
        di_set_of_spare_parts=True, di_set_of_spare_parts_note='',
        di_hydraulic_cylinders_limit_sw=False, di_hydraulic_cylinders_limit_sw_note='',
        oi_frame_refurbishment=True,
        oi_set_of_electric_wires=True,
        oi_others='',
        oi_delivery_date_imex=date(2026, 10, 1),
        oi_ejector_system_fixed_side='Air ejection',
        part_name='Rear Differential Housing Trim', part_number='RDH-102',
        part_dim_length_mm=420.0, part_dim_width_mm=280.0,
        part_dim_height_mm=185.0, min_wall_thickness_mm=3.2,
        max_wall_thickness_mm=15.0, projected_area_cm2=720.0,
        surface_cm2=2100.0, volume_cm3=1380.0, gross_weight_g=3726.0,
        press_type='Mechanical eccentric',
        introduction_extraction_process='Manual extraction with fixture',
        biscuit_position='Side offset',
        quantity_of_punch_pins='8',
        temperature_when_trimmed='ambient',
        comments='Requiere resortes de gas, operacion semiautomatica.',
    ),
    dict(
        DESC='Trim para bracket de suspension - A380',
        PPY=75000, CUST='Stellantis Mexico', PNUM='TRM-2026-103',
        PRLF=1.11, DTQ=date(2026, 10, 15),
        due_date=date(2026, 11, 10),
        press='250T Hydraulic Press',
        no_of_cavities=1,
        no_of_hydraulic_slides='4',
        fully_automatic_process='Yes',
        presence_detectors='Yes - laser sensors',
        trimming_process_condition='Hot trimming 320°C',
        admissible_residual_burr_mm=0.2,
        castings_supplied_by_auma='Yes',
        adjustments_optimization_at_tool='4 rounds',
        gas_springs='6 x 50kN',
        di_design_3d_model=True,  di_design_3d_model_note='NX + STEP',
        di_design_2d_data=True,   di_design_2d_data_note='Complete 2D package',
        di_punch_pins_data=True,  di_punch_pins_data_note='All pins documented',
        di_manufacturing_proposals=True, di_manufacturing_proposals_note='3 proposals required',
        di_latest_trim_die_improvements=True, di_latest_trim_die_improvements_note='FMEA driven improvements',
        di_sketch_trim_die_concept=True, di_sketch_trim_die_concept_note='Preliminary concept included',
        di_trim_die_no1=True,  di_trim_die_no1_note='',
        di_trim_die_no2=False, di_trim_die_no2_note='',
        di_set_of_spare_parts=True, di_set_of_spare_parts_note='Critical wear parts x3',
        di_hydraulic_cylinders_limit_sw=True, di_hydraulic_cylinders_limit_sw_note='All cylinders monitored',
        oi_frame_refurbishment=False,
        oi_set_of_electric_wires=True,
        oi_others='Scrap chute included',
        oi_delivery_date_imex=date(2026, 10, 20),
        oi_ejector_system_fixed_side='Hydraulic ejectors',
        part_name='Suspension Bracket Trim', part_number='SBT-103',
        part_dim_length_mm=520.0, part_dim_width_mm=310.0,
        part_dim_height_mm=140.0, min_wall_thickness_mm=3.5,
        max_wall_thickness_mm=18.0, projected_area_cm2=920.0,
        surface_cm2=2800.0, volume_cm3=1650.0, gross_weight_g=4455.0,
        press_type='Hydraulic vertical double-action',
        introduction_extraction_process='Robot arm with vision system',
        biscuit_position='Center top',
        quantity_of_punch_pins='18',
        temperature_when_trimmed='320',
        comments='Rebaba admisible 0.2mm, pieza de seguridad FMEA nivel alto. Requiere certificacion IATF.',
    ),
]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_usuario(email):
    try:
        user = CustomUser.objects.get(email=email)
        print(f'  [✓] Usuario: {user.email} (rol={user.role})')
        return user
    except CustomUser.DoesNotExist:
        print(f'  [✗] ERROR: Usuario no encontrado: {email}')
        print(f'      Créalo desde /admin/ antes de ejecutar este script.')
        sys.exit(1)


def _crear_rfq_mold(data, creado_por):
    rfq = RFQ_Mold.objects.create(created_by=creado_por, **data)
    registrar_historial(
        rfq_tipo=RFQHistorial.Tipo.MOLD, rfq_id=rfq.id,
        evento=RFQHistorial.Evento.CREACION, actor=creado_por,
        status_nuevo=rfq.status,
    )
    print(f'  [+] RFQ Mold  #{rfq.id}: {rfq.DESC[:50]}')
    return rfq


def _crear_rfq_trimming(data, creado_por):
    rfq = RFQ_Trimming.objects.create(created_by=creado_por, **data)
    registrar_historial(
        rfq_tipo=RFQHistorial.Tipo.TRIMMING, rfq_id=rfq.id,
        evento=RFQHistorial.Evento.CREACION, actor=creado_por,
        status_nuevo=rfq.status,
    )
    print(f'  [+] RFQ Trim  #{rfq.id}: {rfq.DESC[:50]}')
    return rfq


def _enviar_a_com(rfq, tipo, actor):
    anterior = rfq.status
    rfq.status = RFQ_Mold.Status.COMERCIALIZACION
    rfq.save()
    registrar_historial(
        rfq_tipo=tipo, rfq_id=rfq.id,
        evento=RFQHistorial.Evento.ENVIO_COMERCIALIZACION, actor=actor,
        status_anterior=anterior, status_nuevo=rfq.status,
    )
    print(f'  [→] {tipo} #{rfq.id} → En_Com')


@transaction.atomic
def seed():
    print('\n=== Verificando usuarios ===')
    u1 = _get_usuario(EMAIL_U1)
    u3 = _get_usuario(EMAIL_U3)
    u5 = _get_usuario(EMAIL_U5)

    print('\n=== Perfil de proveedor (U5) ===')
    proveedor, created = Proveedor.objects.get_or_create(
        id_account=u5,
        defaults=dict(
            company_name='Alpha Tooling S.A. de C.V.',
            contact_email=u5.email,
            continent='NA',
            rating=4.2,
        ),
    )
    print(f'  {"[+]" if created else "[=]"} {proveedor.company_name}')

    print('\n=== RFQs Mold ===')
    molds = [_crear_rfq_mold(d, u1) for d in RFQS_MOLD]
    m1, m2, m3, m4, m5 = molds

    print('\n=== RFQs Trimming ===')
    trimmings = [_crear_rfq_trimming(d, u1) for d in RFQS_TRIMMING]
    t1, t2, t3 = trimmings

    print('\n=== Enviando a Comercialización (M1-M3, T1-T2) ===')
    for rfq in (m1, m2, m3):
        _enviar_a_com(rfq, RFQHistorial.Tipo.MOLD, u1)
    for rfq in (t1, t2):
        _enviar_a_com(rfq, RFQHistorial.Tipo.TRIMMING, u1)

    print('\n=== Asignaciones → prov.alpha ===')
    a1 = Asignacion_Proveedor_Mold.objects.create(
        id_RFQ_Mold=m1, id_Proveedor=proveedor,
        id_user_comercializacion=u3, due_date=m1.due_date,
    )
    print(f'  [+] Asig Mold    #{a1.id}: RFQ#{m1.id} → {proveedor.company_name}')

    a2 = Asignacion_Proveedor_Trimming.objects.create(
        id_RFQ_Trimming=t1, id_Proveedor=proveedor,
        id_user_comercializacion=u3, due_date=t1.due_date,
    )
    print(f'  [+] Asig Trimming #{a2.id}: RFQ#{t1.id} → {proveedor.company_name}')

    print('\n─── Estado final ───────────────────────────────────────')
    print(f'  Mold  En_Com : #{m1.id} {m1.CUST} | #{m2.id} {m2.CUST} | #{m3.id} {m3.CUST}')
    print(f'  Mold  En_Ind : #{m4.id} {m4.CUST} | #{m5.id} {m5.CUST}')
    print(f'  Trim  En_Com : #{t1.id} {t1.CUST} | #{t2.id} {t2.CUST}')
    print(f'  Trim  En_Ind : #{t3.id} {t3.CUST}')
    print(f'  Asignaciones : {a1.id} (Mold), {a2.id} (Trimming)')
    print('\n✓ Seed completado.\n')


if __name__ == '__main__':
    seed()
