from rest_framework import serializers
from .models import (
    TipoActivo,
    Caracteristica,
    Activo,
    ValorCaracteristica,
    OpcionCaracteristica
)


# 🔹 Opciones de característica
class OpcionCaracteristicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionCaracteristica
        fields = ['id', 'nombre']


# 🔹 Características
class CaracteristicaSerializer(serializers.ModelSerializer):

    opciones = OpcionCaracteristicaSerializer(many=True, required=False)

    class Meta:
        model = Caracteristica
        fields = [
            'id',
            'nombre',
            'tipo_dato',
            'obligatorio',
            'opciones'
        ]


# 🔹 Tipo de activo
class TipoActivoSerializer(serializers.ModelSerializer):

    caracteristicas = CaracteristicaSerializer(many=True)

    class Meta:
        model = TipoActivo
        fields = [
            'id',
            'nombre',
            'caracteristicas'
        ]

    def validate_caracteristicas(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "Debes agregar al menos una característica."
            )
        return value

    def create(self, validated_data):

        caracteristicas_data = validated_data.pop('caracteristicas')
        nombre = validated_data['nombre'].strip()

        tipo_existente = TipoActivo.all_objects.filter(
            nombre__iexact=nombre
        ).first()

        if tipo_existente:
            if not tipo_existente.activo:
                tipo_existente.activo = True
                tipo_existente.nombre = nombre
                tipo_existente.save()
                return tipo_existente
            else:
                raise serializers.ValidationError(
                    "Ya existe un tipo de activo con ese nombre."
                )

        tipo_activo = TipoActivo.objects.create(nombre=nombre)

        for caracteristica_data in caracteristicas_data:

            opciones_data = caracteristica_data.pop('opciones', [])

            caracteristica = Caracteristica.objects.create(
                tipo_activo=tipo_activo,
                **caracteristica_data
            )

            for opcion in opciones_data:
                OpcionCaracteristica.objects.create(
                    caracteristica=caracteristica,
                    nombre=opcion['nombre']
                )

        return tipo_activo


# 🔹 Crear valor de característica
class ValorCaracteristicaCreateSerializer(serializers.Serializer):

    caracteristica = serializers.IntegerField()
    valor_texto = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    opcion = serializers.IntegerField(required=False)


# 🔹 Crear activo
class ActivoCreateSerializer(serializers.ModelSerializer):

    valores = ValorCaracteristicaCreateSerializer(many=True, required=False)

    class Meta:
        model = Activo
        fields = [
            'id',
            'nombre',
            'imagen',
            'descripcion',
            'tipo_activo',
            'area',
            'estado',
            'valores'
        ]

    def validate(self, data):

        tipo = data['tipo_activo']

        valores_enviados = self.initial_data.get('valores', [])

        if isinstance(valores_enviados, str):
            import json
            valores_enviados = json.loads(valores_enviados)

        caracteristicas = Caracteristica.objects.filter(tipo_activo=tipo)

        if not caracteristicas.exists():
            raise serializers.ValidationError(
                "Este tipo de activo no tiene características definidas."
            )

        ids_enviados = set()

        for v in valores_enviados:
            try:
                ids_enviados.add(int(v['caracteristica']))
            except:
                pass

        for caracteristica in caracteristicas:
            if caracteristica.obligatorio and caracteristica.id not in ids_enviados:
                raise serializers.ValidationError(
                    f"La característica '{caracteristica.nombre}' es obligatoria."
                )

        return data

    def create(self, validated_data):

        validated_data.pop('valores', None)

        activo = Activo.objects.create(**validated_data)

        return activo


# 🔹 Serializer para mostrar valores
class ValorCaracteristicaSerializer(serializers.ModelSerializer):

    caracteristica = CaracteristicaSerializer()
    opcion = OpcionCaracteristicaSerializer()

    class Meta:
        model = ValorCaracteristica
        fields = [
            'id',
            'caracteristica',
            'valor_texto',
            'opcion'
        ]


# 🔹 Lista de activos
class ActivoListSerializer(serializers.ModelSerializer):

    tipo_activo = serializers.StringRelatedField()
    area = serializers.StringRelatedField()
    valores = ValorCaracteristicaSerializer(many=True)

    class Meta:
        model = Activo
        fields = [
            'id',
            'nombre',
            'imagen',
            'descripcion',
            'tipo_activo',
            'area',
            'estado',
            'valores'
        ]