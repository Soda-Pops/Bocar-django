import shutil
import tempfile
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from users.models import CustomUser
from RFQ_Mold.models import RFQ_Mold, RFQ_Mold_File
from Proveedores.models import Proveedor
from Asignaciones.models import Asignacion_Proveedor_Mold
from Prov_RFQ_Mold.models import Cost_Breakdown_Mold
from Industrializacion.views import RFQEnviarAComercializacionView
from Comercializacion.views import CrearAsignacionesView
from Asignaciones.views import AsignacionEnviarRespuestaView
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


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRACIÓN — los endpoints de avance de flujo encolan su tarea
# Verifica que el guard `if settings.NOTIFICATIONS_ENABLED` funciona en cada vista.
# ─────────────────────────────────────────────────────────────────────────────

_TMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
class FlujoNotificacionesViewsTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(_TMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.factory = APIRequestFactory()
        self.ind = make_user('ind', 'ind@test.com', role=ROL_INDUSTRIALIZACION)
        self.com = make_user('com', 'com@test.com', role=ROL_COMERCIALIZACION)
        self.pro = make_user('pro', 'pro@test.com', role=ROL_PROVEEDOR)
        self.proveedor = Proveedor.objects.create(
            id_account=self.pro, company_name='ACME', contact_email='acme@test.com',
        )
        self.futuro = date.today() + timedelta(days=30)
        self.rfq = RFQ_Mold.objects.create(created_by=self.ind, due_date=self.futuro)

    # ── Industrialización → Comercialización (notificar_comercializacion) ──
    @override_settings(NOTIFICATIONS_ENABLED=True)
    @patch('Industrializacion.views.notif_tasks.notificar_comercializacion.delay')
    def test_enviar_a_comercializacion_encola_tarea(self, mock_delay):
        RFQ_Mold_File.objects.create(
            rfq_mold=self.rfq, archivo=SimpleUploadedFile('f.txt', b'x'),
        )
        request = self.factory.post('/?tipo=mold')
        force_authenticate(request, user=self.ind)
        response = RFQEnviarAComercializacionView.as_view()(request, pk=self.rfq.id)
        self.assertEqual(response.status_code, 200)
        mock_delay.assert_called_once_with(self.rfq.id, 'mold')

    @override_settings(NOTIFICATIONS_ENABLED=False)
    @patch('Industrializacion.views.notif_tasks.notificar_comercializacion.delay')
    def test_enviar_a_comercializacion_flag_off_no_encola(self, mock_delay):
        RFQ_Mold_File.objects.create(
            rfq_mold=self.rfq, archivo=SimpleUploadedFile('f.txt', b'x'),
        )
        request = self.factory.post('/?tipo=mold')
        force_authenticate(request, user=self.ind)
        response = RFQEnviarAComercializacionView.as_view()(request, pk=self.rfq.id)
        self.assertEqual(response.status_code, 200)
        mock_delay.assert_not_called()

    # ── Comercialización → Proveedores (notificar_proveedores) ──
    @override_settings(NOTIFICATIONS_ENABLED=True)
    @patch('Comercializacion.views.notif_tasks.notificar_proveedores.delay')
    def test_crear_asignaciones_encola_tarea(self, mock_delay):
        request = self.factory.post(
            '/?tipo=mold',
            {
                'id_rfq': self.rfq.id,
                'due_date': self.futuro.isoformat(),
                'proveedores': [self.proveedor.id],
            },
            format='json',
        )
        force_authenticate(request, user=self.com)
        response = CrearAsignacionesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        mock_delay.assert_called_once_with(self.rfq.id, 'mold')

    # ── Proveedor envía cotización (notificar_cotizacion_recibida) ──
    @override_settings(NOTIFICATIONS_ENABLED=True)
    @patch('Asignaciones.views.notif_tasks.notificar_cotizacion_recibida.delay')
    def test_enviar_respuesta_encola_tarea(self, mock_delay):
        asignacion = Asignacion_Proveedor_Mold.objects.create(
            id_RFQ_Mold=self.rfq,
            id_Proveedor=self.proveedor,
            id_user_comercializacion=self.com,
            due_date=self.futuro,
        )
        Cost_Breakdown_Mold.objects.create(id_asignacion=asignacion)
        request = self.factory.post('/?tipo=mold')
        force_authenticate(request, user=self.pro)
        response = AsignacionEnviarRespuestaView.as_view()(request, id_asignacion=asignacion.id)
        self.assertEqual(response.status_code, 200)
        mock_delay.assert_called_once_with(self.rfq.id, 'mold', self.pro.id)
