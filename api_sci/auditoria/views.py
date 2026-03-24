from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework import generics
from .serializers import AuditoriaDetalleSerializer
from .serializers import DetalleAuditoriaSerializer
from .serializers import AuditoriaSerializer

from activos.models import Activo
from .models import Auditoria, DetalleAuditoria


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def iniciar_auditoria(request):

    if request.user.rol != "admin":
        raise PermissionDenied("No autorizado")

    auditoria = Auditoria.objects.create(
        nombre=f"Auditoría {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        responsable=request.user.username,
        estado="en_proceso"
    )

    activos = Activo.objects.all()

    for activo in activos:
        DetalleAuditoria.objects.create(
            auditoria=auditoria,
            activo=activo
        )

    return Response({
        "message": "Auditoría iniciada",
        "auditoria_id": auditoria.id
    }, status=status.HTTP_201_CREATED)


class AuditoriaDetailView(generics.RetrieveAPIView):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaDetalleSerializer
    permission_classes = [IsAuthenticated]


class DetalleAuditoriaUpdateView(generics.UpdateAPIView):
    queryset = DetalleAuditoria.objects.all()
    serializer_class = DetalleAuditoriaSerializer
    permission_classes = [IsAuthenticated]

class AuditoriaListView(generics.ListAPIView):
    queryset = Auditoria.objects.all().order_by("-creado_en")
    serializer_class = AuditoriaSerializer
    permission_classes = [IsAuthenticated]

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def finalizar_auditoria(request, pk):

    if request.user.rol != "admin":
        raise PermissionDenied("No autorizado")

    try:
        auditoria = Auditoria.objects.get(pk=pk)
    except Auditoria.DoesNotExist:
        return Response({"error": "No encontrada"}, status=404)

    auditoria.estado = "finalizada"
    auditoria.fecha_fin = timezone.now()
    auditoria.save()

    return Response({"message": "Auditoría finalizada"})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def iniciar_auditoria_area(request):
    """
    Inicia una auditoría para un área específica.
    Se espera recibir en el body: {"area_id": 1}
    """
    if request.user.rol != "admin":
        raise PermissionDenied("No autorizado")

    area_id = request.data.get("area_id")
    if not area_id:
        return Response({"error": "Se requiere el ID del área"}, status=status.HTTP_400_BAD_REQUEST)

    from areas.models import Area
    try:
        area = Area.objects.get(pk=area_id)
    except Area.DoesNotExist:
        return Response({"error": "Área no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    # 🔹 Evitar duplicar "Auditoría" si el área ya lo tiene
    area_nombre = area.nombre
    if not area_nombre.lower().startswith("auditoría"):
        area_nombre = f"{area_nombre}"

    # 🔹 Crear auditoría
    auditoria = Auditoria.objects.create(
        nombre=f"Auditoría {area_nombre} {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        responsable=request.user.username,
        estado="en_proceso",
        area=area
    )

    # 🔹 Filtrar activos solo de esa área
    activos = Activo.objects.filter(area=area)

    for activo in activos:
        DetalleAuditoria.objects.create(
            auditoria=auditoria,
            activo=activo
        )

    return Response({
        "message": f"Auditoría para el área {area.nombre} iniciada",
        "auditoria_id": auditoria.id
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def iniciar_auditoria_tipo(request):
    """
    Inicia una auditoría por tipo de activos.
    Body: {"tipo": "mantenimiento"} | {"tipo": "prestamo"} | {"tipo": "disponible"}
    """

    if request.user.rol != "admin":
        raise PermissionDenied("No autorizado")

    tipo = request.data.get("tipo")

    if not tipo:
        return Response(
            {"error": "Se requiere el tipo de auditoría"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # AHORA INCLUYE DISPONIBLE
    if tipo not in ["mantenimiento", "prestamo", "disponible"]:
        return Response(
            {"error": "Tipo no válido. Debe ser 'mantenimiento', 'prestamo' o 'disponible'"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔹 Mapear tipo → estado real en Activo
    MAPEO_TIPO_ESTADO = {
        "mantenimiento": "mantenimiento",
        "prestamo": "asignado",  
        "disponible": "disponible"  
    }

    estado_filtro = MAPEO_TIPO_ESTADO.get(tipo)

    # 🔹 Crear auditoría
    auditoria = Auditoria.objects.create(
        nombre=f"Auditoría {tipo.capitalize()} {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        responsable=request.user.username,
        tipo=tipo,
        estado="en_proceso"
    )

    # 🔹 Filtrar activos
    activos = Activo.objects.filter(estado=estado_filtro)

    # 🔹 DEBUG (opcional)
    print("TIPO:", tipo)
    print("ESTADO FILTRO:", estado_filtro)
    print("ACTIVOS ENCONTRADOS:", activos.count())

    # 🔹 Crear detalles
    for activo in activos:
        DetalleAuditoria.objects.create(
            auditoria=auditoria,
            activo=activo
        )

    return Response({
        "message": f"Auditoría de tipo {tipo} iniciada",
        "auditoria_id": auditoria.id,
        "total_activos": activos.count()
    }, status=status.HTTP_201_CREATED)

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .models import Auditoria, DetalleAuditoria


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generar_pdf_auditoria(request, pk):

    try:
        auditoria = Auditoria.objects.get(pk=pk)
    except Auditoria.DoesNotExist:
        return Response({"error": "Auditoría no encontrada"}, status=404)

    if auditoria.estado != "finalizada":
        return Response({"error": "La auditoría no está finalizada"}, status=400)

    detalles = DetalleAuditoria.objects.filter(auditoria=auditoria)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="auditoria_{auditoria.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elementos = []

    # 🔹 Título
    elementos.append(Paragraph("Reporte de Auditoría", styles['Title']))
    elementos.append(Spacer(1, 12))

    # 🔹 Info
    elementos.append(Paragraph(f"Nombre: {auditoria.nombre}", styles['Normal']))
    elementos.append(Paragraph(f"Responsable: {auditoria.responsable}", styles['Normal']))
    elementos.append(Paragraph(f"Estado: {auditoria.estado}", styles['Normal']))
    elementos.append(Paragraph(f"Fecha inicio: {auditoria.creado_en}", styles['Normal']))
    elementos.append(Paragraph(f"Fecha fin: {auditoria.fecha_fin}", styles['Normal']))
    elementos.append(Spacer(1, 12))

    # 🔹 Tabla
    data = [["ID", "Activo", "Sistema", "Real", "Resultado"]]

    correctos = 0
    incorrectos = 0

    for d in detalles:

        estado_sistema = d.activo.estado
        estado_real = getattr(d, "estado_real", None)  # 

        if estado_sistema == estado_real:
            estado_texto = "Correcto"
            correctos += 1
        else:
            estado_texto = "Incorrecto"
            incorrectos += 1

        data.append([
            d.activo.id,
            str(d.activo.nombre),
            estado_sistema,
            estado_real if estado_real else "Sin registro",
            estado_texto
        ])

    # 🔹 Resumen
    elementos.append(Paragraph(f"Correctos: {correctos}", styles['Normal']))
    elementos.append(Paragraph(f"Incorrectos: {incorrectos}", styles['Normal']))
    elementos.append(Spacer(1, 12))

    tabla = Table(data)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response