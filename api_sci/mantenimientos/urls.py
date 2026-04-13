from django.urls import path
from .views import (
    MantenimientoPreventivoCreateView,
    CambiarEstadoMantenimientoView,
    GenerarPreventivosAutomaticosView,
    MantenimientoListView,
    EditarMantenimientoView,
    ReporteMantenimientosExcelView,
    ReporteMantenimientosPDFView
)

urlpatterns = [

    # ==============================
    # GESTIÓN DE MANTENIMIENTOS
    # ==============================
    path("preventivo/", MantenimientoPreventivoCreateView.as_view(), name="mantenimiento-preventivo"),
    path("mantenimientos/list/", MantenimientoListView.as_view()),
    path("mantenimientos/<int:id>/editar/", EditarMantenimientoView.as_view(), name="editar_mantenimiento"),
    path("mantenimientos/<int:pk>/estado/", CambiarEstadoMantenimientoView.as_view(), name="cambiar-estado-mantenimiento"),

    # ==============================
    # AUTOMATIZACIÓN
    # ==============================
    path("generar-preventivos/", GenerarPreventivosAutomaticosView.as_view()),

    # ==============================
    # REPORTES
    # ==============================
    path("reportes/mantenimientos/excel/", ReporteMantenimientosExcelView.as_view()),
    path("reportes/mantenimientos/pdf/", ReporteMantenimientosPDFView.as_view()),
]