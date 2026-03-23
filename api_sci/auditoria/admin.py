from django.contrib import admin
from .models import Auditoria, DetalleAuditoria


# 🔹 Inline para ver detalles dentro de la auditoría
class DetalleAuditoriaInline(admin.TabularInline):
    model = DetalleAuditoria
    extra = 0
    readonly_fields = (
        "activo",
        "estado_sistema",
        "area_sistema",
        "estado_real",
        "area_real",
        "resultado",
        "encontrado",
    )


# 🔹 Auditoría
@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "responsable", "estado", "fecha_inicio", "fecha_fin")
    list_filter = ("estado", "fecha_inicio")
    search_fields = ("nombre", "responsable")
    inlines = [DetalleAuditoriaInline]


# 🔹 Detalle de auditoría
@admin.register(DetalleAuditoria)
class DetalleAuditoriaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "auditoria",
        "activo",
        "estado_sistema",
        "estado_real",
        "resultado",
        "encontrado",
    )
    list_filter = ("resultado", "encontrado")
    search_fields = ("activo__nombre",)