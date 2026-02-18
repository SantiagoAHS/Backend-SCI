from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer


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
