import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming


class RFQEditarViewTests(APITestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.user = get_user_model().objects.create_user(
            username='industrializacion',
            email='industrializacion@example.com',
            password='test-pass-123',
            role='Ind',
        )
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_patch_mold_draft_with_file_creates_related_attachment(self):
        rfq = RFQ_Mold.objects.create(
            created_by=self.user,
            due_date='2026-06-18',
            DESC='original',
        )
        archivo = SimpleUploadedFile(
            'link-repo.pdf',
            b'%PDF-1.4 test',
            content_type='application/pdf',
        )

        response = self.client.patch(
            f"{reverse('industrializacion-rfq-editar', kwargs={'pk': rfq.pk})}?tipo=mold",
            {'DESC': 'actualizado', 'archivos': [archivo]},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rfq.refresh_from_db()
        self.assertEqual(rfq.DESC, 'actualizado')
        self.assertEqual(rfq.archivos.count(), 1)

    def test_patch_trimming_draft_with_file_creates_related_attachment(self):
        rfq = RFQ_Trimming.objects.create(
            created_by=self.user,
            due_date='2026-06-18',
            DESC='original',
        )
        archivo = SimpleUploadedFile(
            'link-repo.pdf',
            b'%PDF-1.4 test',
            content_type='application/pdf',
        )

        response = self.client.patch(
            f"{reverse('industrializacion-rfq-editar', kwargs={'pk': rfq.pk})}?tipo=trimming",
            {'DESC': 'actualizado', 'archivos': [archivo]},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rfq.refresh_from_db()
        self.assertEqual(rfq.DESC, 'actualizado')
        self.assertEqual(rfq.archivos.count(), 1)


class RFQAdminLogicalDeleteVisibilityTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.normal_user = User.objects.create_user(
            username='ind-normal',
            email='ind-normal@example.com',
            password='test-pass-123',
            role='Ind',
        )
        self.admin_user = User.objects.create_user(
            username='ind-admin',
            email='ind-admin@example.com',
            password='test-pass-123',
            role='Ind',
            is_admin=True,
        )
        self.deleted_mold = RFQ_Mold.objects.create(
            created_by=self.normal_user,
            due_date='2026-06-18',
            DESC='deleted mold',
            status=RFQ_Mold.Status.COMERCIALIZACION,
            logical_delete=True,
        )
        self.deleted_trimming = RFQ_Trimming.objects.create(
            created_by=self.normal_user,
            due_date='2026-06-18',
            DESC='deleted trimming',
            status=RFQ_Trimming.Status.COMERCIALIZACION,
            logical_delete=True,
        )

    def test_admin_list_includes_logically_deleted_rfqs(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(reverse('industrializacion-rfq-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.deleted_mold.id, [item['id'] for item in response.data['mold']])
        self.assertIn(self.deleted_trimming.id, [item['id'] for item in response.data['trimming']])
        self.assertTrue(response.data['mold'][0]['logical_delete'])

    def test_normal_user_list_excludes_logically_deleted_rfqs(self):
        self.client.force_authenticate(self.normal_user)

        response = self.client.get(reverse('industrializacion-rfq-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.deleted_mold.id, [item['id'] for item in response.data['mold']])
        self.assertNotIn(self.deleted_trimming.id, [item['id'] for item in response.data['trimming']])

    def test_admin_can_get_deleted_rfq_detail(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(
            f"{reverse('industrializacion-rfq-editar', kwargs={'pk': self.deleted_mold.pk})}?tipo=mold",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['logical_delete'])

    def test_normal_user_get_deleted_rfq_detail_returns_404(self):
        self.client.force_authenticate(self.normal_user)

        response = self.client.get(
            f"{reverse('industrializacion-rfq-editar', kwargs={'pk': self.deleted_mold.pk})}?tipo=mold",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
