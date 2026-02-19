# serializers.py
from rest_framework import serializers
from .models import Area
from user.models import User 


class AreaSerializer(serializers.ModelSerializer):

    # Para mostrar datos del usuario al listar
    responsable_detalle = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Area
        fields = [
            "id",
            "nombre",
            "descripcion",
            "responsable",          # ← recibe ID
            "responsable_detalle",  # ← muestra info del usuario
            "activo"
        ]

    def get_responsable_detalle(self, obj):
        if obj.responsable:
            return {
                "id": obj.responsable.id,
                "username": obj.responsable.username,
                "numero_empleado": obj.responsable.numero_empleado,
                "telefono": obj.responsable.telefono,
            }
        return None
