from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings

from users.models import CustomUser
from RFQ_Mold.models import RFQ_Mold
from notificaciones import services, tasks
from notificaciones.services import ROL_INDUSTRIALIZACION, ROL_COMERCIALIZACION, ROL_PROVEEDOR


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def make_user(username, email, role=None, is_admin=False):
    user = CustomUser.objects.create_user(
        username=username, email=email, password='test1234'
    )
    if role:
        user.role = role
    user.is_admin = is_admin
    user.save()
    return user


# ─────────────────────────────────────────────────────────────────────────────
# SERVICES — lógica de envío
# ─────────────────────────────────────────────────────────────────────────────

class EnviarTest(TestCase):
    """Tests sobre la función _enviar: BCC, TO, y caso vacío."""

    @patch('notificaciones.services.render_to_string', return_value='<html/>')
    @patch('notificaciones.services.EmailMultiAlternatives')
    @override_settings(EMAIL_HOST_USER='sender@bocar.com')
    def test_correo_usa_bcc_y_to_es_sender(self, mock_cls, _mock_render):
        mock_msg = MagicMock()
        mock_cls.return_value = mock_msg

        services._enviar('Asunto', 'tpl.html', {}, ['a@test.com', 'b@test.com'])

        kwargs = mock_cls.call_args.kwargs
        self.assertEqual(kwargs['to'], ['sender@bocar.com'])
        self.assertEqual(kwargs['bcc'], ['a@test.com', 'b@test.com'])
        mock_msg.send.assert_called_once_with(fail_silently=False)

    @patch('notificaciones.services.EmailMultiAlternatives')
    def test_bcc_vacio_no_envia_correo(self, mock_cls):
        services._enviar('Asunto', 'tpl.html', {}, [])
        mock_cls.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# SERVICES — funciones de notificación
# ─────────────────────────────────────────────────────────────────────────────

class NotificacionServicesTest(TestCase):

    def setUp(self):
        self.ind   = make_user('ind',   'ind@test.com',   role=ROL_INDUSTRIALIZACION)
        self.com   = make_user('com',   'com@test.com',   role=ROL_COMERCIALIZACION)
        self.pro   = make_user('pro',   'pro@test.com',   role=ROL_PROVEEDOR)
        self.admin = make_user('admin', 'admin@test.com', is_admin=True)
        self.rfq   = RFQ_Mold.objects.create(
            created_by=self.ind, due_date=date(2026, 12, 31)
        )

    # notificar_comercializacion
    @patch('notificaciones.services._enviar')
    def test_comercializacion_envia_solo_a_com(self, mock_enviar):
        services.notificar_comercializacion(self.rfq)
        mock_enviar.assert_called_once()
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('com@test.com', bcc)
        self.assertNotIn('ind@test.com', bcc)

    @patch('notificaciones.services._enviar')
    def test_comercializacion_sin_usuarios_no_envia(self, mock_enviar):
        CustomUser.objects.filter(role=ROL_COMERCIALIZACION).delete()
        services.notificar_comercializacion(self.rfq)
        mock_enviar.assert_not_called()

    # notificar_proveedores
    @patch('notificaciones.services._enviar')
    def test_proveedores_envia_solo_a_pro(self, mock_enviar):
        services.notificar_proveedores(self.rfq)
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('pro@test.com', bcc)
        self.assertNotIn('com@test.com', bcc)

    # notificar_cancelacion_confirmada
    @patch('notificaciones.services._enviar')
    def test_cancelacion_confirmada_envia_a_ind_y_com(self, mock_enviar):
        services.notificar_cancelacion_confirmada(self.rfq, self.admin)
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('ind@test.com', bcc)
        self.assertIn('com@test.com', bcc)
        self.assertNotIn('pro@test.com', bcc)

    @patch('notificaciones.services._enviar')
    def test_cancelacion_confirmada_sin_internos_no_envia(self, mock_enviar):
        CustomUser.objects.filter(role__in=[ROL_INDUSTRIALIZACION, ROL_COMERCIALIZACION]).update(
            role=CustomUser.Roles.SIN_ASIGNAR
        )
        services.notificar_cancelacion_confirmada(self.rfq, self.admin)
        mock_enviar.assert_not_called()

    # notificar_cancelacion_solicitada
    @patch('notificaciones.services._enviar')
    def test_cancelacion_solicitada_envia_solo_a_admins(self, mock_enviar):
        services.notificar_cancelacion_solicitada(self.rfq, self.ind, 'motivo')
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('admin@test.com', bcc)
        self.assertNotIn('ind@test.com', bcc)

    # notificar_modificacion_rfq
    @patch('notificaciones.services._enviar')
    def test_modificacion_envia_a_industrializacion(self, mock_enviar):
        services.notificar_modificacion_rfq(self.rfq, self.com, [ROL_INDUSTRIALIZACION])
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('ind@test.com', bcc)
        self.assertNotIn('com@test.com', bcc)

    @patch('notificaciones.services._enviar')
    def test_modificacion_envia_a_comercializacion(self, mock_enviar):
        services.notificar_modificacion_rfq(self.rfq, self.ind, [ROL_COMERCIALIZACION])
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('com@test.com', bcc)
        self.assertNotIn('ind@test.com', bcc)

    @patch('notificaciones.services._enviar')
    def test_modificacion_sin_destinatarios_no_envia(self, mock_enviar):
        CustomUser.objects.filter(role=ROL_INDUSTRIALIZACION).update(
            role=CustomUser.Roles.SIN_ASIGNAR
        )
        services.notificar_modificacion_rfq(self.rfq, self.com, [ROL_INDUSTRIALIZACION])
        mock_enviar.assert_not_called()

    # notificar_cotizacion_recibida
    @patch('notificaciones.services._enviar')
    def test_cotizacion_recibida_envia_a_com(self, mock_enviar):
        services.notificar_cotizacion_recibida(self.rfq, self.pro)
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('com@test.com', bcc)
        self.assertNotIn('pro@test.com', bcc)


# ─────────────────────────────────────────────────────────────────────────────
# TASKS — ejecución síncrona con .apply()
# ─────────────────────────────────────────────────────────────────────────────

class NotificacionTasksTest(TestCase):

    def setUp(self):
        self.ind   = make_user('ind',   'ind@test.com',   role=ROL_INDUSTRIALIZACION)
        self.com   = make_user('com',   'com@test.com',   role=ROL_COMERCIALIZACION)
        self.admin = make_user('admin', 'admin@test.com', is_admin=True)
        self.rfq   = RFQ_Mold.objects.create(
            created_by=self.ind, due_date=date(2026, 12, 31)
        )

    @patch('notificaciones.services._enviar')
    def test_task_cancelacion_confirmada(self, mock_enviar):
        result = tasks.notificar_cancelacion_confirmada.apply(
            args=[self.rfq.id, 'mold', self.admin.id]
        )
        self.assertTrue(result.successful())
        mock_enviar.assert_called_once()
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('ind@test.com', bcc)
        self.assertIn('com@test.com', bcc)

    @patch('notificaciones.services._enviar')
    def test_task_modificacion_rfq(self, mock_enviar):
        result = tasks.notificar_modificacion_rfq.apply(
            args=[self.rfq.id, 'mold', self.com.id, [ROL_INDUSTRIALIZACION]]
        )
        self.assertTrue(result.successful())
        mock_enviar.assert_called_once()
        bcc = mock_enviar.call_args.kwargs['bcc']
        self.assertIn('ind@test.com', bcc)

    @patch('notificaciones.services._enviar')
    def test_task_rfq_tipo_invalido_lanza_excepcion(self, _mock_enviar):
        result = tasks.notificar_cancelacion_confirmada.apply(
            args=[self.rfq.id, 'invalido', self.admin.id]
        )
        self.assertFalse(result.successful())
