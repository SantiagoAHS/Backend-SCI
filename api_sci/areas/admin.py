from django.contrib import admin
from .models import Area


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
        'responsable',
        'activo',
    )

    list_filter = (
        'activo',
    )

    search_fields = (
        'nombre',
    )

    autocomplete_fields = (
        'responsable',
    )
