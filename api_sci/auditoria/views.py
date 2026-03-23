from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework import generics
from .serializers import AuditoriaDetalleSerializer
from .serializers import DetalleAuditoriaSerializer
from .serializers import AuditoriaSerializer

from activos.models import Activo
from .models import Auditoria, DetalleAuditoria


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def iniciar_auditoria(request):

    if request.user.rol != "admin":
        raise PermissionDenied("No autorizado")

    auditoria = Auditoria.objects.create(
        nombre=f"Auditoría {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        responsable=request.user.username,
        estado="en_proceso"
    )

    activos = Activo.objects.all()

    for activo in activos:
        DetalleAuditoria.objects.create(
            auditoria=auditoria,
            activo=activo
        )

    return Response({
        "message": "Auditoría iniciada",
        "auditoria_id": auditoria.id
    }, status=status.HTTP_201_CREATED)


class AuditoriaDetailView(generics.RetrieveAPIView):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaDetalleSerializer
    permission_classes = [IsAuthenticated]


class DetalleAuditoriaUpdateView(generics.UpdateAPIView):
    queryset = DetalleAuditoria.objects.all()
    serializer_class = DetalleAuditoriaSerializer
    permission_classes = [IsAuthenticated]

class AuditoriaListView(generics.ListAPIView):
    queryset = Auditoria.objects.all().order_by("-creado_en")
    serializer_class = AuditoriaSerializer
    permission_classes = [IsAuthenticated]

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def finalizar_auditoria(request, pk):

    if request.user.rol != "admin":
        raise PermissionDenied("No autorizado")

    try:
        auditoria = Auditoria.objects.get(pk=pk)
    except Auditoria.DoesNotExist:
        return Response({"error": "No encontrada"}, status=404)

    auditoria.estado = "finalizada"
    auditoria.fecha_fin = timezone.now()
    auditoria.save()

    return Response({"message": "Auditoría finalizada"})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def iniciar_auditoria_area(request):
    """
    Inicia una auditoría para un área específica.
    Se espera recibir en el body: {"area_id": 1}
    """
    if request.user.rol != "admin":
        raise PermissionDenied("No autorizado")

    area_id = request.data.get("area_id")
    if not area_id:
        return Response({"error": "Se requiere el ID del área"}, status=status.HTTP_400_BAD_REQUEST)

    from areas.models import Area
    try:
        area = Area.objects.get(pk=area_id)
    except Area.DoesNotExist:
        return Response({"error": "Área no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    # 🔹 Evitar duplicar "Auditoría" si el área ya lo tiene
    area_nombre = area.nombre
    if not area_nombre.lower().startswith("auditoría"):
        area_nombre = f"{area_nombre}"

    # 🔹 Crear auditoría
    auditoria = Auditoria.objects.create(
        nombre=f"Auditoría {area_nombre} {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        responsable=request.user.username,
        estado="en_proceso",
        area=area
    )

    # 🔹 Filtrar activos solo de esa área
    activos = Activo.objects.filter(area=area)

    for activo in activos:
        DetalleAuditoria.objects.create(
            auditoria=auditoria,
            activo=activo
        )

    return Response({
        "message": f"Auditoría para el área {area.nombre} iniciada",
        "auditoria_id": auditoria.id
    }, status=status.HTTP_201_CREATED)