from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Mantenimiento
from .serializers import MantenimientoPreventivoSerializer, CambiarEstadoMantenimientoSerializer, MantenimientoListSerializer, EditarMantenimientoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404
from .services import generar_mantenimientos_preventivos
from django.http import HttpResponse
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

class EditarMantenimientoView(UpdateAPIView):
    queryset = Mantenimiento.objects.all()
    serializer_class = EditarMantenimientoSerializer
    lookup_field = "id"
    parser_classes = [MultiPartParser, FormParser]

class ReporteMantenimientosExcelView(APIView):

    def get(self, request):

        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")

        mantenimientos = Mantenimiento.objects.all()

        if fecha_inicio and fecha_fin:
            mantenimientos = mantenimientos.filter(
                fecha_ingreso__range=[fecha_inicio, fecha_fin]
            )

        # Crear archivo Excel
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Mantenimientos"

        # Encabezados
        sheet.append([
            "Activo",
            "Tipo",
            "Estado",
            "Fecha ingreso",
            "Fecha finalización",
            "Responsable",
            "Costo",
            "Descripción problema",
            "Acciones realizadas"
        ])

        # Datos
        for m in mantenimientos:
            sheet.append([
                m.activo.nombre,
                m.tipo,
                m.estado,
                m.fecha_ingreso,
                m.fecha_finalizacion,
                m.responsable,
                m.costo,
                m.descripcion_problema,
                m.acciones_realizadas
            ])

        # Crear respuesta
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = "attachment; filename=reporte_mantenimientos.xlsx"

        workbook.save(response)

        return response
    
class ReporteMantenimientosPDFView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        mantenimientos = Mantenimiento.objects.all()

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=reporte_mantenimientos.pdf"

        p = canvas.Canvas(response, pagesize=letter)

        y = 750

        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, y, "Reporte de Mantenimientos")

        y -= 40

        p.setFont("Helvetica-Bold", 10)

        headers = [
            "Activo",
            "Tipo",
            "Estado",
            "Fecha ingreso",
            "Responsable",
            "Costo"
        ]

        x_positions = [40, 150, 230, 320, 420, 520]

        for i, header in enumerate(headers):
            p.drawString(x_positions[i], y, header)

        y -= 20
        p.setFont("Helvetica", 9)

        for m in mantenimientos:

            p.drawString(40, y, str(m.activo.nombre))
            p.drawString(150, y, str(m.tipo))
            p.drawString(230, y, str(m.estado))
            p.drawString(320, y, str(m.fecha_ingreso))
            p.drawString(420, y, str(m.responsable))
            p.drawString(520, y, str(m.costo))

            y -= 20

            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 9)
                y = 750

        p.save()

        return response