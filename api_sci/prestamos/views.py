from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Prestamo
from .serializers import PrestamoCreateSerializer, PrestamoListSerializer
from .utils import actualizar_prestamos_vencidos
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime, timedelta


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
    
class NotificacionesPrestamosView(APIView):

    def get(self, request):

        hoy = timezone.now().date()
        limite = hoy + timedelta(days=2)

        prestamos = Prestamo.objects.exclude(
            estado__in=["finalizado", "cancelado"]
        )

        proximos = [
            p for p in prestamos
            if hoy <= p.fecha_fin <= limite
        ]

        vencidos = [
            p for p in prestamos
            if p.fecha_fin < hoy
        ]

        data = {
            "prestamos_por_vencer": [
                {
                    "id": p.id,
                    "activo": str(p.activo),
                    "responsable": p.responsable_nombre,
                    "fecha_fin": p.fecha_fin,
                    "dias_restantes": p.dias_restantes
                }
                for p in proximos
            ],
            "prestamos_vencidos": [
                {
                    "id": p.id,
                    "activo": str(p.activo),
                    "responsable": p.responsable_nombre,
                    "fecha_fin": p.fecha_fin
                }
                for p in vencidos
            ]
        }

        return Response(data)
    

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime, timedelta

class ReportePrestamosPDFView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        fecha_inicio = request.GET.get("fecha_inicio")
        fecha_fin = request.GET.get("fecha_fin")

        prestamos = Prestamo.objects.select_related("activo", "area").all()

        # 🔍 Filtros
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            prestamos = prestamos.filter(fecha_inicio__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)
            prestamos = prestamos.filter(fecha_inicio__lt=fecha_fin)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=reporte_prestamos.pdf"

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

        # 🎯 Estilos
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

        # 🧾 Header
        header_data = [
            [
                Paragraph("REPORTE DE PRÉSTAMOS", title_style),
                Paragraph("LOGO", logo_style)
            ]
        ]

        header_table = Table(header_data, colWidths=[400, 100])
        elements.append(header_table)

        # 📅 Mostrar filtros aplicados
        if fecha_inicio or fecha_fin:
            rango = f"Desde: {fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '---'}  |  Hasta: {fecha_fin.strftime('%Y-%m-%d') if fecha_fin else '---'}"
            elements.append(Paragraph(rango, subtitle_style))

        elements.append(Spacer(1, 10))

        # 📊 Tabla
        data = [[
            "Activo",
            "Responsable",
            "Área",
            "Tipo",
            "Inicio",
            "Fin",
            "Estado"
        ]]

        for p in prestamos:
            data.append([
                p.activo.nombre if p.activo else "",
                p.responsable_nombre or "",
                p.area.nombre if p.area else "N/A",
                p.tipo_prestamo or "",
                p.fecha_inicio.strftime("%Y-%m-%d") if p.fecha_inicio else "",
                p.fecha_fin.strftime("%Y-%m-%d") if p.fecha_fin else "",
                p.estado_calculado or "",
            ])

        table = Table(data, repeatRows=1)

        # 🎨 Estilo profesional
        table.setStyle(TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
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