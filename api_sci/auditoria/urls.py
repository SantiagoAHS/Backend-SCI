from django.urls import path
from .views import (
    iniciar_auditoria,
    AuditoriaDetailView,
    DetalleAuditoriaUpdateView,
    AuditoriaListView,
    finalizar_auditoria,
    iniciar_auditoria_area,
    iniciar_auditoria_tipo
)

urlpatterns = [
    path("auditoria/iniciar/", iniciar_auditoria, name="iniciar_auditoria"),
    path("auditoria/iniciar/area/", iniciar_auditoria_area, name="iniciar_auditoria_area"),
    path("auditoria/<int:pk>/", AuditoriaDetailView.as_view(), name="auditoria_detalle"),
    path("auditoria/detalle/<int:pk>/", DetalleAuditoriaUpdateView.as_view(), name="detalle_update"),
    path("auditorias/list/", AuditoriaListView.as_view(), name="auditoria_list"),
    path("auditoria/finalizar/<int:pk>/", finalizar_auditoria),
    path("auditoria/iniciar/tipo/", iniciar_auditoria_tipo, name="iniciar_auditoria_tipo"),
]