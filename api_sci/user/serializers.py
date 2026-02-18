from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "numero_empleado",
            "rol",
            "telefono",
            "cargo",
            "fecha_ingreso",
            "activo"
        ]
