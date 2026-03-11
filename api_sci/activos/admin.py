from django.contrib import admin
from .models import (
    TipoActivo,
    Activo,
    Caracteristica,
    ValorCaracteristica,
    OpcionCaracteristica
)


# 🔹 Inline para opciones dentro de cada característica
class OpcionCaracteristicaInline(admin.TabularInline):
    model = OpcionCaracteristica
    extra = 1


# 🔹 Inline para características dentro del TipoActivo
class CaracteristicaInline(admin.TabularInline):
    model = Caracteristica
    extra = 1
    show_change_link = True


@admin.register(TipoActivo)
class TipoActivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)
    inlines = [CaracteristicaInline]

    def get_queryset(self, request):
        return TipoActivo.all_objects.all()


# 🔹 Admin de Caracteristicas
@admin.register(Caracteristica)
class CaracteristicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_activo', 'tipo_dato', 'obligatorio')
    list_filter = ('tipo_activo', 'tipo_dato', 'obligatorio')
    search_fields = ('nombre',)
    inlines = [OpcionCaracteristicaInline]


# 🔹 Inline para valores dentro del Activo
class ValorCaracteristicaInline(admin.TabularInline):
    model = ValorCaracteristica
    extra = 0


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'tipo_activo',
        'area',
        'estado',
        'fecha_registro'
    )

    list_filter = (
        'tipo_activo',
        'area',
        'estado'
    )

    search_fields = ('nombre',)

    inlines = [ValorCaracteristicaInline]


# 🔹 Admin para opciones de característica
@admin.register(OpcionCaracteristica)
class OpcionCaracteristicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'caracteristica')
    list_filter = ('caracteristica',)
    search_fields = ('nombre',)


# 🔹 Admin para valores de características
@admin.register(ValorCaracteristica)
class ValorCaracteristicaAdmin(admin.ModelAdmin):
    list_display = (
        'activo',
        'caracteristica',
        'valor_texto',
        'opcion'
    )

    list_filter = ('caracteristica',)
    search_fields = ('activo__nombre',)