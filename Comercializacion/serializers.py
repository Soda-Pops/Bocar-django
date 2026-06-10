from datetime import date, datetime, timezone
from rest_framework import serializers
from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming
from Proveedores.models import Proveedor


def _calcular_deadline(due_date):
    """
    Recibe un date y devuelve un string dinámico:
    - Si ya venció          → "Vencido"
    - Si faltan < 24 hrs    → "Xh Ym"
    - Si faltan >= 24 hrs   → "X días"
    """
    hoy = date.today()
    delta_dias = (due_date - hoy).days

    if delta_dias < 0:
        return "Vencido"

    if delta_dias == 0:
        # Calculamos horas restantes hasta medianoche del due_date
        ahora = datetime.now(tz=timezone.utc)
        fin   = datetime(due_date.year, due_date.month, due_date.day,
                         23, 59, 59, tzinfo=timezone.utc)
        segundos = max(int((fin - ahora).total_seconds()), 0)
        horas    = segundos // 3600
        minutos  = (segundos % 3600) // 60
        return f"{horas}h {minutos}m"

    return f"{delta_dias} días"


def _calcular_progreso(asignaciones_qs):
    """
    Recibe el queryset de asignaciones de un RFQ y devuelve el string de progreso.
    """
    total = asignaciones_qs.filter(logical_delete=False).count()

    if total == 0:
        return "Sin proveedores asignados"

    respondidos = asignaciones_qs.filter(logical_delete=False, is_answered=True).count()

    if respondidos == total:
        return "Completo"

    return f"{respondidos}/{total} contestados"


# ─────────────────────────────────────────────────────────────────────────────
# MOLD
# ─────────────────────────────────────────────────────────────────────────────

class RFQMoldComercializacionSerializer(serializers.ModelSerializer):

    nombre_pieza      = serializers.ReadOnlyField(source='PT')
    tipo              = serializers.SerializerMethodField()
    deadline          = serializers.SerializerMethodField()
    fecha_creacion    = serializers.SerializerMethodField()
    creado_por        = serializers.ReadOnlyField(source='created_by.username')
    progreso_proveedores = serializers.SerializerMethodField()

    def get_tipo(self, obj) -> str:
        return 'Mold'

    def get_deadline(self, obj) -> str:
        return _calcular_deadline(obj.due_date)

    def get_fecha_creacion(self, obj) -> str:
        return obj.created_date.strftime('%d-%m-%y')

    def get_progreso_proveedores(self, obj) -> str:
        return _calcular_progreso(obj.asignaciones)

    class Meta:
        model  = RFQ_Mold
        fields = [
            'id',
            'nombre_pieza',
            'status',
            'complete',
            'tipo',
            'deadline',
            'fecha_creacion',
            'creado_por',
            'progreso_proveedores',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# TRIMMING
# ─────────────────────────────────────────────────────────────────────────────

class RFQTrimmingComercializacionSerializer(serializers.ModelSerializer):

    nombre_pieza      = serializers.ReadOnlyField(source='part_name')
    tipo              = serializers.SerializerMethodField()
    deadline          = serializers.SerializerMethodField()
    fecha_creacion    = serializers.SerializerMethodField()
    creado_por        = serializers.ReadOnlyField(source='created_by.username')
    progreso_proveedores = serializers.SerializerMethodField()

    def get_tipo(self, obj) -> str:
        return 'Trimming'

    def get_deadline(self, obj) -> str:
        return _calcular_deadline(obj.due_date)

    def get_fecha_creacion(self, obj) -> str:
        return obj.created_date.strftime('%d-%m-%y')

    def get_progreso_proveedores(self, obj) -> str:
        return _calcular_progreso(obj.asignaciones)

    class Meta:
        model  = RFQ_Trimming
        fields = [
            'id',
            'nombre_pieza',
            'status',
            'complete',
            'tipo',
            'deadline',
            'fecha_creacion',
            'creado_por',
            'progreso_proveedores',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# CREAR ASIGNACIONES
# ─────────────────────────────────────────────────────────────────────────────

class CerrarRFQSerializer(serializers.Serializer):
    closure_reason = serializers.CharField(max_length=1000)


class CrearAsignacionesSerializer(serializers.Serializer):
    id_rfq      = serializers.IntegerField()
    due_date    = serializers.DateField()
    proveedores = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
    )

    def validate_due_date(self, value):
        if value <= date.today():
            raise serializers.ValidationError(
                'El due_date debe ser una fecha futura.'
            )
        return value
