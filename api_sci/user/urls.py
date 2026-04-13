from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    UserListView,
    UserProfileUpdateView,
    UserDeleteView,
    UserUpdateView,
    UserProfileView,
    SendVerificationEmailView,
    VerifyEmailView,
    SendPasswordResetEmailView,
    ResetPasswordView,
    GenerarBackupView,
    HistorialBackupView,
    DescargarBackupView
)

urlpatterns = [

    # ==============================
    # AUTENTICACIÓN
    # ==============================
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),

    # ==============================
    # GESTIÓN DE USUARIOS (ADMIN)
    # ==============================
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update-admin"),

    # ==============================
    # PERFIL DE USUARIO
    # ==============================
    path("users/me/", UserProfileUpdateView.as_view(), name="user-update"),
    path("perfil/", UserProfileView.as_view()),

    # ==============================
    # VERIFICACIÓN DE CORREO
    # ==============================
    path('send-verification-email/', SendVerificationEmailView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),

    # ==============================
    # RECUPERACIÓN DE CONTRASEÑA
    # ==============================
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),

    # ==============================
    # BACKUPS DEL SISTEMA
    # ==============================
    path("backup/", GenerarBackupView.as_view()),
    path("backup/historial/", HistorialBackupView.as_view()),
    path("backup/descargar/<int:backup_id>/", DescargarBackupView.as_view()),
]