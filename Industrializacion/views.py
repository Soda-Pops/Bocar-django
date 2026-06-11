from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser

from users.permissions import IsIndustrializacionUser
from General_RFQs.utils import validar_archivos
from django.conf import settings
from django.db import models, transaction

from RFQ_Mold.models import RFQ_Mold, RFQ_Mold_EditRequest
from RFQ_Mold.serializers import (
    RFQMoldCreateSerializer,
    RFQMoldDetailSerializer,
    RFQMoldListSerializer,
    MoldEditRequestCreateSerializer,
)
from RFQ_Trimming.models import RFQ_Trimming, RFQ_Trimming_EditRequest
from RFQ_Trimming.serializers import (
    RFQTrimmingCreateSerializer,
    RFQTrimmingDetailSerializer,
    RFQTrimmingListSerializer,
    TrimmingEditRequestCreateSerializer,
)

from notificaciones import tasks as notif_tasks
from notificaciones.services import ROL_COMERCIALIZACION

from historial.models import RFQHistorial
from historial.services import registrar_historial, diff_campos

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_tipo(request):
    return request.query_params.get('tipo', '').lower()

def _tipo_invalido():
    return Response(
        {'detail': "El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."},
        status=status.HTTP_400_BAD_REQUEST,
    )

MOLD_SUBMIT_REQUIRED_FIELDS = [
    'due_date', 'DESC', 'PPY', 'CUST', 'PT', 'PNUM', 'PRLF', 'TT', 'DTQ', 'ELAB',
    'SMACH', 'No_CAV', 'No_ofHS', 'No_ofMS', 'ThirdPSupp', 'No_subc', 'Jco', 'QcSys',
    'Ihtcs', 'Spin', 'HICS', 'CMGOM', 'SPforThermoR', 'NReturnV',
    # VacV y ChillBl son mutuamente excluyentes (regla "uno u otro"): la UI bloquea
    # el que no aplica y ambos pueden quedar en 0, por eso NO se exigen aquí.
    'No_Pl_Jco_sys', 'Oth',
    'D_3D', 'D_3D_note', 'FlAn', 'FlAn_note', 'Run_des', 'Run_des_note',
    'Run_and_over_mod', 'Run_and_over_mod_note', 'ManProp', 'ManProp_note', 'Ldi',
    'Ldi_note', 'Add_of_mach_st', 'Add_of_mach_st_note', 'Sketch_d_conc_inc_s_dim',
    'Sketch_d_conc_inc_s_dim_note', 'D2_Dr_Des_PDF_CNF', 'D2_Dr_Des_PDF_CNF_note',
    'D3_Mod_solid_Native', 'D3_Mod_solid_Native_note',
    'Comp_Die', 'Comp_Die_note', 'Subseq_D', 'Subseq_D_note', 'Set_of_repl_H13',
    'Set_of_repl_H13_note', 'Sp_set_of_EI', 'Sp_set_of_EI_note', 'FICF', 'FICF_note',
    'HCLS', 'HCLS_note', 'Fr_Refur', 'Fr_Refur_note',
    'Eyeb', 'Eyeb_note', 'Oil_Water_Conn', 'Oil_Water_Conn_note', 'STM_1and2',
    'STM_1and2_note', 'CMM_dim_rep_cai', 'CMM_dim_rep_cai_note', 'GOM_rep_ass',
    'GOM_rep_ass_note', 'H_val_subc_in', 'H_val_subc_in_note', 'Dim_corr_opt',
    'Dim_corr_opt_note', 'Sp_Pt', 'Sp_Pt_note',
    'part_name', 'alloy', 'part_dim_length_mm', 'part_dim_width_mm', 'part_dim_height_mm',
    'min_wall_thickness_mm', 'max_wall_thickness_mm', 'projected_area_cm2', 'surface_cm2',
    'volume_cm3', 'gross_weight_g', 'three_plate_mold', 'number_of_gates_per_part',
    'number_of_parts_per_stroke', 'number_of_tools', 'comments',
]

TRIMMING_SUBMIT_REQUIRED_FIELDS = [
    # 1. RFQ
    'due_date', 'DESC', 'PPY', 'CUST', 'PNUM', 'PRLF', 'previous_job',
    # 2. Trim Die
    'press', 'no_of_cavities', 'no_of_hydraulic_slides', 'fully_automatic_process',
    'presence_detectors', 'trimming_process_condition', 'punch_pins_required',
    'admissible_residual_burr_mm', 'castings_supplied_by_auma',
    'adjustments_optimization_at_tool', 'gas_springs',
    # 3. Data Information (toggle + nota)
    'di_design_3d_model', 'di_design_3d_model_note',
    'di_design_2d_data', 'di_design_2d_data_note',
    'di_punch_pins_data', 'di_punch_pins_data_note',
    'di_manufacturing_proposals', 'di_manufacturing_proposals_note',
    'di_latest_trim_die_improvements', 'di_latest_trim_die_improvements_note',
    'di_sketch_trim_die_concept', 'di_sketch_trim_die_concept_note',
    # 4. Other Information (toggle + nota)
    'di_trim_die_no1', 'di_trim_die_no1_note',
    'di_trim_die_no2', 'di_trim_die_no2_note',
    'di_set_of_spare_parts', 'di_set_of_spare_parts_note',
    'di_hydraulic_cylinders_limit_sw', 'di_hydraulic_cylinders_limit_sw_note',
    'oi_frame_refurbishment', 'oi_frame_refurbishment_note',
    'oi_set_of_electric_wires', 'oi_set_of_electric_wires_note',
    'oi_others_applies', 'oi_others',
    'oi_delivery_date_imex_applies',
    # oi_delivery_date_imex is only required when oi_delivery_date_imex_applies=True (checked below)
    'oi_ejector_fixed_applies', 'oi_ejector_fixed_note',
    # 6. Part Geometry
    'part_name', 'part_number', 'part_dimension',
    'min_wall_thickness_mm', 'max_wall_thickness_mm',
    'projected_area_cm2', 'surface_cm2', 'volume_cm3', 'gross_weight_g',
    # 7. Tool Specification
    'introduction_extraction_process', 'biscuit_position',
    'quantity_of_punch_pins', 'temperature_when_trimmed',
    'oi_ejector_system_fixed_side',
    # 8. Comments
    'comments',
]


def _field_is_missing(rfq, field_name):
    field = rfq._meta.get_field(field_name)
    value = getattr(rfq, field_name, None)

    if isinstance(field, models.BooleanField):
        return value is None
    if isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
        return value is None
    if isinstance(field, (models.DateField, models.DateTimeField)):
        return value is None
    if isinstance(field, (models.CharField, models.TextField)):
        return value is None or not str(value).strip()
    return value is None


def _validar_completitud(rfq, tipo):
    required_fields = MOLD_SUBMIT_REQUIRED_FIELDS if tipo == 'mold' else TRIMMING_SUBMIT_REQUIRED_FIELDS
    missing = []
    for field_name in required_fields:
        try:
            if _field_is_missing(rfq, field_name):
                missing.append(field_name)
        except Exception:
            missing.append(field_name)

    if tipo == 'trimming' and getattr(rfq, 'oi_delivery_date_imex_applies', False):
        if not getattr(rfq, 'oi_delivery_date_imex', None):
            missing.append('oi_delivery_date_imex')

    if missing:
        return Response(
            {
                'detail': 'El RFQ tiene campos obligatorios incompletos.',
                'code': 'rfq_incompleto',
                'missing_fields': missing,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None

_TIPO_PARAM = OpenApiParameter(
    name='tipo',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    enum=['mold', 'trimming'],
    description="Tipo de RFQ: 'mold' o 'trimming'",
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. CREAR RFQ
# ─────────────────────────────────────────────────────────────────────────────

class RFQCrearView(APIView):
    """
    POST /api_industrializacion/v1/rfq/?tipo=mold|trimming
    Crea un nuevo RFQ del tipo indicado.
    Acepta archivos opcionales bajo el key 'archivos' (multipart/form-data).
    El campo created_by se asigna automáticamente.
    Requiere role='Ind'.
    """
    permission_classes = [IsIndustrializacionUser]
    parser_classes     = [MultiPartParser, JSONParser]

    @extend_schema(
        summary="Crear RFQ",
        description="""
            Crea un nuevo RFQ de tipo mold o trimming según el parámetro 'tipo'.
            Enviar como multipart/form-data si se incluyen archivos adjuntos.
            El status inicial debe ser En_Ind.
            Requiere autenticación.

            El cuerpo del request varía según `tipo`:
            - `tipo=mold` → campos de `RFQMoldCreateSerializer`.
            - `tipo=trimming` → campos de `RFQTrimmingCreateSerializer`.
        """,
        parameters=[_TIPO_PARAM],
        request=RFQMoldCreateSerializer,
        responses={
            201: inline_serializer(
                name='RFQCrearResponse',
                fields={
                    'detail': serializers.CharField(),
                    'id': serializers.IntegerField(),
                }
            ),
            400: inline_serializer(
                name='RFQCrearBadRequest',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def post(self, request):
        tipo = _get_tipo(request)
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            SerializerClass = RFQMoldCreateSerializer
        else:
            SerializerClass = RFQTrimmingCreateSerializer

        archivos = request.FILES.getlist('archivos')
        errores  = validar_archivos(archivos)
        if errores:
            return Response(
                {'detail': 'Los archivos adjuntos no son válidos.', **errores},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SerializerClass(data=request.data)
        serializer.is_valid(raise_exception=True)
        rfq = serializer.save(created_by=request.user, archivos=archivos)

        return Response(
            {
                'detail': f'RFQ {tipo.capitalize()} creado correctamente.',
                'id': rfq.id,
            },
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. EDITAR RFQ (solo mientras está en En_Ind)
# ─────────────────────────────────────────────────────────────────────────────

class RFQEditarView(APIView):
    """
    PATCH /api_industrializacion/v1/rfq/<id>/?tipo=mold|trimming
    Edita un RFQ existente. Solo permitido mientras el status sea En_Ind.
    Si el RFQ ya está en En_Com o En_Pro la edición es rechazada.
    Para desbloquearlo debe tramitarse una solicitud de edición aprobada.
    Requiere role='Ind'. Solo el creador puede editar, salvo is_admin=True.
    """
    permission_classes = [IsIndustrializacionUser]
    parser_classes     = [MultiPartParser, JSONParser]

    @extend_schema(
        summary="Editar RFQ (solo en En_Ind)",
        description="""
            Actualiza los campos de un RFQ. Solo se permite si el RFQ está en
            status En_Ind. Si está en En_Com o En_Pro se retorna 403.
            Requiere autenticación.

            El cuerpo del request varía según `tipo`:
            - `tipo=mold` → campos de `RFQMoldCreateSerializer` (partial).
            - `tipo=trimming` → campos de `RFQTrimmingCreateSerializer` (partial).
        """,
        parameters=[_TIPO_PARAM],
        request=RFQMoldCreateSerializer,
        responses={
            200: inline_serializer(
                name='RFQEditarResponse',
                fields={'detail': serializers.CharField()}
            ),
            403: inline_serializer(
                name='RFQEditarForbidden',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='RFQEditarNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def patch(self, request, pk):
        tipo = _get_tipo(request)
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            try:
                rfq = RFQ_Mold.objects.get(pk=pk, logical_delete=False)
            except RFQ_Mold.DoesNotExist:
                return Response(
                    {'detail': 'RFQ Mold no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if rfq.created_by != request.user and not request.user.is_admin:
                return Response(
                    {'detail': 'No tienes permiso para editar este RFQ.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if rfq.status != RFQ_Mold.Status.INDUSTRIALIZACION:
                return Response(
                    {'detail': 'El RFQ ya fue enviado y no puede editarse directamente. '
                               'Solicita una edición a Comercialización.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            archivos = request.FILES.getlist('archivos')
            errores  = validar_archivos(archivos)
            if errores:
                return Response(
                    {'detail': 'Los archivos adjuntos no son válidos.', **errores},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = RFQMoldCreateSerializer(rfq, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            cambios = diff_campos(rfq, serializer.validated_data)
            serializer.save(archivos=archivos)

            if cambios:
                registrar_historial(
                    rfq_tipo = RFQHistorial.Tipo.MOLD,
                    rfq_id   = rfq.id,
                    evento   = RFQHistorial.Evento.EDICION,
                    actor    = request.user,
                    cambios  = cambios,
                )

        else:
            try:
                rfq = RFQ_Trimming.objects.get(pk=pk, logical_delete=False)
            except RFQ_Trimming.DoesNotExist:
                return Response(
                    {'detail': 'RFQ Trimming no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if rfq.created_by != request.user and not request.user.is_admin:
                return Response(
                    {'detail': 'No tienes permiso para editar este RFQ.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if rfq.status != RFQ_Trimming.Status.INDUSTRIALIZACION:
                return Response(
                    {'detail': 'El RFQ ya fue enviado y no puede editarse directamente. '
                               'Solicita una edición a Comercialización.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            archivos = request.FILES.getlist('archivos')
            errores  = validar_archivos(archivos)
            if errores:
                return Response(
                    {'detail': 'Los archivos adjuntos no son válidos.', **errores},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = RFQTrimmingCreateSerializer(rfq, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            cambios = diff_campos(rfq, serializer.validated_data)
            serializer.save(archivos=archivos)

            if cambios:
                registrar_historial(
                    rfq_tipo = RFQHistorial.Tipo.TRIMMING,
                    rfq_id   = rfq.id,
                    evento   = RFQHistorial.Evento.EDICION,
                    actor    = request.user,
                    cambios  = cambios,
                )

        return Response(
            {'detail': f'RFQ {tipo.capitalize()} actualizado correctamente.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. ENVIAR RFQ A COMERCIALIZACIÓN (En_Ind → En_Com)
# ─────────────────────────────────────────────────────────────────────────────

class RFQEnviarAComercializacionView(APIView):
    """
    POST /api_industrializacion/v1/rfq/<id>/enviar/?tipo=mold|trimming
    Cambia el status del RFQ de En_Ind a En_Com.
    Solo se permite si el RFQ está actualmente en En_Ind.
    Requiere role='Ind'. Solo el creador puede enviar, salvo is_admin=True.
    """
    permission_classes = [IsIndustrializacionUser]

    @extend_schema(
        summary="Enviar RFQ a Comercialización",
        description="""
            Cambia el status del RFQ de En_Ind a En_Com (submit to purchasing).
            Solo se permite si el RFQ está en En_Ind y tiene al menos un archivo adjunto.
            No requiere cuerpo en el request.
            Requiere autenticación.
        """,
        parameters=[_TIPO_PARAM],
        request=None,
        responses={
            200: inline_serializer(
                name='RFQEnviarResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='RFQEnviarBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='RFQEnviarNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def post(self, request, pk):
        tipo = _get_tipo(request)
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            try:
                rfq = RFQ_Mold.objects.get(pk=pk, logical_delete=False)
            except RFQ_Mold.DoesNotExist:
                return Response(
                    {'detail': 'RFQ Mold no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if rfq.created_by != request.user and not request.user.is_admin:
                return Response(
                    {'detail': 'No tienes permiso para enviar este RFQ.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if rfq.status != RFQ_Mold.Status.INDUSTRIALIZACION:
                return Response(
                    {'detail': 'El RFQ solo puede enviarse a Comercialización desde el status En_Ind.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not rfq.archivos.exists():
                return Response(
                    {'detail': 'El RFQ debe tener al menos un archivo adjunto antes de enviarse.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            completeness_error = _validar_completitud(rfq, tipo)
            if completeness_error:
                return completeness_error

        else:
            try:
                rfq = RFQ_Trimming.objects.get(pk=pk, logical_delete=False)
            except RFQ_Trimming.DoesNotExist:
                return Response(
                    {'detail': 'RFQ Trimming no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if rfq.created_by != request.user and not request.user.is_admin:
                return Response(
                    {'detail': 'No tienes permiso para enviar este RFQ.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if rfq.status != RFQ_Trimming.Status.INDUSTRIALIZACION:
                return Response(
                    {'detail': 'El RFQ solo puede enviarse a Comercialización desde el status En_Ind.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not rfq.archivos.exists():
                return Response(
                    {'detail': 'El RFQ debe tener al menos un archivo adjunto antes de enviarse.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            completeness_error = _validar_completitud(rfq, tipo)
            if completeness_error:
                return completeness_error

        with transaction.atomic():
            if tipo == 'mold':
                rfq.status = RFQ_Mold.Status.COMERCIALIZACION
            else:
                rfq.status = RFQ_Trimming.Status.COMERCIALIZACION
            rfq.save(update_fields=['status'])
            registrar_historial(
                rfq_tipo        = tipo,
                rfq_id          = rfq.id,
                evento          = RFQHistorial.Evento.ENVIO_COMERCIALIZACION,
                actor           = request.user,
                status_anterior = 'En_Ind',
                status_nuevo    = 'En_Com',
            )
            if settings.NOTIFICATIONS_ENABLED:
                transaction.on_commit(
                    lambda: notif_tasks.notificar_comercializacion.delay(rfq.id, tipo)
                )

        return Response(
            {'detail': f'RFQ {tipo.capitalize()} enviado a Comercialización correctamente.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. SOLICITAR EDICIÓN (pide regresar de En_Com a En_Ind)
# ─────────────────────────────────────────────────────────────────────────────

class RFQSolicitarEdicionView(APIView):
    """
    POST /api_industrializacion/v1/edit-requests/?tipo=mold|trimming
    Crea una solicitud para regresar el RFQ de En_Com a En_Ind.
    Solo válido si el RFQ está en En_Com y no hay otra solicitud Pendiente.
    Requiere role='Ind'.
    """
    permission_classes = [IsIndustrializacionUser]

    @extend_schema(
        summary="Solicitar edición de RFQ (En_Com → En_Ind)",
        description="""
            Crea una solicitud para que Comercialización regrese el RFQ a En_Ind.
            El RFQ debe estar en En_Com y no puede haber una solicitud Pendiente activa.
            Requiere autenticación.

            El cuerpo varía según `tipo`:
            - `tipo=mold` → `{ "rfq_mold": <id>, "reason": "..." }`.
            - `tipo=trimming` → `{ "rfq_trimming": <id>, "reason": "..." }`.
        """,
        parameters=[_TIPO_PARAM],
        request=MoldEditRequestCreateSerializer,
        responses={
            201: inline_serializer(
                name='SolicitarEdicionResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='SolicitarEdicionBadRequest',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def post(self, request):
        tipo = _get_tipo(request)
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            serializer = MoldEditRequestCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(requested_by=request.user)
            if settings.NOTIFICATIONS_ENABLED:
                notif_tasks.notificar_modificacion_rfq.delay(
                    instance.rfq_mold.id, 'mold', request.user.id, [ROL_COMERCIALIZACION]
                )
        else:
            serializer = TrimmingEditRequestCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(requested_by=request.user)
            if settings.NOTIFICATIONS_ENABLED:
                notif_tasks.notificar_modificacion_rfq.delay(
                    instance.rfq_trimming.id, 'trimming', request.user.id, [ROL_COMERCIALIZACION]
                )

        return Response(
            {'detail': 'Solicitud de edición enviada correctamente.'},
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. LISTADO UNIFICADO DE RFQs PARA INDUSTRIALIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────

class RFQListIndustrializacionView(APIView):
    """
    GET /api_industrializacion/v1/rfqs/
    Lista todos los RFQs (mold y trimming) con la siguiente regla de visibilidad:
      - Borradores (En_Ind): solo los creados por el usuario autenticado.
      - En_Com, En_Pro, complete: todos los usuarios del área.
    Requiere role='Ind'.
    """
    permission_classes = [IsIndustrializacionUser]

    @extend_schema(
        summary="Listado de RFQs (Industrialización)",
        description="""
            Devuelve todos los RFQs activos de tipo Mold y Trimming.

            Regla de visibilidad:
            - **En_Ind (borradores):** solo los del usuario autenticado.
            - **En_Com, En_Pro, complete:** todos los usuarios.

            Requiere autenticación.
        """,
        responses={
            200: inline_serializer(
                name='RFQListIndustrializacionResponse',
                fields={
                    'mold':     RFQMoldListSerializer(many=True),
                    'trimming': RFQTrimmingListSerializer(many=True),
                }
            )
        },
    )
    def get(self, request):
        user = request.user

        from django.db.models import Q
        molds = RFQ_Mold.objects.filter(logical_delete=False).filter(
            Q(status=RFQ_Mold.Status.INDUSTRIALIZACION, created_by=user) |
            ~Q(status=RFQ_Mold.Status.INDUSTRIALIZACION)
        ).select_related('created_by').order_by('-created_date')

        trimmings = RFQ_Trimming.objects.filter(logical_delete=False).filter(
            Q(status=RFQ_Trimming.Status.INDUSTRIALIZACION, created_by=user) |
            ~Q(status=RFQ_Trimming.Status.INDUSTRIALIZACION)
        ).select_related('created_by').order_by('-created_date')

        return Response({
            'mold':     RFQMoldListSerializer(molds, many=True).data,
            'trimming': RFQTrimmingListSerializer(trimmings, many=True).data,
        })
