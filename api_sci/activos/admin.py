from django.contrib import admin
from .models import TipoActivo, Activo, Caracteristica, ValorCaracteristica


# 🔹 Inline para las características dentro del TipoActivo
class CaracteristicaInline(admin.TabularInline):
    model = Caracteristica
    extra = 1


@admin.register(TipoActivo)
class TipoActivoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    inlines = [CaracteristicaInline]


# 🔹 Inline para los valores dinámicos dentro del Activo
class ValorCaracteristicaInline(admin.TabularInline):
    model = ValorCaracteristica
    extra = 0


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_activo', 'area', 'responsable_directo', 'activo')
    list_filter = ('tipo_activo', 'area', 'activo')
    search_fields = ('nombre',)
    inlines = [ValorCaracteristicaInline]


@admin.register(Caracteristica)
class CaracteristicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_activo')
    list_filter = ('tipo_activo',)
    search_fields = ('nombre',)


@admin.register(ValorCaracteristica)
class ValorCaracteristicaAdmin(admin.ModelAdmin):
    list_display = ('activo', 'caracteristica', 'valor')
    list_filter = ('caracteristica',)
    search_fields = ('activo__nombre',)