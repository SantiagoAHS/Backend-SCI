from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        'username',
        'numero_empleado',
        'rol',
        'cargo',
        'activo',
        'is_staff',
    )

    list_filter = (
        'rol',
        'activo',
        'is_staff',
        'is_superuser',
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Información Empresarial', {
            'fields': (
                'numero_empleado',
                'rol',
                'telefono',
                'cargo',
                'fecha_ingreso',
                'activo',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Empresarial', {
            'fields': (
                'numero_empleado',
                'rol',
                'telefono',
                'area',
                'fecha_ingreso',
                'activo',
            )
        }),
    )

