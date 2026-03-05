from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Mantenimiento
from .serializers import MantenimientoPreventivoSerializer, CambiarEstadoMantenimientoSerializer, MantenimientoListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .services import generar_mantenimientos_preventivos


class MantenimientoPreventivoCreateView(CreateAPIView):
    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoPreventivoSerializer
    permission_classes = [IsAuthenticated]

class CambiarEstadoMantenimientoView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        mantenimiento = get_object_or_404(Mantenimiento, pk=pk)

        serializer = CambiarEstadoMantenimientoSerializer(
            mantenimiento,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()  
            return Response(
                {"detail": "Estado actualizado correctamente."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GenerarPreventivosAutomaticosView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        generar_mantenimientos_preventivos()

        return Response({
            "mensaje": "Mantenimientos preventivos generados correctamente"
        })
    
class MantenimientoListView(ListAPIView):
    queryset = Mantenimiento.objects.all().select_related("activo")
    serializer_class = MantenimientoListSerializer
    permission_classes = [IsAuthenticated]