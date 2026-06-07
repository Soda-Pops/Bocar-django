from django.db.models import Count

from Asignaciones.models import Asignacion_Proveedor_Mold, Asignacion_Proveedor_Trimming
from historial.models import RFQHistorial
from Proveedores.models import Proveedor
from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming


def _parse_bool(value) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).lower() in ('true', '1', 'yes')


# ─────────────────────────────────────────────────────────────────────────────
# Ind — solo sus propios RFQs
# ─────────────────────────────────────────────────────────────────────────────

def contar_rfqs(user, tipo: str, status: str = None) -> dict:
    model = RFQ_Mold if tipo == 'mold' else RFQ_Trimming
    qs = model.objects.filter(created_by=user, logical_delete=False)
    if status:
        qs = qs.filter(status=status)
    return {'count': qs.count(), 'tipo': tipo, 'status': status or 'todos'}


def listar_rfqs(user, tipo: str, status: str = None) -> dict:
    model = RFQ_Mold if tipo == 'mold' else RFQ_Trimming
    qs = model.objects.filter(created_by=user, logical_delete=False)
    if status:
        qs = qs.filter(status=status)

    results = [
        {
            'id':           rfq.id,
            'descripcion':  rfq.DESC,
            'status':       rfq.status,
            'due_date':     str(rfq.due_date),
            'created_date': str(rfq.created_date.date()),
            'complete':     rfq.complete,
        }
        for rfq in qs[:20]
    ]
    return {'rfqs': results, 'total': qs.count(), 'tipo': tipo}


def historial_rfq(user, tipo: str, rfq_id: int) -> dict:
    # Ind solo puede ver el historial de sus propios RFQs
    if user.role == 'Ind':
        model = RFQ_Mold if tipo == 'mold' else RFQ_Trimming
        if not model.objects.filter(id=rfq_id, created_by=user, logical_delete=False).exists():
            raise PermissionError('No tienes acceso al historial de ese RFQ.')

    qs = RFQHistorial.objects.filter(rfq_tipo=tipo, rfq_id=rfq_id).order_by('-timestamp')[:20]
    results = [
        {
            'evento':          h.evento,
            'timestamp':       str(h.timestamp),
            'actor':           h.actor.username if h.actor else 'Sistema',
            'status_anterior': h.status_anterior,
            'status_nuevo':    h.status_nuevo,
            'detalle':         h.detalle,
        }
        for h in qs
    ]
    return {'historial': results, 'rfq_tipo': tipo, 'rfq_id': rfq_id}


# ─────────────────────────────────────────────────────────────────────────────
# Com — acceso global a todos los RFQs, asignaciones y proveedores
# ─────────────────────────────────────────────────────────────────────────────

def contar_rfqs_todos(tipo: str, status: str = None) -> dict:
    model = RFQ_Mold if tipo == 'mold' else RFQ_Trimming
    qs = model.objects.filter(logical_delete=False)
    if status:
        qs = qs.filter(status=status)
    return {'count': qs.count(), 'tipo': tipo, 'status': status or 'todos'}


def listar_rfqs_todos(tipo: str, status: str = None) -> dict:
    model = RFQ_Mold if tipo == 'mold' else RFQ_Trimming
    qs = model.objects.filter(logical_delete=False)
    if status:
        qs = qs.filter(status=status)

    results = [
        {
            'id':           rfq.id,
            'descripcion':  rfq.DESC,
            'status':       rfq.status,
            'due_date':     str(rfq.due_date),
            'created_date': str(rfq.created_date.date()),
            'complete':     rfq.complete,
            'created_by':   rfq.created_by.username if rfq.created_by else None,
        }
        for rfq in qs[:20]
    ]
    return {'rfqs': results, 'total': qs.count(), 'tipo': tipo}


def rfqs_por_status(tipo: str) -> dict:
    model = RFQ_Mold if tipo == 'mold' else RFQ_Trimming
    distribucion = list(
        model.objects.filter(logical_delete=False)
             .values('status')
             .annotate(total=Count('id'))
    )
    return {'distribucion': distribucion, 'tipo': tipo}


def listar_proveedores() -> dict:
    qs = Proveedor.objects.select_related('id_account').all()[:50]
    results = [
        {
            'id':           p.id,
            'company_name': p.company_name,
            'country':      str(p.country),
            'continent':    p.continent,
            'rating':       p.rating,
        }
        for p in qs
    ]
    return {'proveedores': results, 'total': Proveedor.objects.count()}


def listar_asignaciones(tipo: str, is_answered=None) -> dict:
    model      = Asignacion_Proveedor_Mold if tipo == 'mold' else Asignacion_Proveedor_Trimming
    rfq_field  = 'id_RFQ_Mold'             if tipo == 'mold' else 'id_RFQ_Trimming'
    qs = model.objects.filter(logical_delete=False)

    answered = _parse_bool(is_answered)
    if answered is not None:
        qs = qs.filter(is_answered=answered)

    results = [
        {
            'id':          a.id,
            'proveedor':   a.id_Proveedor.company_name,
            'rfq_id':      getattr(a, rfq_field).id,
            'due_date':    str(a.due_date),
            'is_answered': a.is_answered,
            'is_closed':   a.is_closed,
        }
        for a in qs[:20]
    ]
    return {'asignaciones': results, 'total': qs.count(), 'tipo': tipo}


# ─────────────────────────────────────────────────────────────────────────────
# Pro — solo sus propias asignaciones
# ─────────────────────────────────────────────────────────────────────────────

def mis_asignaciones(user, tipo: str, is_answered=None) -> dict:
    try:
        proveedor = user.proveedor
    except Exception:
        raise PermissionError('Tu cuenta no tiene un perfil de proveedor asociado.')

    model     = Asignacion_Proveedor_Mold if tipo == 'mold' else Asignacion_Proveedor_Trimming
    rfq_field = 'id_RFQ_Mold'             if tipo == 'mold' else 'id_RFQ_Trimming'
    qs = model.objects.filter(id_Proveedor=proveedor, logical_delete=False)

    answered = _parse_bool(is_answered)
    if answered is not None:
        qs = qs.filter(is_answered=answered)

    results = [
        {
            'id':          a.id,
            'rfq_id':      getattr(a, rfq_field).id,
            'due_date':    str(a.due_date),
            'is_answered': a.is_answered,
            'is_closed':   a.is_closed,
        }
        for a in qs[:20]
    ]
    return {'asignaciones': results, 'total': qs.count(), 'tipo': tipo}
