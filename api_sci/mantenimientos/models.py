from django.db import models
from django.utils import timezone


class Mantenimiento(models.Model):

    TIPO_MANTENIMIENTO = [
        ("preventivo", "Preventivo"),
        ("correctivo", "Correctivo"),
    ]

    ESTADO_MANTENIMIENTO = [
        ("programado", "Programado"),
        ("en_proceso", "En proceso"),
        ("completado", "Completado"),
        ("cancelado", "Cancelado"),
    ]

    activo = models.ForeignKey(
        "activos.Activo",
        on_delete=models.CASCADE,
        related_name="mantenimientos"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_MANTENIMIENTO
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_MANTENIMIENTO,
        default="programado"
    )

    fecha_ingreso = models.DateField(default=timezone.now)
    fecha_finalizacion = models.DateField(blank=True, null=True)

    responsable = models.CharField(
        max_length=200,
        help_text="Nombre del técnico o empresa responsable"
    )

    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    comprobante = models.FileField(
        upload_to="mantenimientos/comprobantes/",
        blank=True,
        null=True
    )

    descripcion_problema = models.TextField(blank=True, null=True)
    acciones_realizadas = models.TextField(blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        # Si entra en proceso → cambiar activo a mantenimiento
        if self.estado == "en_proceso":
            self.activo.estado = "mantenimiento"
            self.activo.save()

        # Si se completa → activo vuelve a disponible
        if self.estado == "completado":
            self.activo.estado = "disponible"
            self.activo.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.activo.nombre} - {self.tipo} ({self.estado})"