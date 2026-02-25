from rest_framework import serializers
from .models import TipoActivo, Caracteristica, Activo, ValorCaracteristica
from rest_framework import serializers

class CaracteristicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caracteristica
        fields = ['id', 'nombre']


class TipoActivoSerializer(serializers.ModelSerializer):
    caracteristicas = CaracteristicaSerializer(many=True)

    class Meta:
        model = TipoActivo
        fields = ['id', 'nombre', 'caracteristicas']

    def validate_caracteristicas(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "Debes agregar al menos una característica."
            )
        return value

    def create(self, validated_data):
        caracteristicas_data = validated_data.pop('caracteristicas')
        tipo_activo = TipoActivo.objects.create(**validated_data)

        for caracteristica in caracteristicas_data:
            Caracteristica.objects.create(
                tipo_activo=tipo_activo,
                **caracteristica
            )

        return tipo_activo
    
class ValorCaracteristicaCreateSerializer(serializers.Serializer):
    caracteristica = serializers.IntegerField()
    valor = serializers.CharField()

class ActivoCreateSerializer(serializers.ModelSerializer):
    valores = ValorCaracteristicaCreateSerializer(many=True)

    class Meta:
        model = Activo
        fields = [
            'id',
            'nombre',
            'descripcion',
            'tipo_activo',
            'area',
            'estado',
            'valores'
        ]

    def validate(self, data):
        tipo = data['tipo_activo']
        valores_enviados = data.get('valores', [])

        caracteristicas_tipo = tipo.caracteristicas.all()

        if not caracteristicas_tipo.exists():
            raise serializers.ValidationError(
                "Este tipo de activo no tiene características definidas."
            )

        ids_requeridos = set(caracteristicas_tipo.values_list('id', flat=True))
        ids_enviados = set(v['caracteristica'] for v in valores_enviados)

        if ids_requeridos != ids_enviados:
            raise serializers.ValidationError(
                "Debes enviar valores para todas las características del tipo."
            )

        return data

    def create(self, validated_data):
        valores_data = validated_data.pop('valores')
        activo = Activo.objects.create(**validated_data)

        for valor in valores_data:
            caracteristica_obj = Caracteristica.objects.get(id=valor['caracteristica'])

            ValorCaracteristica.objects.create(
                activo=activo,
                caracteristica=caracteristica_obj,
                valor=valor['valor']
            )

        return activo