from rest_framework import serializers

from .models import RFQHistorial


class RFQHistorialSerializer(serializers.ModelSerializer):
    evento_display = serializers.CharField(source='get_evento_display', read_only=True)
    actor_username = serializers.ReadOnlyField(source='actor.username')

    class Meta:
        model  = RFQHistorial
        fields = [
            'id',
            'rfq_tipo',
            'rfq_id',
            'evento',
            'evento_display',
            'actor',
            'actor_username',
            'timestamp',
            'status_anterior',
            'status_nuevo',
            'cambios',
            'detalle',
        ]
