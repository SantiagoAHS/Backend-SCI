from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import BackupHistorial


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        'username',
        'email',
        'email_verified',
        'numero_empleado',
        'rol',
        'cargo',
        'activo',
        'is_staff',
    )

    list_filter = (
        'rol',
        'activo',
        'email_verified',
        'is_staff',
        'is_superuser',
    )

    # DEFINICIÓN COMPLETA (sin duplicados)
    fieldsets = (
        ('Credenciales', {
            'fields': ('username', 'password')
        }),
        ('Información personal', {
            'fields': ('email', 'email_verified', 'telefono')
        }),
        ('Información empresarial', {
            'fields': ('numero_empleado', 'rol', 'cargo', 'fecha_ingreso', 'activo')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Información empresarial', {
            'fields': ('numero_empleado', 'rol', 'telefono', 'cargo', 'activo')
        }),
    )

@admin.register(BackupHistorial)
class BackupHistorialAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre",
        "usuario",
        "fecha",
        "descargado",
    )

    list_filter = (
        "descargado",
        "fecha",
        "usuario",
    )

    search_fields = (
        "nombre",
        "usuario__username",
    )

    readonly_fields = (
        "fecha",
        "archivo",
    )

    ordering = ("-fecha",)