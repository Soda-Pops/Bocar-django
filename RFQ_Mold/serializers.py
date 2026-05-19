from rest_framework import serializers
from .models import RFQ_Mold, RFQ_Mold_File


# ─────────────────────────────────────────────────────────────────────────────
# AUXILIAR: Representa cada archivo adjunto en las respuestas
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQ_Mold_File
        fields = ['id', 'archivo', 'uploaded_at']


# ─────────────────────────────────────────────────────────────────────────────
# 1. SERIALIZER DE CREACIÓN (POST)
#    - Acepta todos los campos editables del modelo
#    - created_by y created_date son read_only (se asignan automáticamente)
#    - archivos es un campo extra fuera del modelo para recibir los ficheros
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldCreateSerializer(serializers.ModelSerializer):

    # Campo extra que NO existe en el modelo
    # ListField + FileField permite recibir múltiples archivos bajo el mismo key 'archivos'
    # required=False → el registro puede crearse sin archivos
    archivos = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = RFQ_Mold
        fields = '__all__'  # Incluye todos los campos del modelo + 'archivos' se agrega en __init__

        # Campos que el cliente NO puede enviar — se asignan solos en la vista o en el modelo
        read_only_fields = ['created_by', 'created_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregamos el campo 'archivos' manualmente después de que __all__ cargó los campos del modelo
        # Esto es necesario porque __all__ solo carga campos que existen en el modelo
        self.fields['archivos'] = serializers.ListField(
            child=serializers.FileField(),
            write_only=True,
            required=False
        )

    def create(self, validated_data):
        # Extraemos los archivos ANTES de crear el registro
        # Si no mandaron archivos, pop retorna lista vacía por defecto
        archivos = validated_data.pop('archivos', [])

        # Creamos el registro — en este punto validated_data ya no tiene 'archivos'
        rfq_mold = RFQ_Mold.objects.create(**validated_data)

        # Por cada archivo recibido creamos un RFQ_Mold_File enlazado al registro
        for archivo in archivos:
            RFQ_Mold_File.objects.create(rfq_mold=rfq_mold, archivo=archivo)

        return rfq_mold


# ─────────────────────────────────────────────────────────────────────────────
# 2. SERIALIZER DE DETALLE (GET por ID)
#    - Devuelve absolutamente todos los campos
#    - Incluye el nombre del usuario y los archivos adjuntos
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldDetailSerializer(serializers.ModelSerializer):

    # source='created_by.username' navega el FK para traer el nombre del usuario
    created_by_name = serializers.ReadOnlyField(source='created_by.username')

    # related_name='archivos' definido en el FK de RFQ_Mold_File
    # many=True → lista de archivos, read_only=True → solo lectura
    archivos = RFQMoldFileSerializer(many=True, read_only=True)

    class Meta:
        model = RFQ_Mold
        fields = '__all__'  # Todos los campos del modelo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inyectamos los campos extra que no son del modelo
        self.fields['created_by_name'] = serializers.ReadOnlyField(source='created_by.username')
        self.fields['archivos'] = RFQMoldFileSerializer(many=True, read_only=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. SERIALIZER DE LISTA (GET todos)
#    - Solo los campos esenciales para que la respuesta sea ligera
#    - No incluye archivos ni todos los campos del formulario
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldListSerializer(serializers.ModelSerializer):

    created_by_name = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = RFQ_Mold
        # Solo los campos de resumen — el resto se consulta con el endpoint de detalle
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
