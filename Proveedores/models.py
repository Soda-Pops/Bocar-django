from django.db import models
from Bocar import settings
from django_countries.fields import CountryField

# Create your models here.
class Proveedor(models.Model):

    class Continente(models.TextChoices):
        AMERICA_NORTE  = 'NA', 'North America'
        AMERICA_LATINA = 'LA', 'Latin America'
        EUROPA         = 'EU', 'Europe'
        ASIA           = 'AS', 'Asia'
        AFRICA         = 'AF', 'Africa'
        OCEANIA        = 'OC', 'Oceania'
    
    
    id_account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proveedor'
    )
    company_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    country = CountryField(blank=True, null=True)
    continent = models.CharField(max_length=2, choices=Continente.choices, default= 'NA') # en esto tengo dudas del default, o no se si se pueda identificar el continente por pais
    rating = models.FloatField()

    def __str__(self):
        return self.company_name
    
    class Meta:
        db_table = 'Proveedores'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'