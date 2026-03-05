from rest_framework import serializers
from .models import Mantenimiento
from django.utils import timezone
from activos.models import Activo

class MantenimientoPreventivoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mantenimiento
        fields = [
            "activo",
            "estado",
            "fecha_ingreso",
            "responsable",
            "descripcion_problema",
            "costo",
        ]

    def validate(self, data):
        activo = data["activo"]

        # No permitir mantenimiento si ya está en mantenimiento
        if activo.estado == "mantenimiento":
            raise serializers.ValidationError(
                "Este activo ya está en mantenimiento."
            )

        # No permitir si está prestado
        if activo.estado == "asignado":
            raise serializers.ValidationError(
                "No se puede enviar a mantenimiento un activo prestado."
            )

        return data

    def create(self, validated_data):
        validated_data["tipo"] = "preventivo"
        return super().create(validated_data)
    
class CambiarEstadoMantenimientoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mantenimiento
        fields = ["estado"]

    def validate_estado(self, value):
        estados_validos = [
            "programado",
            "en_proceso",
            "completado",
            "cancelado"
        ]

        if value not in estados_validos:
            raise serializers.ValidationError("Estado no válido.")

        return value

    def update(self, instance, validated_data):
        estado = validated_data.get("estado", instance.estado)

        # Si el mantenimiento se completa → guardar fecha automáticamente
        if estado == "completado":
            instance.fecha_finalizacion = timezone.now().date()

        instance.estado = estado
        instance.save()

        return instance

class MantenimientoListSerializer(serializers.ModelSerializer):
    activo = serializers.CharField(source="activo.nombre", read_only=True)
    codigo_activo = serializers.CharField(source="activo.codigo", read_only=True)

    tipo = serializers.CharField()
    estado = serializers.CharField()
    fecha_ingreso = serializers.DateField()
    fecha_finalizacion = serializers.DateField(allow_null=True)

    responsable = serializers.CharField()
    costo = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    descripcion_problema = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Mantenimiento
        fields = [
            "id",
            "activo",
            "codigo_activo",
            "tipo",
            "estado",
            "fecha_ingreso",
            "fecha_finalizacion",
            "responsable",
            "costo",
            "descripcion_problema",
        ]