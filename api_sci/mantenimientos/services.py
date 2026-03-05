from django.utils import timezone
from activos.models import Activo
from .models import Mantenimiento


def generar_mantenimientos_preventivos():

    activos = Activo.objects.all()

    for activo in activos:

        if activo.necesita_mantenimiento():

            existe = Mantenimiento.objects.filter(
                activo=activo,
                tipo="preventivo",
                estado="programado"
            ).exists()

            if not existe:
                Mantenimiento.objects.create(
                    activo=activo,
                    tipo="preventivo",
                    estado="programado",
                    fecha_ingreso=timezone.now().date(),
                    responsable="Sistema automático",
                    descripcion_problema="Mantenimiento preventivo generado automáticamente"
                )