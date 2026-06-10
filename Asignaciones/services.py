from datetime import date

from django.db import transaction

from .models import Asignacion_Proveedor_Mold, Asignacion_Proveedor_Trimming


def close_if_expired(asignacion):
    if (
        not asignacion.is_answered
        and not asignacion.is_closed
        and asignacion.due_date < date.today()
    ):
        asignacion.is_closed = True
        asignacion.save(update_fields=['is_closed'])

    return asignacion


def validate_assignment_can_receive_quote(asignacion):
    close_if_expired(asignacion)

    if asignacion.is_closed:
        return False, 'La asignación está cerrada y ya no recibe cotizaciones.'

    if asignacion.due_date < date.today():
        return False, 'El plazo de esta asignación ha vencido. Solicita una extensión de tiempo.'

    if asignacion.is_answered:
        return False, 'La asignación ya fue respondida.'

    return True, None


def mark_assignment_answered_and_closed(asignacion):
    asignacion.is_answered = True
    asignacion.is_closed = True
    asignacion.save(update_fields=['is_answered', 'is_closed'])
    return asignacion


def close_rfq_if_all_assignments_answered(rfq):
    active_assignments = rfq.asignaciones.filter(logical_delete=False)

    if not active_assignments.exists():
        return False

    if active_assignments.filter(is_answered=False).exists():
        return False

    # Solo cierra asignaciones individuales; el RFQ se cierra manualmente
    active_assignments.update(is_closed=True)
    return True


def reopen_assignment_for_extension(asignacion, new_due_date):
    asignacion.due_date = new_due_date
    asignacion.is_closed = False
    asignacion.save(update_fields=['due_date', 'is_closed'])
    return asignacion


@transaction.atomic
def close_expired_assignments():
    today = date.today()
    mold_count = Asignacion_Proveedor_Mold.objects.filter(
        due_date__lt=today,
        is_answered=False,
        is_closed=False,
        logical_delete=False,
    ).update(is_closed=True)

    trimming_count = Asignacion_Proveedor_Trimming.objects.filter(
        due_date__lt=today,
        is_answered=False,
        is_closed=False,
        logical_delete=False,
    ).update(is_closed=True)

    return {
        'mold_closed': mold_count,
        'trimming_closed': trimming_count,
        'total_closed': mold_count + trimming_count,
    }
