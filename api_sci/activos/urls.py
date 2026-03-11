from django.urls import path
from .views import TipoActivoListCreateView, ActivoCreateView, TipoActivoDeleteView, ActivoListView, ActivoDeleteView, DashboardStatsView, ReporteActivosExcelView, ReporteActivosPDFView

urlpatterns = [
    path('tipos-activo/', TipoActivoListCreateView.as_view(), name='tipos-activo'),
    path('tipos-activo/<int:pk>/', TipoActivoDeleteView.as_view(), name='tipo-activo-delete'),
    path('activos/', ActivoCreateView.as_view(), name='crear-activo'),
    path('activos/list/', ActivoListView.as_view(), name='activo-list'),
    path('activos/<int:pk>/delete/', ActivoDeleteView.as_view(), name='activo-delete'),
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("reportes/activos/excel/",ReporteActivosExcelView.as_view()),
    path("reportes/activos/pdf/",ReporteActivosPDFView.as_view()),
]