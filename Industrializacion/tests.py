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
