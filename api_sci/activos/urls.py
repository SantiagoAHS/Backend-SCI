from django.urls import path
from .views import TipoActivoListCreateView, ActivoCreateView, TipoActivoDeleteView, ActivoListView

urlpatterns = [
    path('tipos-activo/', TipoActivoListCreateView.as_view(), name='tipos-activo'),
    path('tipos-activo/<int:pk>/', TipoActivoDeleteView.as_view(), name='tipo-activo-delete'),
    path('activos/', ActivoCreateView.as_view(), name='crear-activo'),
    path('activos/list/', ActivoListView.as_view(), name='activo-list'),
]