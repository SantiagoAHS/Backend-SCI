from django.db import models
from django.utils import timezone

class Auditoria(models.Model):
    ESTADO_AUDITORIA = [
        ("pendiente", "Pendiente"),
        ("en_proceso", "En proceso"),
        ("finalizada", "Finalizada"),
    ]

    TIPO_AUDITORIA = [
        ("mantenimiento", "Mantenimiento"),
        ("prestamo", "Préstamo"),
        ("disponible", "Disponible"),
    ]

    nombre = models.CharField(max_length=150)
    responsable = models.CharField(max_length=150)
    area = models.ForeignKey(
        "areas.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_AUDITORIA,
        blank=True,
        null=True
    )
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_AUDITORIA, default="pendiente")
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        desc = ""
        if self.area:
            desc += f"{self.area.nombre}"
        else:
            desc += "General"
        if self.tipo:
            desc += f" - {self.tipo.capitalize()}"
        return f"{self.nombre} - {desc}"
    
class DetalleAuditoria(models.Model):

    RESULTADO_CHOICES = [
        ("correcto", "Correcto"),
        ("incorrecto", "Incorrecto"),
    ]

    auditoria = models.ForeignKey(
        Auditoria,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    activo = models.ForeignKey(
        "activos.Activo",
        on_delete=models.CASCADE,
        related_name="auditorias"
    )

    # Datos del sistema (se guardan automáticamente)
    estado_sistema = models.CharField(max_length=20, blank=True)
    
    area_sistema = models.ForeignKey(
        "areas.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+"
    )

    # Datos reales (los llena el usuario)
    estado_real = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    area_real = models.ForeignKey(
        "areas.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+"
    )

    encontrado = models.BooleanField(default=True)

    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        blank=True
    )

    observaciones = models.TextField(blank=True, null=True)

    fecha_revision = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['auditoria', 'activo']  

    def save(self, *args, **kwargs):

        # Autollenado de datos del sistema
        if not self.estado_sistema:
            self.estado_sistema = self.activo.estado

        if not self.area_sistema:
            self.area_sistema = self.activo.area

        # Lógica de resultado
        if not self.encontrado:
            self.resultado = "incorrecto"

        elif self.estado_real and self.area_real:
            if (
                self.estado_sistema == self.estado_real and
                self.area_sistema == self.area_real
            ):
                self.resultado = "correcto"
            else:
                self.resultado = "incorrecto"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.auditoria} - {self.activo}"