from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

class User(AbstractUser):

    ROLES = (
        ('admin', 'Administrador'),
        ('operativo', 'Operativo'),
        ('auditor', 'Auditor'),
    )

    numero_empleado = models.CharField(max_length=20, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES)

    # Email opcional pero único
    email = models.EmailField(unique=True, blank=True, null=True)

    # Verificación de correo
    email_verified = models.BooleanField(default=False)

    telefono = models.CharField(max_length=15, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)

    fecha_ingreso = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} - {self.numero_empleado}"
    
class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(hours=24)


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(hours=1)