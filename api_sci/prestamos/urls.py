from django.urls import path
from .views import PrestamoCreateView, PrestamoListView, FinalizarPrestamoView, NotificacionesPrestamosView, ReportePrestamosPDFView

urlpatterns = [
    path("prestamo/", PrestamoCreateView.as_view(), name="prestamo-create"),
    path("prestamos/list/", PrestamoListView.as_view(), name="prestamo-list"),
    path("prestamos/<int:pk>/finalizar/", FinalizarPrestamoView.as_view(), name="finalizar-prestamo"),
    path("prestamos/notificaciones/",NotificacionesPrestamosView.as_view(),name="prestamos-notificaciones"),
    path("reportes/prestamos/pdf/", ReportePrestamosPDFView.as_view(), name="reporte-prestamos-pdf"),
]