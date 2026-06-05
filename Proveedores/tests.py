from django.test import TestCase

from users.models import CustomUser

from .models import Proveedor
from .serializers import ProveedorListSerializer


class ProveedorListSerializerTests(TestCase):
    def test_country_is_serialized_as_iso_code(self):
        user = CustomUser.objects.create_user(
            username='proveedor',
            email='proveedor@example.com',
            password='pass12345',
            role='Pro',
        )
        proveedor = Proveedor.objects.create(
            id_account=user,
            company_name='Proveedor MX',
            contact_email='ventas@example.com',
            country='MX',
        )

        data = ProveedorListSerializer(proveedor).data

        self.assertEqual(data['country'], 'MX')
        self.assertEqual(data['country_name'], 'Mexico')
