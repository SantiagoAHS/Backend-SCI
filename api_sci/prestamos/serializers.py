from rest_framework import serializers
from .models import Prestamo
from django.utils import timezone
from activos.models import Activo
from mantenimientos.models import Mantenimiento

class PrestamoCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prestamo
        fields = "__all__"

    def validate(self, data):
        activo = data["activo"]

        # 🔹 Verificar si el activo ya tiene un préstamo activo
        prestamo_activo = activo.prestamos.filter(
            estado="activo"
        ).exists()

        if prestamo_activo:
            raise serializers.ValidationError(
                "Este activo ya está prestado."
            )

        # 🔹 Verificar si está en mantenimiento
        mantenimiento = activo.mantenimientos.filter(
            estado="en_proceso"
        ).exists()

        if mantenimiento:
            raise serializers.ValidationError(
                "Este activo está en mantenimiento."
            )

        return data

    def create(self, validated_data):
        activo = validated_data["activo"]

        # Crear préstamo
        prestamo = Prestamo.objects.create(**validated_data)

        # Cambiar estado del activo a ASIGNADO
        activo.estado = "asignado"
        activo.save()

        return prestamo
    
class PrestamoListSerializer(serializers.ModelSerializer):

    estado_calculado = serializers.SerializerMethodField()
    dias_restantes = serializers.SerializerMethodField()

    # datos del activo
    activo_nombre = serializers.CharField(source="activo.nombre", read_only=True)
    activo_tipo = serializers.CharField(source="activo.tipo", read_only=True)

    class Meta:
        model = Prestamo
        fields = [
            "id",
            "activo",
            "activo_nombre",
            "activo_tipo",
            "responsable_nombre",
            "tipo_prestamo",
            "estado",
            "estado_calculado",
            "fecha_inicio",
            "fecha_fin",
            "dias_restantes",
            "area",
        ]

    def get_estado_calculado(self, obj):
        if obj.estado in ["finalizado", "cancelado"]:
            return obj.estado

        if obj.fecha_fin < timezone.now().date():
            return "vencido"

        return "activo"

    def get_dias_restantes(self, obj):
        return (obj.fecha_fin - timezone.now().date()).days
    
class PrestamoInfoSerializer(serializers.ModelSerializer):

    area = serializers.StringRelatedField()
    estado_calculado = serializers.ReadOnlyField()

    class Meta:
        model = Prestamo
        fields = [
            "id",
            "responsable_nombre",
            "responsable_telefono",
            "area",
            "tipo_prestamo",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "estado_calculado"
        ]