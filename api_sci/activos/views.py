from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from django.db.models import Count
from django.http import HttpResponse

import openpyxl
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter
import json


from .models import TipoActivo, Activo
from .serializers import (
    TipoActivoSerializer,
    ActivoCreateSerializer,
    ActivoListSerializer
)


# 🔹 Listar y crear tipos de activo
class TipoActivoListCreateView(generics.ListCreateAPIView):
    queryset = TipoActivo.objects.all()
    serializer_class = TipoActivoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.rol != "admin":
            raise PermissionDenied("No autorizado")
        serializer.save()

# 🔹 Crear activo con características dinámicas
class ActivoCreateView(generics.CreateAPIView):
    queryset = Activo.objects.all()
    serializer_class = ActivoCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        data = request.data.copy()

        valores = data.get("valores")

        # 🔹 convertir JSON string a lista real
        if isinstance(valores, str):
            valores = json.loads(valores)

        print("VALORES ENVIADOS A SERIALIZER:", valores)

        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            print("ERRORES SERIALIZER:", serializer.errors)
            return Response(serializer.errors, status=400)

        # 🔹 guardar activo primero
        activo = serializer.save()

        # 🔹 guardar características manualmente
        if valores:
            from .models import Caracteristica, OpcionCaracteristica, ValorCaracteristica

            for v in valores:

                caracteristica = Caracteristica.objects.get(
                    id=int(v["caracteristica"])
                )

                opcion = None

                if v.get("opcion"):
                    opcion = OpcionCaracteristica.objects.get(
                        id=int(v["opcion"])
                    )

                ValorCaracteristica.objects.create(
                    activo=activo,
                    caracteristica=caracteristica,
                    valor_texto=v.get("valor_texto"),
                    opcion=opcion
                )

        return Response(
            ActivoListSerializer(activo).data,
            status=status.HTTP_201_CREATED
        )
    
# 🔹 Desactivar tipo de activo
class TipoActivoDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TipoActivo.objects.all()

    def destroy(self, request, *args, **kwargs):

        if request.user.rol != "admin":
            raise PermissionDenied("No autorizado")

        instance = self.get_object()
        instance.activo = False
        instance.save()

        return Response(
            {"detail": "Tipo de activo desactivado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )


# 🔹 Listar activos
class ActivoListView(generics.ListAPIView):

    serializer_class = ActivoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activo.objects.select_related(
            "tipo_activo",
            "area"
        ).prefetch_related(
            "valores__caracteristica",
            "valores__opcion"
        )


# 🔹 Eliminar activo
class ActivoDeleteView(generics.DestroyAPIView):

    queryset = Activo.objects.all()
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):

        if request.user.rol != "admin":
            raise PermissionDenied("No autorizado")

        instance = self.get_object()
        instance.delete()

        return Response(
            {"detail": "Activo eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )


# 🔹 Dashboard
class DashboardStatsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        total_activos = Activo.objects.count()

        activos_por_estado = (
            Activo.objects
            .values("estado")
            .annotate(total=Count("id"))
        )

        activos_por_tipo = (
            Activo.objects
            .values("tipo_activo__nombre")
            .annotate(total=Count("id"))
        )

        return Response({
            "kpis": {
                "total": total_activos,
                "asignados": Activo.objects.filter(estado="asignado").count(),
                "mantenimiento": Activo.objects.filter(estado="mantenimiento").count(),
                "baja": Activo.objects.filter(estado="baja").count(),
                "disponibles": Activo.objects.filter(estado="disponible").count(),
            },
            "por_estado": list(activos_por_estado),
            "por_tipo": list(activos_por_tipo),
        })


# 🔹 Reporte Excel
class ReporteActivosExcelView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Activos"

        headers = [
            "ID",
            "Nombre",
            "Tipo",
            "Area",
            "Estado",
            "Frecuencia Mantenimiento",
            "Fecha Registro",
        ]

        ws.append(headers)

        activos = Activo.objects.select_related(
            "tipo_activo",
            "area"
        ).all()

        for a in activos:
            ws.append([
                a.id,
                a.nombre,
                a.tipo_activo.nombre,
                a.area.nombre,
                a.estado,
                a.frecuencia_mantenimiento,
                a.fecha_registro.strftime("%Y-%m-%d"),
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = "attachment; filename=reporte_activos.xlsx"

        wb.save(response)

        return response


# 🔹 Reporte PDF
class ReporteActivosPDFView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=reporte_activos.pdf"

        doc = SimpleDocTemplate(response, pagesize=letter)

        data = [[
            "ID",
            "Nombre",
            "Tipo",
            "Area",
            "Estado",
            "Frecuencia Mant.",
            "Fecha Registro"
        ]]

        activos = Activo.objects.select_related(
            "tipo_activo",
            "area"
        ).all()

        for a in activos:
            data.append([
                a.id,
                a.nombre,
                a.tipo_activo.nombre,
                a.area.nombre,
                a.estado,
                a.frecuencia_mantenimiento,
                a.fecha_registro.strftime("%Y-%m-%d"),
            ])

        table = Table(data)

        doc.build([table])

        return response