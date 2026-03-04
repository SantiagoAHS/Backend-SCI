from django.contrib import admin
from .models import Mantenimiento


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "activo",
        "tipo",
        "estado",
        "fecha_ingreso",
        "responsable",
        "costo",
    )
    list_filter = ("tipo", "estado", "fecha_ingreso")
    search_fields = ("activo__nombre", "responsable")