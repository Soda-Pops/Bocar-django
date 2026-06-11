from rest_framework import serializers as drf_serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, inline_serializer

from .permissions import IsChatbotAllowed
from .processor import process_query
from .serializers import ChatbotQuerySerializer


class ChatbotQueryView(APIView):
    """
    POST /api_chatbot/v1/query/
    Recibe una pregunta en lenguaje natural y devuelve una respuesta
    basada en los datos accesibles según el rol del usuario autenticado.
    """

    permission_classes = [IsAuthenticated, IsChatbotAllowed]

    @extend_schema(
        tags=['Chatbot'],
        summary='Consulta al chatbot',
        description=(
            'Procesa una pregunta en lenguaje natural y consulta la base de datos '
            'según el rol del usuario. Incluye historial de conversación opcional.\n\n'
            'Roles y acceso:\n'
            '- **Ind**: sus propios RFQs e historial\n'
            '- **Com**: todos los RFQs, asignaciones y proveedores\n'
            '- **Pro**: sus propias asignaciones\n'
            '- **SinRol**: acceso denegado (403)'
        ),
        request=ChatbotQuerySerializer,
        responses={
            200: inline_serializer(
                name='ChatbotResponse',
                fields={
                    'answer':  drf_serializers.CharField(),
                    'sources': drf_serializers.ListField(child=drf_serializers.CharField()),
                },
            ),
            403: inline_serializer(
                name='ChatbotDenied',
                fields={
                    'answer':        drf_serializers.CharField(),
                    'access_denied': drf_serializers.BooleanField(),
                },
            ),
        },
    )
    def post(self, request):
        serializer = ChatbotQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pregunta  = serializer.validated_data['pregunta']
        historial = serializer.validated_data.get('historial', [])

        result = process_query(request.user, pregunta, historial)
        return Response(result, status=status.HTTP_200_OK)
