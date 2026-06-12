from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Asignaciones.models import Asignacion_Proveedor_Mold
from historial.models import RFQHistorial
from Proveedores.models import Proveedor
from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming


class RFQListComercializacionAdminVisibilityTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.creator = User.objects.create_user(
            username='ind-creator',
            email='ind-creator@example.com',
            password='test-pass-123',
            role='Ind',
        )
        self.normal_user = User.objects.create_user(
            username='com-normal',
            email='com-normal@example.com',
            password='test-pass-123',
            role='Com',
        )
        self.admin_user = User.objects.create_user(
            username='com-admin',
            email='com-admin@example.com',
            password='test-pass-123',
            role='Com',
            is_admin=True,
        )
        self.deleted_mold = RFQ_Mold.objects.create(
            created_by=self.creator,
            due_date='2026-06-18',
            DESC='deleted mold',
            status=RFQ_Mold.Status.COMERCIALIZACION,
            logical_delete=True,
        )
        self.deleted_trimming = RFQ_Trimming.objects.create(
            created_by=self.creator,
            due_date='2026-06-18',
            DESC='deleted trimming',
            status=RFQ_Trimming.Status.COMERCIALIZACION,
            logical_delete=True,
        )

    def test_admin_list_includes_logically_deleted_rfqs(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(reverse('comercializacion-rfq-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.deleted_mold.id, [item['id'] for item in response.data['mold']])
        self.assertIn(self.deleted_trimming.id, [item['id'] for item in response.data['trimming']])
        self.assertTrue(response.data['mold'][0]['logical_delete'])

    def test_normal_user_list_excludes_logically_deleted_rfqs(self):
        self.client.force_authenticate(self.normal_user)

        response = self.client.get(reverse('comercializacion-rfq-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.deleted_mold.id, [item['id'] for item in response.data['mold']])
        self.assertNotIn(self.deleted_trimming.id, [item['id'] for item in response.data['trimming']])


class ExtenderDeadlineRFQTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.ind_user = User.objects.create_user(
            username='ind-user',
            email='ind-user@example.com',
            password='test-pass-123',
            role='Ind',
        )
        self.com_user = User.objects.create_user(
            username='com-user',
            email='com-user@example.com',
            password='test-pass-123',
            role='Com',
        )
        self.provider_user = User.objects.create_user(
            username='provider-user',
            email='provider-user@example.com',
            password='test-pass-123',
            role='Pro',
        )
        self.provider = Proveedor.objects.create(
            id_account=self.provider_user,
            company_name='Proveedor Test',
            contact_email='provider@example.com',
        )
        self.rfq = RFQ_Mold.objects.create(
            created_by=self.ind_user,
            due_date=date.today() - timedelta(days=2),
            DESC='expired mold',
            status=RFQ_Mold.Status.PROVEEDOR,
        )
        self.assignment = Asignacion_Proveedor_Mold.objects.create(
            id_RFQ_Mold=self.rfq,
            id_Proveedor=self.provider,
            id_user_comercializacion=self.com_user,
            due_date=date.today() - timedelta(days=1),
            is_closed=True,
            is_answered=False,
        )

    def test_com_user_extends_expired_rfq_deadline_and_reopens_assignment(self):
        self.client.force_authenticate(self.com_user)
        new_due_date = date.today() + timedelta(days=7)

        response = self.client.patch(
            f"{reverse('comercializacion-extender-deadline-rfq', kwargs={'pk': self.rfq.pk})}?tipo=mold",
            {'due_date': new_due_date.isoformat()},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rfq.refresh_from_db()
        self.assignment.refresh_from_db()
        self.assertEqual(self.rfq.due_date, new_due_date)
        self.assertEqual(self.assignment.due_date, new_due_date)
        self.assertFalse(self.assignment.is_closed)
        self.assertEqual(response.data['assignments_reopened'], 1)
        self.assertTrue(
            RFQHistorial.objects.filter(
                rfq_tipo=RFQHistorial.Tipo.MOLD,
                rfq_id=self.rfq.id,
                evento=RFQHistorial.Evento.EXTENSION_APROBADA,
            ).exists()
        )

    def test_non_com_user_cannot_extend_rfq_deadline(self):
        self.client.force_authenticate(self.ind_user)
        new_due_date = date.today() + timedelta(days=7)

        response = self.client.patch(
            f"{reverse('comercializacion-extender-deadline-rfq', kwargs={'pk': self.rfq.pk})}?tipo=mold",
            {'due_date': new_due_date.isoformat()},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_new_due_date_must_be_future(self):
        self.client.force_authenticate(self.com_user)

        response = self.client.patch(
            f"{reverse('comercializacion-extender-deadline-rfq', kwargs={'pk': self.rfq.pk})}?tipo=mold",
            {'due_date': date.today().isoformat()},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
