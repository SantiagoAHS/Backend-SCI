from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TipoActivo, Activo
from .serializers import TipoActivoSerializer, ActivoCreateSerializer, ActivoListSerializer
from rest_framework.views import APIView
from django.db.models import Count

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

class ActivoDeleteView(generics.DestroyAPIView):
    queryset = Activo.objects.all()
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        instance = self.get_object()
        instance.delete()  # eliminación física real

        return Response(
            {"detail": "Activo eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
    
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Total activos
        total_activos = Activo.objects.count()

        # Conteo por estado (usando tus choices reales)
        activos_por_estado = (
            Activo.objects
            .values("estado")
            .annotate(total=Count("id"))
        )

        # Conteo por tipo de activo
        activos_por_tipo = (
            Activo.objects
            .values("tipo_activo__nombre")
            .annotate(total=Count("id"))
        )

        # KPIs específicos
        asignados = Activo.objects.filter(estado="asignado").count()
        mantenimiento = Activo.objects.filter(estado="mantenimiento").count()
        baja = Activo.objects.filter(estado="baja").count()
        disponibles = Activo.objects.filter(estado="disponible").count()

        return Response({
            "kpis": {
                "total": total_activos,
                "asignados": asignados,
                "mantenimiento": mantenimiento,
                "baja": baja,
                "disponibles": disponibles
            },
            "por_estado": list(activos_por_estado),
            "por_tipo": list(activos_por_tipo),
        })