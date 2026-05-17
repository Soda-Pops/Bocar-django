from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import RFQ_Mold
from .serializers import RFQMoldSerializer, RFQMoldListSerializer

# 1. Endpoint para LISTAR y CREAR (POST / GET general)
class RFQMoldListCreateView(generics.ListCreateAPIView):
    queryset = RFQ_Mold.objects.all()
    permission_classes = [IsAuthenticated]

    # Usamos el serializador recortado para el GET general
    serializer_class = RFQMoldListSerializer 

    def perform_create(self, serializer):
        # Al hacer POST, Django REST Framework usará el serializador de la vista, 
        # pero aquí aseguramos que se guarde el usuario actual.
        serializer.save(created_by=self.request.user)

    # Tip pro: Si quieres usar el serializador completo SOLO para el POST, 
    # puedes sobrescribir este método:
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RFQMoldSerializer
        return RFQMoldListSerializer


# 2. Endpoint para ver el DETALLE de uno solo (GET específico)
# Al usar RetrieveAPIView, no existe ni PUT, ni PATCH, ni DELETE.
class RFQMoldDetailView(generics.RetrieveAPIView):
    queryset = RFQ_Mold.objects.all()
    permission_classes = [IsAuthenticated]
    # Usamos el serializador completo con toda la info del usuario
    serializer_class = RFQMoldSerializer