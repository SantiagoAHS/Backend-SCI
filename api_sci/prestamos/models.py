from django.db import models
from django.utils import timezone
from datetime import timedelta

class Prestamo(models.Model):

    TIPO_PRESTAMO_CHOICES = [
        ("interno", "Interno"),
        ("externo", "Externo"),
        ("temporal", "Temporal"),
    ]

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("finalizado", "Finalizado"),
        ("vencido", "Vencido"),
        ("cancelado", "Cancelado"),
    ]

    activo = models.ForeignKey(
        "activos.Activo",   
        on_delete=models.CASCADE,
        related_name="prestamos"
    )

    # Responsable externo
    responsable_nombre = models.CharField(max_length=150)
    responsable_telefono = models.CharField(max_length=20, blank=True, null=True)

    # Área donde trabaja
    area = models.ForeignKey(
        "areas.Area",     
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prestamos"
    )

    tipo_prestamo = models.CharField(
        max_length=20,
        choices=TIPO_PRESTAMO_CHOICES
    )

    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="activo"
    )

    observaciones = models.TextField(blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Si no se define fecha_fin, se asigna automáticamente +7 días
        if not self.fecha_fin:
            self.fecha_fin = self.fecha_inicio + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.activo} - {self.responsable_nombre} ({self.estado})"
    
@property
def estado_calculado(self):
    if self.estado in ["finalizado", "cancelado"]:
        return self.estado

    if self.fecha_fin < timezone.now().date():
        return "vencido"

    return "activo"


@property
def dias_restantes(self):
    return (self.fecha_fin - timezone.now().date()).days