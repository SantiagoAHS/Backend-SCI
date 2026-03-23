from django.urls import path
from .views import (
    iniciar_auditoria,
    AuditoriaDetailView,
    DetalleAuditoriaUpdateView,
    AuditoriaListView,
    finalizar_auditoria,
)

urlpatterns = [
    path("auditoria/iniciar/", iniciar_auditoria, name="iniciar_auditoria"),
    path("auditoria/<int:pk>/", AuditoriaDetailView.as_view(), name="auditoria_detalle"),
    path("auditoria/detalle/<int:pk>/", DetalleAuditoriaUpdateView.as_view(), name="detalle_update"),
    path("auditorias/list/", AuditoriaListView.as_view(), name="auditoria_list"),
    path("auditoria/finalizar/<int:pk>/", finalizar_auditoria),
]