from rest_framework import serializers
from .models import Asignacion_Proveedor_Mold, Asignacion_Proveedor_Trimming


class AsignacionMoldProveedorSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para asignaciones de tipo Mold.
    Incluye el campo PT del RFQ Mold como nombre del RFQ.
    """
    # Navega el FK id_RFQ_Mold para traer el campo PT
    rfq_nombre = serializers.ReadOnlyField(source='id_RFQ_Mold.PT')

    class Meta:
        model  = Asignacion_Proveedor_Mold
        fields = [
            'id',
            'rfq_nombre',           # PT de RFQ_Mold
            'fecha_de_asignacion',
            'due_date',
            'is_closed',
        ]


class AsignacionTrimmingProveedorSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para asignaciones de tipo Trimming.
    Incluye el campo part_name del RFQ Trimming como nombre del RFQ.
    """
    # Navega el FK id_RFQ_Trimming para traer el campo part_name
    rfq_nombre = serializers.ReadOnlyField(source='id_RFQ_Trimming.part_name')

    class Meta:
        model  = Asignacion_Proveedor_Trimming
        fields = [
            'id',
            'rfq_nombre',           # part_name de RFQ_Trimming
            'fecha_de_asignacion',
            'due_date',
            'is_closed',
        ]