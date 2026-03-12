from django.db import models
from django.utils import timezone
from datetime import timedelta


class TipoActivoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)


class TipoActivo(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    objects = TipoActivoManager()      # Solo activos
    all_objects = models.Manager()     # Todos

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

    # obligatorio
    imagen = models.ImageField(
        upload_to="activos/",
    )

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

    frecuencia_mantenimiento = models.IntegerField(
        default=60,
        help_text="Cada cuantos días se debe hacer mantenimiento preventivo"
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo_activo.nombre})"

    def necesita_mantenimiento(self):

        ultimo_mantenimiento = self.mantenimientos.filter(
            tipo="preventivo",
            estado="completado"
        ).order_by("-fecha_finalizacion").first()

        if ultimo_mantenimiento and ultimo_mantenimiento.fecha_finalizacion:
            fecha_base = ultimo_mantenimiento.fecha_finalizacion
        else:
            fecha_base = self.fecha_registro.date()

        proximo = fecha_base + timedelta(days=self.frecuencia_mantenimiento)

        return timezone.now().date() >= proximo


class Caracteristica(models.Model):

    TIPOS_DATO = [
        ('text', 'Texto'),
        ('int', 'Número entero'),
        ('float', 'Número decimal'),
        ('date', 'Fecha'),
        ('boolean', 'Booleano'),
        ('select', 'Selección'),
        ('multiselect', 'Selección múltiple'),
    ]

    tipo_activo = models.ForeignKey(
        TipoActivo,
        on_delete=models.CASCADE,
        related_name='caracteristicas'
    )

    nombre = models.CharField(max_length=100)

    tipo_dato = models.CharField(
        max_length=20,
        choices=TIPOS_DATO,
        default='text'
    )

    obligatorio = models.BooleanField(
        default=False,
        help_text="Indica si esta característica es obligatoria"
    )

    tamano = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.tipo_activo.nombre} - {self.nombre}"

    class Meta:
        unique_together = ['tipo_activo', 'nombre']


class OpcionCaracteristica(models.Model):

    caracteristica = models.ForeignKey(
        Caracteristica,
        on_delete=models.CASCADE,
        related_name='opciones'
    )

    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.caracteristica.nombre} - {self.nombre}"


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

    # para valores simples
    valor_texto = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # para select
    opcion = models.ForeignKey(
        OpcionCaracteristica,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.activo.nombre} - {self.caracteristica.nombre}"