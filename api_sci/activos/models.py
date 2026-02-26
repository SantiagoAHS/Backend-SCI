from django.db import models

class TipoActivoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)

class TipoActivo(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    objects = TipoActivoManager()      # Solo activos
    all_objects = models.Manager()     # Todos (incluye desactivados)

    def __str__(self):
        return self.nombre

class Activo(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('asignado', 'Asignado'),
        ('mantenimiento', 'En mantenimiento'),
        ('baja', 'Baja'),
    ]

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    tipo_activo = models.ForeignKey(
        TipoActivo,
        on_delete=models.PROTECT,
        related_name='activos'
    )

    area = models.ForeignKey(
        'areas.Area',
        on_delete=models.PROTECT,
        related_name='activos'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='disponible'
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

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