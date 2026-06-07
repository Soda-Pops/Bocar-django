from rest_framework import serializers


class MensajeHistorialSerializer(serializers.Serializer):
    role    = serializers.ChoiceField(choices=['user', 'assistant'])
    content = serializers.CharField()


class ChatbotQuerySerializer(serializers.Serializer):
    pregunta  = serializers.CharField(max_length=1000)
    historial = MensajeHistorialSerializer(many=True, required=False, default=list)
