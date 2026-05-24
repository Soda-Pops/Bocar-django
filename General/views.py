from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming


class RFQGlobalCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # ─── Parámetro opcional: filtrar En_Ind por usuario ───────────────────
        # Si no mandan user_id, usamos el usuario autenticado por defecto
        user_id = request.query_params.get('user_id', request.user.id)

        # ─── Base: solo registros NO borrados lógicamente ─────────────────────
        molds     = RFQ_Mold.objects.filter(logical_delete=False)
        trimmings = RFQ_Trimming.objects.filter(logical_delete=False)

        # ─── 1. Completados ───────────────────────────────────────────────────
        # Suma de RFQ Molds + RFQ Trimmings que tienen complete=True
        molds_completos     = molds.filter(complete=True).count()
        trimmings_completos = trimmings.filter(complete=True).count()
        total_completos     = molds_completos + trimmings_completos

        # ─── 2. En Comercialización ───────────────────────────────────────────
        # Suma de todos los RFQs con status=En_Com sin importar usuario
        molds_en_com     = molds.filter(status=RFQ_Mold.Status.COMERCIALIZACION).count()
        trimmings_en_com = trimmings.filter(status=RFQ_Trimming.Status.COMERCIALIZACION).count()
        total_en_com     = molds_en_com + trimmings_en_com

        # ─── 3. En Industrialización del usuario ─────────────────────────────
        # Solo los RFQs en En_Ind que pertenezcan al user_id recibido
        molds_en_ind     = molds.filter(status=RFQ_Mold.Status.INDUSTRIALIZACION, created_by=user_id).count()
        trimmings_en_ind = trimmings.filter(status=RFQ_Trimming.Status.INDUSTRIALIZACION, created_by=user_id).count()
        total_en_ind     = molds_en_ind + trimmings_en_ind

        return Response({
            # Completados (ambos tipos, cualquier usuario)
            'completados': {
                'molds':     molds_completos,
                'trimmings': trimmings_completos,
                'total':     total_completos,
            },
            # En Comercialización (ambos tipos, cualquier usuario)
            'en_comercializacion': {
                'molds':     molds_en_com,
                'trimmings': trimmings_en_com,
                'total':     total_en_com,
            },
            # En Industrialización filtrado por usuario
            'en_industrializacion_usuario': {
                'user_id':   user_id,
                'molds':     molds_en_ind,
                'trimmings': trimmings_en_ind,
                'total':     total_en_ind,
            },
        })