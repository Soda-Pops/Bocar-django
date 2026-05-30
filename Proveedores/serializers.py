from rest_framework import serializers
from .models import Proveedor


class ProveedorListSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para listar proveedores.
    Expone únicamente los campos relevantes para el área de Comercialización.
    """

    # Trae el email de la cuenta de usuario enlazada por el OneToOneField
    account_email = serializers.ReadOnlyField(source='id_account.email')

    # Devuelve el nombre legible del país en lugar del código ISO
    country_name  = serializers.SerializerMethodField()

    # Devuelve el nombre legible del continente en lugar del código
    continent_name = serializers.SerializerMethodField()

    def get_country_name(self, obj):
        # CountryField tiene un método .name que devuelve el nombre completo del país
        return obj.country.name if obj.country else None

    def get_continent_name(self, obj):
        # get_FOO_display() devuelve el label del TextChoices en lugar del valor corto
        return obj.get_continent_display()

    class Meta:
        model  = Proveedor
        fields = [
            'id',
            'company_name',
            'contact_email',
            'account_email',
            'country',          # código ISO (ej. 'MX')
            'country_name',     # nombre completo (ej. 'Mexico')
            'continent',        # código corto (ej. 'NA')
            'continent_name',   # nombre completo (ej. 'North America')
            'rating',
        ]