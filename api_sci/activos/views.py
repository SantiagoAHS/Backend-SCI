from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TipoActivo, Activo
from .serializers import TipoActivoSerializer, ActivoCreateSerializer, ActivoListSerializer

# Solo admin puede crear
class TipoActivoCreateView(generics.CreateAPIView):
    queryset = TipoActivo.objects.all()
    serializer_class = TipoActivoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.rol != "admin":
            raise Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class TipoActivoListCreateView(generics.ListCreateAPIView):
    queryset = TipoActivo.objects.all()
    serializer_class = TipoActivoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.rol != "admin":
            raise Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class ActivoCreateView(generics.CreateAPIView):
    queryset = Activo.objects.all()
    serializer_class = ActivoCreateSerializer
    permission_classes = [IsAuthenticated]  # solo usuarios autenticados

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activo = serializer.save()

        # Serializamos el activo recién creado con ActivoListSerializer
        return Response(
            ActivoListSerializer(activo).data,
            status=status.HTTP_201_CREATED
        )

class TipoActivoDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TipoActivo.objects.all()

    def destroy(self, request, *args, **kwargs):
        if request.user.rol != "admin":
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(
            {"detail": "Tipo de activo desactivado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )


class ActivoListView(generics.ListAPIView):
    queryset = Activo.objects.all()
    serializer_class = ActivoListSerializer
    permission_classes = [IsAuthenticated]