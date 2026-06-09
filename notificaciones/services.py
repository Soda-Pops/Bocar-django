import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from users.models import CustomUser

logger = logging.getLogger(__name__)

ROL_INDUSTRIALIZACION = CustomUser.Roles.INDUSTRIALIZACION  # 'Ind'
ROL_COMERCIALIZACION  = CustomUser.Roles.COMERCIALIZACION   # 'Com'
ROL_PROVEEDOR         = CustomUser.Roles.PROVEEDOR          # 'Pro'


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS INTERNOS
# ─────────────────────────────────────────────────────────────────────────────

def _emails_por_rol(rol):
    return list(CustomUser.objects.filter(role=rol).values_list('email', flat=True))


def _emails_asignados(rfq):
    return list(
        rfq.asignaciones.filter(logical_delete=False)
        .values_list('id_Proveedor__contact_email', flat=True)
    )


def _emails_admins():
    return list(CustomUser.objects.filter(is_admin=True).values_list('email', flat=True))


def _enviar(subject, template, context, bcc):
    if not bcc:
        logger.warning('_enviar: lista BCC vacía para "%s", correo no enviado.', subject)
        return
    html_body = render_to_string(template, context)
    msg = EmailMultiAlternatives(
        subject    = subject,
        body       = subject,
        from_email = settings.EMAIL_HOST_USER,
        to         = [settings.EMAIL_HOST_USER],
        bcc        = bcc,
    )
    msg.attach_alternative(html_body, 'text/html')
    try:
        msg.send(fail_silently=False)
    except Exception:
        logger.exception('Error enviando correo "%s"', subject)


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE NOTIFICACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def notificar_comercializacion(rfq):
    """RFQ avanza a En_Com — notifica al equipo de Comercialización (BCC)."""
    emails = _emails_por_rol(ROL_COMERCIALIZACION)
    if not emails:
        logger.warning('notificar_comercializacion: no hay usuarios con rol Comercialización.')
        return
    _enviar(
        subject  = f'[BOCAR] Nueva RFQ #{rfq.id} pendiente de gestión',
        template = 'notificaciones/rfq_a_compras.html',
        context  = {'rfq': rfq},
        bcc      = emails,
    )


def notificar_proveedores(rfq):
    """RFQ avanza a En_Pro — notifica solo a los proveedores asignados a este RFQ (BCC)."""
    emails = _emails_asignados(rfq)
    if not emails:
        logger.warning('notificar_proveedores: RFQ #%s no tiene asignaciones activas.', rfq.id)
        return
    _enviar(
        subject  = f'[BOCAR] Solicitud de Cotización — RFQ #{rfq.id}',
        template = 'notificaciones/rfq_a_proveedores.html',
        context  = {'rfq': rfq},
        bcc      = emails,
    )


def notificar_cotizacion_recibida(rfq, proveedor):
    """Proveedor sube cotización — notifica al equipo de Comercialización (BCC)."""
    emails = _emails_por_rol(ROL_COMERCIALIZACION)
    if not emails:
        logger.warning('notificar_cotizacion_recibida: no hay usuarios con rol Comercialización.')
        return
    _enviar(
        subject  = f'[BOCAR] Cotización recibida — RFQ #{rfq.id} — {proveedor.get_full_name()}',
        template = 'notificaciones/cotizacion_recibida.html',
        context  = {'rfq': rfq, 'proveedor': proveedor},
        bcc      = emails,
    )


def notificar_cancelacion_solicitada(rfq, solicitante, motivo=''):
    """Solicitud de eliminación lógica — notifica a los admins (BCC)."""
    emails = _emails_admins()
    if not emails:
        logger.warning('notificar_cancelacion_solicitada: no hay usuarios admin.')
        return
    _enviar(
        subject  = f'[BOCAR] Solicitud de cancelación — RFQ #{rfq.id}',
        template = 'notificaciones/solicitud_cancelacion.html',
        context  = {'rfq': rfq, 'solicitante': solicitante, 'motivo': motivo},
        bcc      = emails,
    )


def notificar_cancelacion_confirmada(rfq, cancelado_por, motivo=''):
    """Eliminación lógica ejecutada — notifica a Industrialización y Comercialización (BCC)."""
    emails = list(set(
        _emails_por_rol(ROL_INDUSTRIALIZACION) + _emails_por_rol(ROL_COMERCIALIZACION)
    ))
    if not emails:
        logger.warning('notificar_cancelacion_confirmada: no hay destinatarios internos.')
        return
    _enviar(
        subject  = f'[BOCAR] RFQ #{rfq.id} cancelada',
        template = 'notificaciones/cancelacion_confirmada.html',
        context  = {'rfq': rfq, 'cancelado_por': cancelado_por, 'motivo': motivo},
        bcc      = emails,
    )


def notificar_modificacion_rfq(rfq, modificado_por, roles_destino):
    """Modificación en una RFQ — notifica a los roles involucrados (BCC).

    roles_destino: lista de valores de CustomUser.Roles,
                   e.g. [ROL_INDUSTRIALIZACION] o [ROL_COMERCIALIZACION].
    """
    emails = list(set(
        email
        for rol in roles_destino
        for email in _emails_por_rol(rol)
    ))
    if not emails:
        logger.warning('notificar_modificacion_rfq: sin destinatarios para roles %s.', roles_destino)
        return
    _enviar(
        subject  = f'[BOCAR] Modificación en RFQ #{rfq.id}',
        template = 'notificaciones/modificacion_rfq.html',
        context  = {'rfq': rfq, 'modificado_por': modificado_por},
        bcc      = emails,
    )
