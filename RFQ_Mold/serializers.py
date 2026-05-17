from rest_framework import serializers
from .models import RFQ_Mold

# Serializador Completo (Para detalle y creación)
class RFQMoldSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = RFQ_Mold
        fields = ['id', 'status', 'created_by', 'created_by_name']
        extra_kwargs = {'created_by': {'required': False}}

# Serializador Limitado (Solo para el listado)
class RFQMoldListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQ_Mold
        fields = ['id', 'status', 'created_by', 'created_date', 'due_date',] # <-- Aquí pones SOLO lo que quieres que salga en el GET general

#

# obtener todos los campos de un registro especifico por el id
#
# obtener todos algunos campos de todos los resgistros
#
# 
#
#
#
#
#
#