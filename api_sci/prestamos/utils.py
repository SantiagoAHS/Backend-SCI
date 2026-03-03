from django.utils import timezone
from .models import Prestamo

def actualizar_prestamos_vencidos():
    hoy = timezone.now().date()

    prestamos_vencidos = Prestamo.objects.filter(
        estado="activo",
        fecha_fin__lt=hoy
    )

    prestamos_vencidos.update(estado="vencido")