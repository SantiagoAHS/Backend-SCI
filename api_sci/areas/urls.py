from django.urls import path
from .views import AreaCreateView, AreaListView, AreaUpdateView, AreaDeleteView

urlpatterns = [
    path("areas/", AreaCreateView.as_view(), name="area-create"),
    path("areas/list/", AreaListView.as_view(), name="area-list"),
    path("areas/<int:pk>/", AreaUpdateView.as_view(), name="area-update"),
    path("areas/<int:pk>/delete/", AreaDeleteView.as_view(), name="area-delete"),
]
