from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import PasswordResetToken, User
from .serializers import UserSerializer, RegisterSerializer, UserUpdateSerializer, AdminUserUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerificationToken
import resend


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        # Solo admin puede editar usuarios
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = get_object_or_404(User, pk=pk)

        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario actualizado correctamente"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        numero_empleado = request.data.get("numero_empleado")
        password = request.data.get("password")

        if not numero_empleado or not password:
            return Response({"error": "Debe enviar numero_empleado y password"}, status=400)

        try:
            user_obj = User.objects.get(numero_empleado=numero_empleado)
        except User.DoesNotExist:
            return Response({"error": "Credenciales inválidas"}, status=400)

        user = authenticate(
            request,
            username=user_obj.username,  # usamos username interno
            password=password
        )

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            })

        return Response({"error": "Credenciales inválidas"}, status=400)

class RegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Solo admin puede crear usuarios
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Usuario creado correctamente"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Solo admin puede ver la lista
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        users = User.objects.all().order_by("id")
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)
    
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):

        user = request.user  #  Usuario autenticado automáticamente

        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Datos actualizados correctamente"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        # Solo admin puede eliminar usuarios
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = get_object_or_404(User, pk=pk)

        # Opcional: evitar que el admin se elimine a sí mismo
        if user == request.user:
            return Response(
                {"error": "No puedes eliminar tu propio usuario"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()

        return Response(
            {"message": "Usuario eliminado correctamente"},
            status=status.HTTP_200_OK
        )
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)

        return Response(serializer.data)
    

class SendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.email:
            return Response({"error": "No tienes correo registrado"}, status=400)

        user.email_verified = False
        user.save()

        token_obj = EmailVerificationToken.objects.create(user=user)

        link = f"{settings.FRONTEND_URL}/verify-email/{token_obj.token}"

        resend.api_key = settings.RESEND_API_KEY

        resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [user.email],
            "subject": "Verifica tu correo",
            "html": f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                
                <h2 style="color:#333;">Verifica tu cuenta</h2>
                
                <p style="color:#555;">
                    Gracias por registrarte. Para continuar, confirma tu correo electrónico.
                </p>

                <a href="{link}" 
                style="
                    display:inline-block;
                    margin-top:20px;
                    padding:12px 20px;
                    background-color:#3b82f6;
                    color:white;
                    text-decoration:none;
                    border-radius:8px;
                    font-weight:bold;
                ">
                    Verificar correo
                </a>

                <p style="margin-top:20px; font-size:12px; color:#999;">
                    Si no solicitaste esto, puedes ignorar este mensaje.
                </p>

            </div>
            """
        })

        return Response({"message": "Correo enviado correctamente"})

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"error": "Token requerido"}, status=400)

        try:
            token_obj = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response({"error": "Token inválido"}, status=400)

        if token_obj.is_expired():
            token_obj.delete()  # 🔥 limpiar
            return Response({"error": "Token expirado"}, status=400)

        user = token_obj.user
        user.email_verified = True
        user.save()

        token_obj.delete()

        return Response({"message": "Correo verificado correctamente"})


class SendPasswordResetEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Debes enviar un correo"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # 🔒 Seguridad: no revelar si el correo existe
            return Response({
                "message": "Si el correo existe, se enviará un enlace"
            })

        # 🧹 Eliminar tokens anteriores
        PasswordResetToken.objects.filter(user=user).delete()

        # 🎟 Crear nuevo token
        token_obj = PasswordResetToken.objects.create(user=user)

        # 🔗 Link al frontend
        link = f"{settings.FRONTEND_URL}/reset-password/{token_obj.token}"

        # 📧 Configurar Resend
        resend.api_key = settings.RESEND_API_KEY

        # ✉️ Enviar correo
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": user.email,
            "subject": "Recuperación de contraseña",
            "html": f"""
                <h2>🔐 Recuperación de contraseña</h2>
                <p>Solicitaste cambiar tu contraseña.</p>
                <p>Haz clic en el siguiente botón:</p>

                <a href="{link}" 
                   style="display:inline-block;padding:10px 20px;background:black;color:white;text-decoration:none;border-radius:5px;">
                   Cambiar contraseña
                </a>

                <p>Si no solicitaste esto, puedes ignorar este correo.</p>
            """
        })

        return Response({
            "message": "Correo de recuperación enviado"
        })

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not token or not new_password:
            return Response({"error": "Datos incompletos"}, status=400)

        try:
            token_obj = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "Token inválido"}, status=400)

        if token_obj.is_expired():
            token_obj.delete()  # 🔥 limpiar
            return Response({"error": "Token expirado"}, status=400)

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        token_obj.delete()

        return Response({"message": "Contraseña actualizada correctamente"})