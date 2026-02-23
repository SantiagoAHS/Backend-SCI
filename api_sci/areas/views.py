from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Area
from .serializers import AreaSerializer
from django.shortcuts import get_object_or_404

class AreaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # 🔐 Solo admin puede crear áreas
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        nombre = request.data.get("nombre", "").strip()

        if not nombre:
            return Response(
                {"error": "El nombre es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔎 Buscar ignorando mayúsculas/minúsculas
        area_existente = Area.objects.filter(nombre__iexact=nombre).first()

        if area_existente:

            # ♻️ Si existe pero está inactiva → reactivar
            if not area_existente.activo:
                area_existente.activo = True
                area_existente.descripcion = request.data.get("descripcion")
                area_existente.responsable_id = request.data.get("responsable")
                area_existente.save()

                return Response(
                    {
                        "message": "Área reactivada correctamente",
                        "data": AreaSerializer(area_existente).data
                    },
                    status=status.HTTP_200_OK
                )

            # ❌ Si ya está activa
            return Response(
                {"error": "Ya existe un área con ese nombre"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Si no existe → crear normal
        serializer = AreaSerializer(data=request.data)

        if serializer.is_valid():
            area = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AreaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        solo_activas = request.query_params.get("activas")

        if solo_activas == "false":
            areas = Area.objects.all().order_by("id")
        else:
            areas = Area.objects.filter(activo=True).order_by("id")

        serializer = AreaSerializer(areas, many=True)
        return Response(serializer.data)

class AreaUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        # 🔐 Solo admin puede editar
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        area = get_object_or_404(Area, pk=pk)

        serializer = AreaSerializer(
            area,
            data=request.data,
            partial=True  # permite actualizar solo campos enviados
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AreaDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        # 🔐 Solo admin puede eliminar
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        area = get_object_or_404(Area, pk=pk)

        # 🔄 Soft delete
        area.activo = False
        area.save()

        return Response(
            {"message": "Área desactivada correctamente"},
            status=status.HTTP_200_OK
        )

