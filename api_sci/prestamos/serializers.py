from rest_framework import serializers
from .models import Prestamo
from django.utils import timezone
from activos.models import Activo

class PrestamoCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prestamo
        fields = "__all__"

    def validate(self, data):
        activo = data["activo"]

        # Validar que el activo esté disponible
        if activo.estado != "disponible":
            raise serializers.ValidationError(
                "Este activo no está disponible para préstamo."
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

    class Meta:
        model = Prestamo
        fields = "__all__"  

    def get_estado_calculado(self, obj):
        if obj.estado in ["finalizado", "cancelado"]:
            return obj.estado

        if obj.fecha_fin < timezone.now().date():
            return "vencido"

        return "activo"

    def get_dias_restantes(self, obj):
        return (obj.fecha_fin - timezone.now().date()).days