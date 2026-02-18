from django.db import models
from django.conf import settings


class Area(models.Model):

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='areas_responsables'
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
