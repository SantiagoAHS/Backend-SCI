from django.urls import path
from .views import (
    iniciar_auditoria,
    iniciar_auditoria_area,
    iniciar_auditoria_tipo,
    finalizar_auditoria,
    generar_pdf_auditoria,
    AuditoriaDetailView,
    DetalleAuditoriaUpdateView,
    AuditoriaListView
)

urlpatterns = [

    # ==============================
    # INICIO DE AUDITORÍAS
    # ==============================
    path("auditoria/iniciar/", iniciar_auditoria, name="iniciar_auditoria"),
    path("auditoria/iniciar/area/", iniciar_auditoria_area, name="iniciar_auditoria_area"),
    path("auditoria/iniciar/tipo/", iniciar_auditoria_tipo, name="iniciar_auditoria_tipo"),

    # ==============================
    # GESTIÓN DE AUDITORÍAS
    # ==============================
    path("auditoria/<int:pk>/", AuditoriaDetailView.as_view(), name="auditoria_detalle"),
    path("auditoria/detalle/<int:pk>/", DetalleAuditoriaUpdateView.as_view(), name="detalle_update"),
    path("auditorias/list/", AuditoriaListView.as_view(), name="auditoria_list"),

    # ==============================
    # FINALIZACIÓN
    # ==============================
    path("auditoria/finalizar/<int:pk>/", finalizar_auditoria),

    # ==============================
    # REPORTES
    # ==============================
    path("auditoria/<int:pk>/pdf/", generar_pdf_auditoria),
]