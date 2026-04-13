from django.urls import path
from .views import (
    TipoActivoListCreateView,
    TipoActivoDeleteView,
    ActivoCreateView,
    ActivoListView,
    ActivoDisponibleListView,
    ActivoDeleteView,
    ActivoDetailView,
    DashboardStatsView,
    ReporteActivosExcelView,
    ReporteActivosPDFView,
    ReporteActivosPorAreaPDFView,
    DescargarQRActivosView
)

urlpatterns = [

    # ==============================
    # TIPOS DE ACTIVOS
    # ==============================
    path('tipos-activo/', TipoActivoListCreateView.as_view(), name='tipos-activo'),
    path('tipos-activo/<int:pk>/', TipoActivoDeleteView.as_view(), name='tipo-activo-delete'),

    # ==============================
    # GESTIÓN DE ACTIVOS
    # ==============================
    path('activos/', ActivoCreateView.as_view(), name='crear-activo'),
    path('activos/list/', ActivoListView.as_view(), name='activo-list'),
    path('activos/disponibles/', ActivoDisponibleListView.as_view(), name='activo-disponible-list'),
    path('activos/<int:pk>/', ActivoDetailView.as_view(), name='activo-detail'),
    path('activos/<int:pk>/delete/', ActivoDeleteView.as_view(), name='activo-delete'),

    # ==============================
    # DASHBOARD
    # ==============================
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),

    # ==============================
    # REPORTES
    # ==============================
    path("reportes/activos/excel/", ReporteActivosExcelView.as_view()),
    path("reportes/activos/pdf/", ReporteActivosPDFView.as_view()),
    path("reporte/activos/area/<int:area_id>/", ReporteActivosPorAreaPDFView.as_view()),

    # ==============================
    # CÓDIGOS QR
    # ==============================
    path("activos/qr/descargar/", DescargarQRActivosView.as_view()),
]