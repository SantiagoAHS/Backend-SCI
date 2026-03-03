from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Prestamo
from .serializers import PrestamoCreateSerializer, PrestamoListSerializer
from .utils import actualizar_prestamos_vencidos
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class PrestamoCreateView(CreateAPIView):
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoCreateSerializer
    permission_classes = [IsAuthenticated]

class PrestamoListView(ListAPIView):
    queryset = Prestamo.objects.all().order_by("-creado_en")
    serializer_class = PrestamoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        actualizar_prestamos_vencidos()  
        return Prestamo.objects.all().order_by("-creado_en")
    
class FinalizarPrestamoView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        prestamo = get_object_or_404(Prestamo, pk=pk)

        # No permitir finalizar si ya está finalizado o cancelado
        if prestamo.estado in ["finalizado", "cancelado"]:
            return Response(
                {"detail": "Este préstamo ya fue cerrado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cambiar estado del préstamo
        prestamo.estado = "finalizado"
        prestamo.save()

        # Liberar activo
        activo = prestamo.activo
        activo.estado = "disponible"
        activo.save()

        return Response(
            {"detail": "Préstamo finalizado correctamente."},
            status=status.HTTP_200_OK
        )