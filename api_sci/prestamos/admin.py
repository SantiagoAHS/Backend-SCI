from django.contrib import admin
from .models import Prestamo


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "activo",
        "responsable_nombre",
        "tipo_prestamo",
        "estado",
        "fecha_inicio",
        "fecha_fin",
    )

    list_filter = (
        "estado",
        "tipo_prestamo",
        "fecha_inicio",
    )

    search_fields = (
        "responsable_nombre",
        "activo__nombre",
    )

    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )

    ordering = ("-creado_en",)

    fieldsets = (
        ("Información del Préstamo", {
            "fields": (
                "activo",
                "tipo_prestamo",
                "estado",
            )
        }),
        ("Responsable", {
            "fields": (
                "responsable_nombre",
                "responsable_telefono",
                "area",
            )
        }),
        ("Fechas", {
            "fields": (
                "fecha_inicio",
                "fecha_fin",
            )
        }),
        ("Información adicional", {
            "fields": (
                "observaciones",
                "creado_en",
                "actualizado_en",
            )
        }),
    )