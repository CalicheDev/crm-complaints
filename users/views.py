from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User, Group

class RegisterView(APIView):
    """
    Endpoint para registrar usuarios.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response(
                {'error': 'Faltan campos obligatorios: username, password y email.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response({'error': 'El usuario ya existe.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'El correo electrónico ya está en uso.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            token = Token.objects.create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    """
    Endpoint para iniciar sesión.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate

        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            # Generar o obtener el token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Responder con el token en el cuerpo de la respuesta
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            # Si las credenciales son incorrectas
            return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Endpoint para cerrar sesión.
    """
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Cierre de sesión exitoso.'}, status=status.HTTP_200_OK)

class UserListView(APIView):
    """
    Endpoint para listar usuarios y sus roles.
    Solo accesible para administradores.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.groups.filter(name='admin').exists():
            return Response({'error': 'Permiso denegado. Solo para administradores.'}, status=403)
        
        users = User.objects.all().values('id', 'username', 'email', 'groups__name')
        return Response({'users': list(users)}, status=status.HTTP_200_OK)


class UpdateUserRoleView(APIView):
    """
    Endpoint para asignar roles a un usuario.
    Solo accesible para administradores.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not request.user.groups.filter(name='admin').exists():
            return Response({'error': 'Permiso denegado. Solo para administradores.'}, status=403)
        
        role = request.data.get('role')
        if role not in ['admin', 'agent']:
            return Response({'error': 'Rol no válido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name=role)
            user.groups.clear()
            user.groups.add(group)
            return Response({'message': f'Rol actualizado a {role} para el usuario {user.username}.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'Grupo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    """
    Endpoint para ver y editar el perfil del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retorna la información del usuario autenticado
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })

    def put(self, request):
        # Actualiza la información del usuario autenticado
        user = request.user
        data = request.data

        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.email = data.get("email", user.email)

        # Actualizar contraseña solo si se proporciona
        password = data.get("password")
        if password:
            user.set_password(password)

        user.save()
        return Response({"message": "Perfil actualizado correctamente."}, status=status.HTTP_200_OK)