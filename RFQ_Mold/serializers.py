from rest_framework import serializers
from django.utils import timezone
from .models import RFQ_Mold, RFQ_Mold_File, RFQ_Mold_EditRequest


# ─────────────────────────────────────────────────────────────────────────────
# AUXILIAR: Representa cada archivo adjunto en las respuestas
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldFileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RFQ_Mold_File
        fields = ['id', 'archivo', 'uploaded_at']


# ─────────────────────────────────────────────────────────────────────────────
# 1. SERIALIZER DE CREACIÓN (POST)
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model            = RFQ_Mold
        fields           = '__all__'
        read_only_fields = ['created_by', 'created_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivos'] = serializers.ListField(
            child=serializers.FileField(),
            write_only=True,
            required=False
        )

    def validate_status(self, value):
        # En_Pro está bloqueado en creación — el status Proveedor
        # solo se asigna mediante el flujo de aprobación, no directamente
        if value == RFQ_Mold.Status.PROVEEDOR:
            raise serializers.ValidationError(
                "No se puede crear un RFQ directamente en status 'En Proveedor'."
            )
        return value

    def create(self, validated_data):
        archivos = validated_data.pop('archivos', [])
        rfq_mold = RFQ_Mold.objects.create(**validated_data)

        for archivo in archivos:
            RFQ_Mold_File.objects.create(rfq_mold=rfq_mold, archivo=archivo)

        return rfq_mold


# ─────────────────────────────────────────────────────────────────────────────
# 2. SERIALIZER DE DETALLE (GET por ID)
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model  = RFQ_Mold
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos extra que no existen en el modelo pero queremos mostrar
        self.fields['created_by_name'] = serializers.ReadOnlyField(source='created_by.username')
        self.fields['archivos']        = RFQMoldFileSerializer(many=True, read_only=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. SERIALIZER DE LISTA (GET todos)
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldListSerializer(serializers.ModelSerializer):

    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    rfq_type        = serializers.SerializerMethodField()

    def get_rfq_type(self, obj):
        return 'Mold'   # Valor fijo — siempre será Mold en este serializer

    class Meta:
        model  = RFQ_Mold
        fields = [
            'id', 'status',
            'created_by', 'created_by_name',
            'created_date', 'due_date',
            'complete', 'logical_delete',
            'rfq_type',   # <-- campo nuevo
        ]

# ─────────────────────────────────────────────────────────────────────────────
# 4. SOLICITUD DE EDICIÓN — CREAR
#    Cualquier usuario autenticado puede solicitar regresar a En_Ind
# ─────────────────────────────────────────────────────────────────────────────
class MoldEditRequestCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = RFQ_Mold_EditRequest
        fields = ['id', 'rfq_mold', 'reason']

    def validate_rfq_mold(self, rfq_mold):
        # Solo se puede solicitar si el RFQ está en En_Com
        if rfq_mold.status != RFQ_Mold.Status.COMERCIALIZACION:
            raise serializers.ValidationError(
                "Solo se puede solicitar edición cuando el status es 'En Comercialización'."
            )
        # No puede haber ya una solicitud pendiente para el mismo RFQ
        if RFQ_Mold_EditRequest.objects.filter(rfq_mold=rfq_mold, status='Pendiente').exists():
            raise serializers.ValidationError(
                "Ya existe una solicitud pendiente para este RFQ Mold."
            )
        return rfq_mold


# ─────────────────────────────────────────────────────────────────────────────
# 5. SOLICITUD DE EDICIÓN — LISTA
#    Solo admin de Comercialización puede ver las pendientes
# ─────────────────────────────────────────────────────────────────────────────
class MoldEditRequestListSerializer(serializers.ModelSerializer):

    requested_by_name = serializers.ReadOnlyField(source='requested_by.username')
    rfq_mold_status   = serializers.ReadOnlyField(source='rfq_mold.status')

    class Meta:
        model  = RFQ_Mold_EditRequest
        fields = [
            'id', 'rfq_mold', 'rfq_mold_status',
            'requested_by', 'requested_by_name',
            'requested_at', 'status', 'reason',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# 6. SOLICITUD DE EDICIÓN — APROBAR
#    Cambia la solicitud a Aprobada y el RFQ a En_Ind
# ─────────────────────────────────────────────────────────────────────────────
class MoldEditRequestApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model  = RFQ_Mold_EditRequest
        fields = ['id', 'status']

    def validate(self, data):
        # Solo puede aprobarse si aún está Pendiente
        if self.instance.status != 'Pendiente':
            raise serializers.ValidationError("Esta solicitud ya fue resuelta.")
        # No se puede aprobar si el RFQ ya está en En_Pro
        if self.instance.rfq_mold.status == RFQ_Mold.Status.PROVEEDOR:
            raise serializers.ValidationError(
                "No se puede aprobar: el RFQ Mold está en status 'En Proveedor'."
            )
        return data

    def update(self, instance, validated_data):
        # Marcamos la solicitud como aprobada
        instance.status      = RFQ_Mold_EditRequest.EditStatus.APROBADA
        instance.reviewed_by = self.context['request'].user
        instance.reviewed_at = timezone.now()
        instance.save()

        # Cambiamos el RFQ de En_Com a En_Ind
        instance.rfq_mold.status = RFQ_Mold.Status.INDUSTRIALIZACION
        instance.rfq_mold.save()

        return instance