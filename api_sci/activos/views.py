from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from datetime import datetime
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from django.db.models import Count
from django.http import HttpResponse

import openpyxl
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter
import json


from .models import TipoActivo, Activo, Caracteristica, OpcionCaracteristica, ValorCaracteristica
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

# 🔹 Crear activo con validación de características
class ActivoCreateView(generics.CreateAPIView):

    queryset = Activo.objects.all()
    serializer_class = ActivoCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        data = request.data.copy()

        valores = data.get("valores")

        # 🔹 convertir JSON string a lista
        if isinstance(valores, str):
            valores = json.loads(valores)

        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # 🔹 VALIDAR TODO ANTES DE GUARDAR
        if valores:

            for v in valores:

                caracteristica = Caracteristica.objects.get(
                    id=int(v["caracteristica"])
                )

                valor_texto = v.get("valor_texto")
                opcion = None

                tipo = caracteristica.tipo_dato
                tamano = caracteristica.tamano

                # 🔹 TEXTO
                if tipo == "text":

                    if valor_texto is None:
                        continue

                    if tamano and len(valor_texto) > tamano:
                        return Response(
                            {
                                "error": f"{caracteristica.nombre} excede el tamaño máximo ({tamano})."
                            },
                            status=400
                        )

                # 🔹 ENTERO
                elif tipo == "int":

                    try:
                        int(valor_texto)
                    except:
                        return Response(
                            {
                                "error": f"{caracteristica.nombre} debe ser un número entero."
                            },
                            status=400
                        )

                    if tamano and len(str(valor_texto)) > tamano:
                        return Response(
                            {
                                "error": f"{caracteristica.nombre} excede {tamano} dígitos."
                            },
                            status=400
                        )

                # 🔹 DECIMAL
                elif tipo == "float":

                    try:
                        float(valor_texto)
                    except:
                        return Response(
                            {
                                "error": f"{caracteristica.nombre} debe ser un número decimal."
                            },
                            status=400
                        )

                    if tamano and len(str(valor_texto).replace(".", "")) > tamano:
                        return Response(
                            {
                                "error": f"{caracteristica.nombre} excede {tamano} dígitos."
                            },
                            status=400
                        )

                # 🔹 FECHA
                elif tipo == "date":

                    if not valor_texto:
                        return Response(
                            {"error": f"{caracteristica.nombre} requiere una fecha."},
                            status=400
                        )

                    try:
                        fecha = str(valor_texto).strip()

                        # si viene con hora
                        if "T" in fecha:
                            fecha = fecha.split("T")[0]

                        datetime.strptime(fecha, "%Y-%m-%d")

                        # 🔹 guardar fecha limpia
                        v["valor_texto"] = fecha

                    except ValueError:
                        return Response(
                            {
                                "error": f"{caracteristica.nombre} debe ser una fecha válida (YYYY-MM-DD)."
                            },
                            status=400
                        )

                # 🔹 BOOLEANO
                elif tipo == "boolean":

                    if str(valor_texto).lower() not in ["true", "false", "1", "0"]:
                        return Response(
                            {
                                "error": f"{caracteristica.nombre} debe ser verdadero o falso."
                            },
                            status=400
                        )

                # 🔹 SELECT
                elif tipo == "select":

                    if v.get("opcion"):

                        opcion = OpcionCaracteristica.objects.get(
                            id=int(v["opcion"])
                        )

                        if opcion.caracteristica.id != caracteristica.id:
                            return Response(
                                {
                                    "error": f"Opción inválida para {caracteristica.nombre}."
                                },
                                status=400
                            )

                    else:
                        return Response(
                            {
                                "error": f"Debes seleccionar una opción para {caracteristica.nombre}."
                            },
                            status=400
                        )

        # 🔹 GUARDAR SOLO SI TODO ES VÁLIDO
        with transaction.atomic():

            activo = serializer.save()

            if valores:

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
    
# 🔹 Listar activos disponibles
class ActivoDisponibleListView(generics.ListAPIView):

    serializer_class = ActivoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activo.objects.select_related(
            "tipo_activo",
            "area"
        ).prefetch_related(
            "valores__caracteristica",
            "valores__opcion"
        ).filter(
            estado='disponible'
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

        fecha_inicio = request.GET.get("fecha_inicio")
        fecha_fin = request.GET.get("fecha_fin")

        activos = Activo.objects.select_related(
            "tipo_activo",
            "area"
        ).all()

        # Filtro por fechas
        if fecha_inicio and fecha_fin:
            activos = activos.filter(
                fecha_registro__date__range=[fecha_inicio, fecha_fin]
            )

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
    
    
class ReporteActivosPorAreaPDFView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, area_id):

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=reporte_activos_area.pdf"

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
        ).filter(area_id=area_id)  # FILTRO

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

class ActivoDetailView(RetrieveAPIView):
    queryset = Activo.objects.all()
    serializer_class = ActivoListSerializer
    permission_classes = [AllowAny]


import qrcode
import zipfile
import os
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from django.conf import settings
from .models import Activo

class DescargarQRActivosView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        activos = Activo.objects.all()

        base_url = request.build_absolute_uri('/').rstrip('/')

        buffer = BytesIO()

        with zipfile.ZipFile(buffer, "w") as zip_file:

            for activo in activos:

                url = f"{settings.FRONTEND_URL}/activos/{activo.id}"

                qr = qrcode.make(url)

                img_buffer = BytesIO()
                qr.save(img_buffer, format="PNG")

                file_name = f"activo_{activo.id}.png"

                zip_file.writestr(file_name, img_buffer.getvalue())

        buffer.seek(0)

        response = HttpResponse(buffer, content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=qr_activos.zip"

        return response
    
