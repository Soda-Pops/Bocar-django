from rest_framework import serializers
from django.utils import timezone
from .models import RFQ_Trimming, RFQ_Trimming_File, RFQ_Trimming_EditRequest


# ─────────────────────────────────────────────────────────────────────────────
# AUXILIAR: Representa cada archivo adjunto en las respuestas
# ─────────────────────────────────────────────────────────────────────────────
class RFQTrimmingFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQ_Trimming_File
        fields = ['id', 'archivo', 'uploaded_at']


# ─────────────────────────────────────────────────────────────────────────────
# 1. SERIALIZER DE CREACIÓN (POST)
#    - Acepta todos los campos editables del modelo
#    - created_by y created_date son read_only (se asignan automáticamente)
#    - archivos es un campo extra para recibir los ficheros
# ─────────────────────────────────────────────────────────────────────────────
class RFQTrimmingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RFQ_Trimming
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inyectamos 'archivos' manualmente porque no existe en el modelo
        # __all__ solo carga campos del modelo, los extras se agregan aquí
        self.fields['archivos'] = serializers.ListField(
            child=serializers.FileField(),
            write_only=True,
            required=False
        )

    def create(self, validated_data):
        # Extraemos archivos antes del INSERT — si no mandaron, lista vacía
        archivos = validated_data.pop('archivos', [])

        rfq_trimming = RFQ_Trimming.objects.create(**validated_data)

        # Creamos un RFQ_Trimming_File por cada archivo recibido
        for archivo in archivos:
            RFQ_Trimming_File.objects.create(rfq_trimming=rfq_trimming, archivo=archivo)

        return rfq_trimming


# ─────────────────────────────────────────────────────────────────────────────
# 2. SERIALIZER DE DETALLE (GET por ID)
#    - Todos los campos + nombre del usuario + archivos adjuntos
# ─────────────────────────────────────────────────────────────────────────────
class RFQTrimmingDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = RFQ_Trimming
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by_name'] = serializers.ReadOnlyField(source='created_by.username')
        self.fields['archivos']        = RFQTrimmingFileSerializer(many=True, read_only=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. SERIALIZER DE LISTA (GET todos)
#    - Solo campos de resumen para que la respuesta sea ligera
# ─────────────────────────────────────────────────────────────────────────────
class RFQTrimmingListSerializer(serializers.ModelSerializer):

    created_by_name = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = RFQ_Trimming
        fields = [
            'id',
            'status',
            'created_by',
            'created_by_name',
            'created_date',
            'due_date',
            'complete',
            'logical_delete',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# 4. SOLICITUD DE EDICIÓN — CREAR
#    Cualquier usuario autenticado puede solicitar regresar a En_Ind
# ─────────────────────────────────────────────────────────────────────────────
class TrimmingEditRequestCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RFQ_Trimming_EditRequest
        fields = ['id', 'rfq_trimming', 'reason']
        # requested_by, status, reviewed_by, reviewed_at se asignan automáticamente

    def validate_rfq_trimming(self, rfq_trimming):
        # Solo se puede solicitar edición si el status es En_Com
        if rfq_trimming.status != RFQ_Trimming.Status.COMERCIALIZACION:
            raise serializers.ValidationError(
                "Solo se puede solicitar edición cuando el status es 'En Comercialización'."
            )
        # No puede haber ya una solicitud pendiente para el mismo registro
        if RFQ_Trimming_EditRequest.objects.filter(rfq_trimming=rfq_trimming, status='Pendiente').exists():
            raise serializers.ValidationError(
                "Ya existe una solicitud pendiente para este RFQ Trimming."
            )
        return rfq_trimming


# ─────────────────────────────────────────────────────────────────────────────
# 5. SOLICITUD DE EDICIÓN — LISTA
#    Solo admin de Comercialización puede ver las pendientes
# ─────────────────────────────────────────────────────────────────────────────
class TrimmingEditRequestListSerializer(serializers.ModelSerializer):

    requested_by_name  = serializers.ReadOnlyField(source='requested_by.username')
    rfq_trimming_status = serializers.ReadOnlyField(source='rfq_trimming.status')

    class Meta:
        model = RFQ_Trimming_EditRequest
        fields = [
            'id',
            'rfq_trimming',
            'rfq_trimming_status',
            'requested_by',
            'requested_by_name',
            'requested_at',
            'status',
            'reason',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# 6. SOLICITUD DE EDICIÓN — APROBAR
#    Solo admin de Comercialización puede aprobar
#    Cambia la solicitud a Aprobada y el RFQ a En_Ind
# ─────────────────────────────────────────────────────────────────────────────
class TrimmingEditRequestApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = RFQ_Trimming_EditRequest
        fields = ['id', 'status']

    def validate(self, data):
        # Solo puede aprobarse si aún está Pendiente
        if self.instance.status != 'Pendiente':
            raise serializers.ValidationError("Esta solicitud ya fue resuelta.")

        # No se puede aprobar si el RFQ ya está en En_Pro
        if self.instance.rfq_trimming.status == RFQ_Trimming.Status.PROVEEDOR:
            raise serializers.ValidationError(
                "No se puede aprobar: el RFQ Trimming está en status 'En Proveedor'."
            )
        return data

    def update(self, instance, validated_data):
        # Marcamos la solicitud como aprobada y registramos quién y cuándo
        instance.status      = RFQ_Trimming_EditRequest.EditStatus.APROBADA
        instance.reviewed_by = self.context['request'].user
        instance.reviewed_at = timezone.now()
        instance.save()

        # Cambiamos el RFQ de En_Com a En_Ind
        instance.rfq_trimming.status = RFQ_Trimming.Status.INDUSTRIALIZACION
        instance.rfq_trimming.save()

        return instance