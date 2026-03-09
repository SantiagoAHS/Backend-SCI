from django.urls import path
from .views import MantenimientoPreventivoCreateView, CambiarEstadoMantenimientoView, GenerarPreventivosAutomaticosView, MantenimientoListView, EditarMantenimientoView

urlpatterns = [
    path("preventivo/", MantenimientoPreventivoCreateView.as_view(), name="mantenimiento-preventivo"),
    path("mantenimientos/<int:pk>/estado/", CambiarEstadoMantenimientoView.as_view(), name="cambiar-estado-mantenimiento"),
    path("generar-preventivos/", GenerarPreventivosAutomaticosView.as_view()),
    path("mantenimientos/list/", MantenimientoListView.as_view()),
    path("mantenimientos/<int:id>/editar/",EditarMantenimientoView.as_view(),name="editar_mantenimiento"),

]