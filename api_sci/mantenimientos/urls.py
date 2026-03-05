from django.urls import path
from .views import MantenimientoPreventivoCreateView, CambiarEstadoMantenimientoView, GenerarPreventivosAutomaticosView

urlpatterns = [
    path("preventivo/", MantenimientoPreventivoCreateView.as_view(), name="mantenimiento-preventivo"),
    path("mantenimientos/<int:pk>/estado/", CambiarEstadoMantenimientoView.as_view(), name="cambiar-estado-mantenimiento"),
    path("generar-preventivos/", GenerarPreventivosAutomaticosView.as_view()),
]