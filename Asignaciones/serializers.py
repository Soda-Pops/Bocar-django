from datetime import date
from rest_framework import serializers
from .models import (
    Asignacion_Proveedor_Mold,
    Asignacion_Proveedor_Trimming,
    SolicitudExtensionMold,
    SolicitudExtensionTrimming,
    ExtensionStatus,
)
from Prov_RFQ_Mold.models import Cost_Breakdown_Mold, Set_of_Cavities_Mold
from Prov_RFQ_Trimming.models import Cost_Breakdown_Trimming


class AsignacionMoldProveedorSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para asignaciones de tipo Mold.
    Incluye el campo PT del RFQ Mold como nombre del RFQ y si está en tiempo.
    """
    rfq_nombre = serializers.ReadOnlyField(source='id_RFQ_Mold.PT')
    en_tiempo  = serializers.SerializerMethodField()

    def get_en_tiempo(self, obj) -> bool:
        return obj.due_date >= date.today()

    class Meta:
        model  = Asignacion_Proveedor_Mold
        fields = [
            'id',
            'rfq_nombre',
            'fecha_de_asignacion',
            'due_date',
            'en_tiempo',
            'is_answered',
            'is_closed',
        ]


class AsignacionTrimmingProveedorSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para asignaciones de tipo Trimming.
    Incluye el campo part_name del RFQ Trimming como nombre del RFQ y si está en tiempo.
    """
    rfq_nombre = serializers.ReadOnlyField(source='id_RFQ_Trimming.part_name')
    en_tiempo  = serializers.SerializerMethodField()

    def get_en_tiempo(self, obj) -> bool:
        return obj.due_date >= date.today()

    class Meta:
        model  = Asignacion_Proveedor_Trimming
        fields = [
            'id',
            'rfq_nombre',
            'fecha_de_asignacion',
            'due_date',
            'en_tiempo',
            'is_answered',
            'is_closed',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# RESPUESTA DEL PROVEEDOR — MOLD
# ─────────────────────────────────────────────────────────────────────────────

class SetOfCavitiesMoldSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Set_of_Cavities_Mold
        exclude = ['id', 'id_cost_breakdown']


class CostBreakdownMoldCreateSerializer(serializers.ModelSerializer):
    # El set_of_cavities es opcional — si el proveedor lo incluye se crea junto
    set_of_cavities = SetOfCavitiesMoldSerializer(required=False, allow_null=True)

    class Meta:
        model   = Cost_Breakdown_Mold
        exclude = ['id', 'id_asignacion', 'last_edited_by', 'last_change']

    def create(self, validated_data):
        soc_data = validated_data.pop('set_of_cavities', None)
        breakdown = Cost_Breakdown_Mold.objects.create(**validated_data)
        if soc_data:
            Set_of_Cavities_Mold.objects.create(id_cost_breakdown=breakdown, **soc_data)
        return breakdown


# ─────────────────────────────────────────────────────────────────────────────
# RESPUESTA DEL PROVEEDOR — TRIMMING
# ─────────────────────────────────────────────────────────────────────────────

class CostBreakdownTrimmingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Cost_Breakdown_Trimming
        exclude = ['id', 'id_asignacion', 'last_edited_by', 'last_change']


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
            instance.id_asignacion.due_date = instance.nueva_fecha
            instance.id_asignacion.save(update_fields=['due_date'])

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
            instance.id_asignacion.due_date = instance.nueva_fecha
            instance.id_asignacion.save(update_fields=['due_date'])

        return instance