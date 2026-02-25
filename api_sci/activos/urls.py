from django.urls import path
from .views import TipoActivoListCreateView, ActivoCreateView

urlpatterns = [
    path('tipos-activo/', TipoActivoListCreateView.as_view(), name='tipos-activo'),
    path('activos/', ActivoCreateView.as_view(), name='crear-activo'),
]