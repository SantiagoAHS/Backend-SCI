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

        prestamos = Prestamo.objects.select_related("activo", "area").all()

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=reporte_prestamos.pdf"

        p = canvas.Canvas(response, pagesize=letter)

        width, height = letter

        # 🔹 LOGO (texto temporal)
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

        # 🔹 Dibujar línea superior de la tabla
        p.line(40, y + 10, 580, y + 10)

        p.setFont("Helvetica-Bold", 10)

        for i, header in enumerate(headers):
            p.drawString(x_positions[i], y, header)

        # 🔹 Línea debajo del header
        p.line(40, y - 5, 580, y - 5)

        y -= 20
        p.setFont("Helvetica", 9)

        for prestamo in prestamos:

            p.drawString(40, y, str(prestamo.activo.nombre))
            p.drawString(140, y, str(prestamo.responsable_nombre))
            p.drawString(260, y, str(prestamo.area.nombre if prestamo.area else "N/A"))
            p.drawString(340, y, str(prestamo.tipo_prestamo))
            p.drawString(400, y, str(prestamo.fecha_inicio))
            p.drawString(460, y, str(prestamo.fecha_fin))
            p.drawString(520, y, str(prestamo.estado_calculado))

            # 🔹 Línea horizontal de cada fila
            p.line(40, y - 5, 580, y - 5)

            y -= 20

            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 9)
                y = 750

        # 🔹 Líneas verticales de la tabla
        for x in [40, 140, 260, 340, 400, 460, 520, 580]:
            p.line(x, 710, x, y + 20)

        p.save()

        return response