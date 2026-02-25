from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import TipoActivo, Activo
from .serializers import TipoActivoSerializer , ActivoCreateSerializer

class TipoActivoCreateView(generics.CreateAPIView):
    queryset = TipoActivo.objects.all()
    serializer_class = TipoActivoSerializer
    permission_classes = [AllowAny]

class TipoActivoListCreateView(generics.ListCreateAPIView):
    queryset = TipoActivo.objects.all()
    serializer_class = TipoActivoSerializer



class ActivoCreateView(generics.CreateAPIView):
    queryset = Activo.objects.all()
    serializer_class = ActivoCreateSerializer