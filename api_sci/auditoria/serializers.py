from rest_framework import serializers
from .models import Auditoria, DetalleAuditoria


class DetalleAuditoriaSerializer(serializers.ModelSerializer):
    activo_nombre = serializers.CharField(source="activo.nombre", read_only=True)

    class Meta:
        model = DetalleAuditoria
        fields = "__all__"

class AuditoriaDetalleSerializer(serializers.ModelSerializer):
    detalles = DetalleAuditoriaSerializer(many=True, read_only=True)

    class Meta:
        model = Auditoria
        fields = "__all__"

class AuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditoria
        fields = "__all__"