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
    

class ReportePrestamosPDFView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Fechas desde query params
        fecha_inicio = request.GET.get("fecha_inicio")
        fecha_fin = request.GET.get("fecha_fin")

        prestamos = Prestamo.objects.select_related("activo", "area").all()

        # Filtros correctos
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            prestamos = prestamos.filter(
                fecha_inicio__gte=fecha_inicio
            )

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)
            prestamos = prestamos.filter(
                fecha_inicio__lt=fecha_fin
            )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=reporte_prestamos.pdf"

        p = canvas.Canvas(response, pagesize=letter)

        width, height = letter

        # 🔹 LOGO
        p.setFont("Helvetica-Bold", 30)
        p.drawString(width - 150, height - 60, "LOGO")

        # 🔹 Título
        y = 750
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, y, "Reporte de Préstamos")

        y -= 40

        headers = [
            "Activo",
            "Responsable",
            "Área",
            "Tipo",
            "Inicio",
            "Fin",
            "Estado"
        ]

        x_positions = [40, 140, 260, 340, 400, 460, 520]

        # 🔹 Línea superior
        p.line(40, y + 10, 580, y + 10)

        p.setFont("Helvetica-Bold", 10)

        for i, header in enumerate(headers):
            p.drawString(x_positions[i], y, header)

        # 🔹 Línea header
        p.line(40, y - 5, 580, y - 5)

        y -= 20
        p.setFont("Helvetica", 9)

        for prestamo in prestamos:

            # Manejo seguro
            activo = prestamo.activo.nombre if prestamo.activo else ""
            responsable = prestamo.responsable_nombre if prestamo.responsable_nombre else ""
            area = prestamo.area.nombre if prestamo.area else "N/A"
            tipo = prestamo.tipo_prestamo if prestamo.tipo_prestamo else ""
            inicio = prestamo.fecha_inicio.strftime("%Y-%m-%d") if prestamo.fecha_inicio else ""
            fin = prestamo.fecha_fin.strftime("%Y-%m-%d") if prestamo.fecha_fin else ""
            estado = prestamo.estado_calculado if prestamo.estado_calculado else ""

            p.drawString(40, y, str(activo))
            p.drawString(140, y, str(responsable))
            p.drawString(260, y, str(area))
            p.drawString(340, y, str(tipo))
            p.drawString(400, y, inicio)
            p.drawString(460, y, fin)
            p.drawString(520, y, str(estado))

            # 🔹 línea fila
            p.line(40, y - 5, 580, y - 5)

            y -= 20

            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 9)
                y = 750

        # 🔹 líneas verticales (opcional, se dibujan al final de cada página realmente)
        for x in [40, 140, 260, 340, 400, 460, 520, 580]:
            p.line(x, 710, x, y + 20)

        p.save()

        return response