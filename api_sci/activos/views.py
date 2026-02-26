from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import TipoActivo, Activo
from .serializers import TipoActivoSerializer , ActivoCreateSerializer, ActivoListSerializer
from rest_framework.response import Response
from rest_framework import status


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

class TipoActivoDeleteView(generics.DestroyAPIView):
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Solo permite desactivar los que están activos
        return TipoActivo.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Soft delete
        instance.activo = False
        instance.save()

        return Response(
            {"detail": "Tipo de activo desactivado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
    
class ActivoListView(generics.ListAPIView):
    queryset = Activo.objects.all()
    serializer_class = ActivoListSerializer