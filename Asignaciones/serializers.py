from datetime import date, datetime, timezone
from rest_framework import serializers


def _calcular_deadline(due_date) -> str:
    """Tiempo restante dinámico igual que en Comercialización."""
    delta = (due_date - date.today()).days
    if delta < 0:
        return 'Vencido'
    if delta == 0:
        ahora    = datetime.now(tz=timezone.utc)
        fin      = datetime(due_date.year, due_date.month, due_date.day,
                            23, 59, 59, tzinfo=timezone.utc)
        segundos = max(int((fin - ahora).total_seconds()), 0)
        return f"{segundos // 3600}h {(segundos % 3600) // 60}m"
    return f"{delta} días"
from .models import (
    Asignacion_Proveedor_Mold,
    Asignacion_Proveedor_Trimming,
    SolicitudExtensionMold,
    SolicitudExtensionTrimming,
    ExtensionStatus,
)
from Prov_RFQ_Mold.models import (
    Cost_Breakdown_Mold,
    Cost_Breakdown_Mold_File,
    Set_of_Cavities_Mold,
)
from Prov_RFQ_Trimming.models import Cost_Breakdown_Trimming, Cost_Breakdown_Trimming_File
from .services import reopen_assignment_for_extension


class AsignacionMoldProveedorSerializer(serializers.ModelSerializer):
    rfq_id         = serializers.ReadOnlyField(source='id_RFQ_Mold_id')
    rfq_nombre     = serializers.ReadOnlyField(source='id_RFQ_Mold.PT')
    DESC           = serializers.ReadOnlyField(source='id_RFQ_Mold.DESC')
    en_tiempo      = serializers.SerializerMethodField()
    deadline       = serializers.SerializerMethodField()
    tiene_borrador = serializers.SerializerMethodField()

    def get_en_tiempo(self, obj) -> bool:
        return obj.due_date >= date.today()

    def get_deadline(self, obj) -> str:
        return _calcular_deadline(obj.due_date)

    def get_tiene_borrador(self, obj) -> bool:
        return (
            hasattr(obj, 'cost_breakdown') and
            obj.cost_breakdown.status == 'draft'
        )

    class Meta:
        model  = Asignacion_Proveedor_Mold
        fields = [
            'id',
            'rfq_id',
            'rfq_nombre',
            'DESC',
            'fecha_de_asignacion',
            'due_date',
            'deadline',
            'en_tiempo',
            'tiene_borrador',
            'is_answered',
            'is_closed',
        ]


class AsignacionTrimmingProveedorSerializer(serializers.ModelSerializer):
    rfq_id         = serializers.ReadOnlyField(source='id_RFQ_Trimming_id')
    rfq_nombre     = serializers.ReadOnlyField(source='id_RFQ_Trimming.part_name')
    DESC           = serializers.ReadOnlyField(source='id_RFQ_Trimming.DESC')
    en_tiempo      = serializers.SerializerMethodField()
    deadline       = serializers.SerializerMethodField()
    tiene_borrador = serializers.SerializerMethodField()

    def get_en_tiempo(self, obj) -> bool:
        return obj.due_date >= date.today()

    def get_deadline(self, obj) -> str:
        return _calcular_deadline(obj.due_date)

    def get_tiene_borrador(self, obj) -> bool:
        return (
            hasattr(obj, 'cost_breakdown') and
            obj.cost_breakdown.status == 'draft'
        )

    class Meta:
        model  = Asignacion_Proveedor_Trimming
        fields = [
            'id',
            'rfq_id',
            'rfq_nombre',
            'DESC',
            'fecha_de_asignacion',
            'due_date',
            'deadline',
            'en_tiempo',
            'tiene_borrador',
            'is_answered',
            'is_closed',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# RESPUESTA DEL PROVEEDOR — MOLD
# ─────────────────────────────────────────────────────────────────────────────

class SetOfCavitiesMoldSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Set_of_Cavities_Mold
        exclude = ['id', 'id_cost_breakdown']


class CostBreakdownMoldFileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Cost_Breakdown_Mold_File
        fields = ['id', 'archivo', 'uploaded_at']


# Crear borrador (POST)
class CostBreakdownMoldCreateSerializer(serializers.ModelSerializer):
    set_of_cavities = SetOfCavitiesMoldSerializer(required=False, allow_null=True)

    class Meta:
        model   = Cost_Breakdown_Mold
        exclude = ['id', 'id_asignacion', 'last_edited_by', 'last_change', 'status']

    def create(self, validated_data):
        soc_data  = validated_data.pop('set_of_cavities', None)
        breakdown = Cost_Breakdown_Mold.objects.create(**validated_data)
        if soc_data:
            Set_of_Cavities_Mold.objects.create(id_cost_breakdown=breakdown, **soc_data)
        return breakdown


# Leer borrador/respuesta (GET)
class CostBreakdownMoldDetailSerializer(serializers.ModelSerializer):
    set_of_cavities = SetOfCavitiesMoldSerializer(read_only=True)
    archivos = CostBreakdownMoldFileSerializer(many=True, read_only=True)

    class Meta:
        model   = Cost_Breakdown_Mold
        exclude = ['id_asignacion', 'last_edited_by']


# Actualizar borrador (PATCH)
class CostBreakdownMoldUpdateSerializer(serializers.ModelSerializer):
    set_of_cavities = SetOfCavitiesMoldSerializer(required=False, allow_null=True)

    class Meta:
        model   = Cost_Breakdown_Mold
        exclude = ['id', 'id_asignacion', 'last_edited_by', 'last_change', 'status']

    def update(self, instance, validated_data):
        soc_data = validated_data.pop('set_of_cavities', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if soc_data is not None:
            if hasattr(instance, 'set_of_cavities'):
                soc = instance.set_of_cavities
                for attr, value in soc_data.items():
                    setattr(soc, attr, value)
                soc.save()
            else:
                Set_of_Cavities_Mold.objects.create(id_cost_breakdown=instance, **soc_data)

        return instance


# ─────────────────────────────────────────────────────────────────────────────
# RESPUESTA DEL PROVEEDOR — TRIMMING
# ─────────────────────────────────────────────────────────────────────────────

class CostBreakdownTrimmingFileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Cost_Breakdown_Trimming_File
        fields = ['id', 'archivo', 'uploaded_at']


# Crear borrador (POST)
class CostBreakdownTrimmingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Cost_Breakdown_Trimming
        exclude = ['id', 'id_asignacion', 'last_edited_by', 'last_change', 'status']


# Leer borrador/respuesta (GET)
class CostBreakdownTrimmingDetailSerializer(serializers.ModelSerializer):
    archivos = CostBreakdownTrimmingFileSerializer(many=True, read_only=True)

    class Meta:
        model   = Cost_Breakdown_Trimming
        exclude = ['id_asignacion', 'last_edited_by']


# Actualizar borrador (PATCH)
class CostBreakdownTrimmingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Cost_Breakdown_Trimming
        exclude = ['id', 'id_asignacion', 'last_edited_by', 'last_change', 'status']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ─────────────────────────────────────────────────────────────────────────────
# SOLICITUD DE EXTENSIÓN — LISTADO (comercialización)
# ─────────────────────────────────────────────────────────────────────────────

class SolicitudExtensionMoldListSerializer(serializers.ModelSerializer):
    rfq_id             = serializers.ReadOnlyField(source='id_asignacion.id_RFQ_Mold_id')
    proveedor_nombre   = serializers.ReadOnlyField(source='id_asignacion.id_Proveedor.company_name')
    rfq_nombre         = serializers.ReadOnlyField(source='id_asignacion.id_RFQ_Mold.PT')
    due_date_actual    = serializers.ReadOnlyField(source='id_asignacion.due_date')

    class Meta:
        model  = SolicitudExtensionMold
        fields = [
            'id', 'rfq_id', 'rfq_nombre', 'proveedor_nombre',
            'due_date_actual', 'nueva_fecha',
            'motivo', 'status', 'solicitada_at',
        ]


class SolicitudExtensionTrimmingListSerializer(serializers.ModelSerializer):
    rfq_id             = serializers.ReadOnlyField(source='id_asignacion.id_RFQ_Trimming_id')
    proveedor_nombre   = serializers.ReadOnlyField(source='id_asignacion.id_Proveedor.company_name')
    rfq_nombre         = serializers.ReadOnlyField(source='id_asignacion.id_RFQ_Trimming.part_name')
    due_date_actual    = serializers.ReadOnlyField(source='id_asignacion.due_date')

    class Meta:
        model  = SolicitudExtensionTrimming
        fields = [
            'id', 'rfq_id', 'rfq_nombre', 'proveedor_nombre',
            'due_date_actual', 'nueva_fecha',
            'motivo', 'status', 'solicitada_at',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# SOLICITUD DE EXTENSIÓN — CREAR (proveedor)
# ─────────────────────────────────────────────────────────────────────────────

class SolicitudExtensionMoldCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = SolicitudExtensionMold
        fields = ['id', 'motivo', 'nueva_fecha']

    def validate(self, data):
        asignacion = self.context['asignacion']

        # La nueva fecha debe ser posterior al due_date actual
        if data['nueva_fecha'] <= asignacion.due_date:
            raise serializers.ValidationError(
                {'nueva_fecha': 'La nueva fecha debe ser posterior a la fecha límite actual.'}
            )

        # No puede haber ya una solicitud Pendiente para esta asignación
        if SolicitudExtensionMold.objects.filter(
            id_asignacion=asignacion,
            status=ExtensionStatus.PENDIENTE,
        ).exists():
            raise serializers.ValidationError(
                'Ya existe una solicitud de extensión pendiente para esta asignación.'
            )
        return data


class SolicitudExtensionTrimmingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = SolicitudExtensionTrimming
        fields = ['id', 'motivo', 'nueva_fecha']

    def validate(self, data):
        asignacion = self.context['asignacion']

        if data['nueva_fecha'] <= asignacion.due_date:
            raise serializers.ValidationError(
                {'nueva_fecha': 'La nueva fecha debe ser posterior a la fecha límite actual.'}
            )

        if SolicitudExtensionTrimming.objects.filter(
            id_asignacion=asignacion,
            status=ExtensionStatus.PENDIENTE,
        ).exists():
            raise serializers.ValidationError(
                'Ya existe una solicitud de extensión pendiente para esta asignación.'
            )
        return data


# ─────────────────────────────────────────────────────────────────────────────
# SOLICITUD DE EXTENSIÓN — RESOLVER (comercialización)
# ─────────────────────────────────────────────────────────────────────────────

class SolicitudExtensionMoldResolverSerializer(serializers.ModelSerializer):

    class Meta:
        model  = SolicitudExtensionMold
        fields = ['id', 'status']

    def validate_status(self, value):
        if value not in (ExtensionStatus.APROBADA, ExtensionStatus.RECHAZADA):
            raise serializers.ValidationError(
                "El status debe ser 'Aprobada' o 'Rechazada'."
            )
        if self.instance.status != ExtensionStatus.PENDIENTE:
            raise serializers.ValidationError(
                'Esta solicitud ya fue resuelta.'
            )
        return value

    def update(self, instance, validated_data):
        from django.utils import timezone
        instance.status      = validated_data['status']
        instance.revisada_por = self.context['request'].user
        instance.revisada_at  = timezone.now()
        instance.save()

        # Si se aprueba, actualizamos el due_date de la asignación
        if instance.status == ExtensionStatus.APROBADA:
            reopen_assignment_for_extension(instance.id_asignacion, instance.nueva_fecha)

        from historial.models import RFQHistorial
        from historial.services import registrar_historial
        aprobada = instance.status == ExtensionStatus.APROBADA
        registrar_historial(
            rfq_tipo = RFQHistorial.Tipo.MOLD,
            rfq_id   = instance.id_asignacion.id_RFQ_Mold_id,
            evento   = (RFQHistorial.Evento.EXTENSION_APROBADA if aprobada
                        else RFQHistorial.Evento.EXTENSION_RECHAZADA),
            actor    = instance.revisada_por,
            detalle  = {'nueva_fecha': str(instance.nueva_fecha)},
        )

        return instance


class SolicitudExtensionTrimmingResolverSerializer(serializers.ModelSerializer):

    class Meta:
        model  = SolicitudExtensionTrimming
        fields = ['id', 'status']

    def validate_status(self, value):
        if value not in (ExtensionStatus.APROBADA, ExtensionStatus.RECHAZADA):
            raise serializers.ValidationError(
                "El status debe ser 'Aprobada' o 'Rechazada'."
            )
        if self.instance.status != ExtensionStatus.PENDIENTE:
            raise serializers.ValidationError(
                'Esta solicitud ya fue resuelta.'
            )
        return value

    def update(self, instance, validated_data):
        from django.utils import timezone
        instance.status       = validated_data['status']
        instance.revisada_por = self.context['request'].user
        instance.revisada_at  = timezone.now()
        instance.save()

        if instance.status == ExtensionStatus.APROBADA:
            reopen_assignment_for_extension(instance.id_asignacion, instance.nueva_fecha)

        from historial.models import RFQHistorial
        from historial.services import registrar_historial
        aprobada = instance.status == ExtensionStatus.APROBADA
        registrar_historial(
            rfq_tipo = RFQHistorial.Tipo.TRIMMING,
            rfq_id   = instance.id_asignacion.id_RFQ_Trimming_id,
            evento   = (RFQHistorial.Evento.EXTENSION_APROBADA if aprobada
                        else RFQHistorial.Evento.EXTENSION_RECHAZADA),
            actor    = instance.revisada_por,
            detalle  = {'nueva_fecha': str(instance.nueva_fecha)},
        )

        return instance
