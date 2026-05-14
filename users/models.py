from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        SIN_ASIGNAR = "SinRol", "Sin Rol Asignado"
        INDUSTRIALIZACION = 'Ind', 'Industrialización'
        COMERCIALIZACION = 'Com', 'Comercialización'
        PROVEEDOR = 'Pro', 'Proveedor'

    # Añade los atributos que requieras
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.SIN_ASIGNAR,
        verbose_name="Role"
    )
    is_admin = models.BooleanField("is admin", default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username