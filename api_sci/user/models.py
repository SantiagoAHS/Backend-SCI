from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    ROLES = (
        ('admin', 'Administrador'),
        ('operativo', 'Operativo'),
        ('auditor', 'Auditor'),
    )

    numero_empleado = models.CharField(max_length=20, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES)

    telefono = models.CharField(max_length=15, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)

    fecha_ingreso = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} - {self.numero_empleado}"
