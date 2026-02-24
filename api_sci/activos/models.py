from django.db import models
from django.conf import settings


class TipoActivo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Activo(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    tipo_activo = models.ForeignKey(
        TipoActivo,
        on_delete=models.PROTECT,
        related_name='activos'
    )

    area = models.ForeignKey(
        'areas.Area',  # suponiendo que tu app de Area se llama areas
        on_delete=models.PROTECT,
        related_name='activos'
    )

    responsable_directo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activos_asignados'
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo_activo.nombre})"


class Caracteristica(models.Model):
    tipo_activo = models.ForeignKey(
        TipoActivo,
        on_delete=models.CASCADE,
        related_name='caracteristicas'
    )

    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.tipo_activo.nombre} - {self.nombre}"


class ValorCaracteristica(models.Model):
    activo = models.ForeignKey(
        Activo,
        on_delete=models.CASCADE,
        related_name='valores'
    )

    caracteristica = models.ForeignKey(
        Caracteristica,
        on_delete=models.CASCADE
    )

    valor = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.activo.nombre} - {self.caracteristica.nombre}"