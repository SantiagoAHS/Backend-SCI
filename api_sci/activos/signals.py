from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Activo, Caracteristica, ValorCaracteristica


# 🔹 Cuando se guarda un Activo
@receiver(post_save, sender=Activo)
def sincronizar_caracteristicas_activo(sender, instance, **kwargs):

    caracteristicas = Caracteristica.objects.filter(
        tipo_activo=instance.tipo_activo
    )

    for caracteristica in caracteristicas:
        ValorCaracteristica.objects.get_or_create(
            activo=instance,
            caracteristica=caracteristica
        )

# 🔹 Cuando se crea una nueva Caracteristica
@receiver(post_save, sender=Caracteristica)
def agregar_nueva_caracteristica_a_activos(sender, instance, created, **kwargs):

    if created:
        activos = Activo.objects.filter(
            tipo_activo=instance.tipo_activo
        )

        for activo in activos:
            ValorCaracteristica.objects.get_or_create(
                activo=activo,
                caracteristica=instance
            )