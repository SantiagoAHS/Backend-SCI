from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime, timedelta
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from .models import Mantenimiento
from .serializers import (
    MantenimientoPreventivoSerializer,
    CambiarEstadoMantenimientoSerializer,
    MantenimientoListSerializer,
    EditarMantenimientoSerializer
)
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

        fecha_inicio = request.GET.get("fecha_inicio")
        fecha_fin = request.GET.get("fecha_fin")

        mantenimientos = Mantenimiento.objects.select_related("activo").all()

        # Filtros
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            mantenimientos = mantenimientos.filter(fecha_ingreso__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)
            mantenimientos = mantenimientos.filter(fecha_ingreso__lt=fecha_fin)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=reporte_mantenimientos.pdf"

        doc = SimpleDocTemplate(
            response,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        elements = []
        styles = getSampleStyleSheet()

        # Estilos
        title_style = ParagraphStyle(
            name="TitleStyle",
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=22
        )

        subtitle_style = ParagraphStyle(
            name="SubTitleStyle",
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=15
        )

        logo_style = ParagraphStyle(
            name="LogoStyle",
            fontSize=10,
            alignment=TA_RIGHT
        )

        # Encabezado
        header_data = [
            [
                Paragraph("REPORTE DE MANTENIMIENTOS", title_style),
                Paragraph("LOGO", logo_style)
            ]
        ]

        header_table = Table(header_data, colWidths=[400, 100])
        elements.append(header_table)

        # Mostrar filtros
        if fecha_inicio or fecha_fin:
            rango = f"Desde: {fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '---'}  |  Hasta: {fecha_fin.strftime('%Y-%m-%d') if fecha_fin else '---'}"
            elements.append(Paragraph(rango, subtitle_style))

        elements.append(Spacer(1, 10))

        # Tabla
        data = [[
            "Activo",
            "Tipo",
            "Estado",
            "Fecha ingreso",
            "Responsable",
            "Costo"
        ]]

        for m in mantenimientos:
            data.append([
                m.activo.nombre if m.activo else "",
                m.tipo or "",
                m.estado or "",
                m.fecha_ingreso.strftime("%Y-%m-%d") if m.fecha_ingreso else "",
                m.responsable or "",
                f"${m.costo}" if m.costo else "$0",
            ])

        table = Table(data, repeatRows=1)

        # Estilo profesional
        table.setStyle(TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#145a32")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            # Filas
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            # Padding
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
        ]))

        elements.append(table)

        doc.build(elements)

        return response