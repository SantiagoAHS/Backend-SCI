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

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "numero_empleado",
            "password",
            "rol",
            "telefono",
            "cargo",
            "fecha_ingreso",
            "activo",
        ]

    def validate_numero_empleado(self, value):
        if User.objects.filter(numero_empleado=value).exists():
            raise serializers.ValidationError("El número de empleado ya existe.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # 🔐 encripta contraseña
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    telefono = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ["password", "telefono"]

    def update(self, instance, validated_data):
        password = validated_data.get("password", None)
        telefono = validated_data.get("telefono", None)

        if password:
            instance.set_password(password)  # 🔐 encripta

        if telefono is not None:
            instance.telefono = telefono

        instance.save()
        return instance

