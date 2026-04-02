from django.urls import path
from .views import LoginView, RegisterView, UserListView, UserProfileUpdateView, UserDeleteView, UserUpdateView, UserProfileView, SendVerificationEmailView, VerifyEmailView, SendPasswordResetEmailView, ResetPasswordView, GenerarBackupView, HistorialBackupView, DescargarBackupView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
     path("register/", RegisterView.as_view(), name="register"),
     path("users/", UserListView.as_view(), name="user-list"),
     path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
     path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update-admin"),
     path("users/me/", UserProfileUpdateView.as_view(), name="user-update"),
     path("perfil/", UserProfileView.as_view()),
     path('send-verification-email/', SendVerificationEmailView.as_view()),
     path('verify-email/', VerifyEmailView.as_view()),
     path('send-reset-password-email/', SendPasswordResetEmailView.as_view()),
     path('reset-password/', ResetPasswordView.as_view()),
     path("backup/", GenerarBackupView.as_view()),
     path("backup/historial/", HistorialBackupView.as_view()),
     path("backup/descargar/<int:backup_id>/", DescargarBackupView.as_view()),
]
