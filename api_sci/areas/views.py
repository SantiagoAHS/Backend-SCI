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

        serializer = AreaSerializer(data=request.data)

        if serializer.is_valid():
            area = serializer.save()
            return Response(
                AreaSerializer(area).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AreaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        areas = Area.objects.all().order_by("id")
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

