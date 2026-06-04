import shutil
import tempfile
from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from users.models import CustomUser
from RFQ_Mold.models import RFQ_Mold, RFQ_Mold_File, RFQ_Mold_EditRequest
from RFQ_Mold.serializers import RFQMoldCreateSerializer, MoldEditRequestApproveSerializer
from RFQ_Mold.views import RFQMoldLogicalDeleteView
from Proveedores.models import Proveedor
from Industrializacion.views import RFQEditarView, RFQEnviarAComercializacionView
from Comercializacion.views import CrearAsignacionesView
from historial.models import RFQHistorial
from historial.services import diff_campos, registrar_historial
from historial.views import RFQHistorialView


def make_user(username, email, role=None, is_admin=False):
    user = CustomUser.objects.create_user(username=username, email=email, password='test1234')
    if role:
        user.role = role
    user.is_admin = is_admin
    user.save()
    return user


# ─────────────────────────────────────────────────────────────────────────────
# Helper diff_campos (unitario)
# ─────────────────────────────────────────────────────────────────────────────

class DiffCamposTest(TestCase):
    def test_detecta_cambios_e_ignora_archivos(self):
        ind = make_user('ind', 'ind@test.com', role='Ind')
        rfq = RFQ_Mold.objects.create(created_by=ind, due_date=date(2030, 1, 1), DESC='viejo')
        cambios = diff_campos(rfq, {'DESC': 'nuevo', 'archivos': ['x'], 'PPY': rfq.PPY})
        self.assertEqual(cambios, {'DESC': {'antes': 'viejo', 'despues': 'nuevo'}})


# ─────────────────────────────────────────────────────────────────────────────
# Integración — cada evento del flujo crea su fila de historial
# ─────────────────────────────────────────────────────────────────────────────

_TMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
class HistorialFlujoTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(_TMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.factory = APIRequestFactory()
        self.ind = make_user('ind', 'ind@test.com', role='Ind')
        self.com = make_user('com', 'com@test.com', role='Com', is_admin=True)
        self.pro = make_user('pro', 'pro@test.com', role='Pro')
        self.proveedor = Proveedor.objects.create(
            id_account=self.pro, company_name='ACME', contact_email='acme@test.com',
        )
        self.futuro = date.today() + timedelta(days=30)

    def _rfq(self, **kwargs):
        return RFQ_Mold.objects.create(created_by=self.ind, due_date=self.futuro, **kwargs)

    # ── CREACION (vía serializer compartido) ──
    def test_creacion_registra_historial(self):
        serializer = RFQMoldCreateSerializer(data={'due_date': self.futuro.isoformat()})
        serializer.is_valid(raise_exception=True)
        rfq = serializer.save(created_by=self.ind)
        evento = RFQHistorial.objects.get(rfq_tipo='mold', rfq_id=rfq.id)
        self.assertEqual(evento.evento, RFQHistorial.Evento.CREACION)
        self.assertEqual(evento.actor, self.ind)

    # ── EDICION con diff ──
    def test_edicion_registra_diff(self):
        rfq = self._rfq(DESC='viejo')
        request = self.factory.patch('/?tipo=mold', {'DESC': 'nuevo'}, format='json')
        force_authenticate(request, user=self.ind)
        response = RFQEditarView.as_view()(request, pk=rfq.id)
        self.assertEqual(response.status_code, 200)
        evento = RFQHistorial.objects.get(rfq_id=rfq.id, evento=RFQHistorial.Evento.EDICION)
        self.assertEqual(evento.cambios['DESC'], {'antes': 'viejo', 'despues': 'nuevo'})

    # ── ENVIO_COMERCIALIZACION ──
    def test_envio_comercializacion_registra_status(self):
        rfq = self._rfq()
        RFQ_Mold_File.objects.create(rfq_mold=rfq, archivo=SimpleUploadedFile('f.txt', b'x'))
        request = self.factory.post('/?tipo=mold')
        force_authenticate(request, user=self.ind)
        response = RFQEnviarAComercializacionView.as_view()(request, pk=rfq.id)
        self.assertEqual(response.status_code, 200)
        evento = RFQHistorial.objects.get(rfq_id=rfq.id, evento=RFQHistorial.Evento.ENVIO_COMERCIALIZACION)
        self.assertEqual(evento.status_anterior, 'En_Ind')
        self.assertEqual(evento.status_nuevo, 'En_Com')

    # ── ASIGNACION + ENVIO_PROVEEDORES ──
    def test_asignacion_registra_dos_eventos(self):
        rfq = self._rfq(status=RFQ_Mold.Status.COMERCIALIZACION)
        request = self.factory.post(
            '/?tipo=mold',
            {'id_rfq': rfq.id, 'due_date': self.futuro.isoformat(), 'proveedores': [self.proveedor.id]},
            format='json',
        )
        force_authenticate(request, user=self.com)
        response = CrearAsignacionesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        eventos = set(
            RFQHistorial.objects.filter(rfq_id=rfq.id).values_list('evento', flat=True)
        )
        self.assertIn(RFQHistorial.Evento.ENVIO_PROVEEDORES, eventos)
        self.assertIn(RFQHistorial.Evento.ASIGNACION_PROVEEDORES, eventos)

    # ── CANCELACION ──
    def test_cancelacion_registra_historial(self):
        rfq = self._rfq()
        request = self.factory.patch('/')
        force_authenticate(request, user=self.com)
        response = RFQMoldLogicalDeleteView.as_view()(request, pk=rfq.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            RFQHistorial.objects.filter(rfq_id=rfq.id, evento=RFQHistorial.Evento.CANCELACION).exists()
        )

    # ── EDICION_APROBADA vía serializer compartido (cubre ruta vieja y nueva) ──
    def test_aprobar_edicion_registra_historial(self):
        rfq = self._rfq(status=RFQ_Mold.Status.COMERCIALIZACION)
        edit = RFQ_Mold_EditRequest.objects.create(rfq_mold=rfq, requested_by=self.ind)
        request = self.factory.patch('/')
        request.user = self.com
        serializer = MoldEditRequestApproveSerializer(
            edit, data={'status': 'Aprobada'}, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.assertTrue(
            RFQHistorial.objects.filter(rfq_id=rfq.id, evento=RFQHistorial.Evento.EDICION_APROBADA).exists()
        )

    # ── Endpoint de lectura ──
    def test_get_historial_autenticado(self):
        rfq = self._rfq()
        registrar_historial(rfq_tipo='mold', rfq_id=rfq.id,
                            evento=RFQHistorial.Evento.CREACION, actor=self.ind)
        request = self.factory.get('/')
        force_authenticate(request, user=self.ind)
        response = RFQHistorialView.as_view()(request, tipo='mold', rfq_id=rfq.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['evento'], RFQHistorial.Evento.CREACION)

    def test_get_historial_sin_auth_rechazado(self):
        request = self.factory.get('/')
        response = RFQHistorialView.as_view()(request, tipo='mold', rfq_id=1)
        self.assertIn(response.status_code, (401, 403))

    # ── Filtros del endpoint ──
    def _poblar_eventos(self, rfq):
        registrar_historial(rfq_tipo='mold', rfq_id=rfq.id,
                            evento=RFQHistorial.Evento.CREACION, actor=self.ind)
        registrar_historial(rfq_tipo='mold', rfq_id=rfq.id,
                            evento=RFQHistorial.Evento.EDICION, actor=self.ind)
        registrar_historial(rfq_tipo='mold', rfq_id=rfq.id,
                            evento=RFQHistorial.Evento.CANCELACION, actor=self.com)

    def _get(self, rfq_id, query=''):
        request = self.factory.get(f'/{query}')
        force_authenticate(request, user=self.ind)
        return RFQHistorialView.as_view()(request, tipo='mold', rfq_id=rfq_id)

    def test_filtro_por_evento(self):
        rfq = self._rfq()
        self._poblar_eventos(rfq)
        response = self._get(rfq.id, '?evento=CANCELACION')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['evento'], RFQHistorial.Evento.CANCELACION)

    def test_filtro_por_varios_eventos(self):
        rfq = self._rfq()
        self._poblar_eventos(rfq)
        response = self._get(rfq.id, '?evento=CREACION&evento=EDICION')
        self.assertEqual(response.data['count'], 2)

    def test_filtro_por_actor(self):
        rfq = self._rfq()
        self._poblar_eventos(rfq)
        response = self._get(rfq.id, f'?actor={self.com.id}')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['evento'], RFQHistorial.Evento.CANCELACION)

    def test_paginacion(self):
        rfq = self._rfq()
        self._poblar_eventos(rfq)  # 3 eventos
        response = self._get(rfq.id, '?page_size=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['next'])

    def test_filtro_evento_invalido(self):
        rfq = self._rfq()
        response = self._get(rfq.id, '?evento=NO_EXISTE')
        self.assertEqual(response.status_code, 400)

    def test_filtro_fecha_invalida(self):
        rfq = self._rfq()
        response = self._get(rfq.id, '?desde=2026-31-31')
        self.assertEqual(response.status_code, 400)
