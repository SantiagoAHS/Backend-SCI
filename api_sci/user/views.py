from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import RegisterSerializer, UserUpdateSerializer
from django.shortcuts import get_object_or_404


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        # 🔐 Solo admin puede editar usuarios
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = get_object_or_404(User, pk=pk)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

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

        # 🔐 Solo admin puede crear usuarios
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

        # 🔐 Solo admin puede ver la lista
        if request.user.rol != "admin":
            return Response(
                {"error": "No autorizado"},
                status=status.HTTP_403_FORBIDDEN
            )

        users = User.objects.all().order_by("id")
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)
    
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):

        user = request.user  # 👈 Usuario autenticado automáticamente

        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Datos actualizados correctamente"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


