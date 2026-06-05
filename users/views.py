# general/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers as drf_serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.conf import settings

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from drf_spectacular.types import OpenApiTypes


class LoginView(APIView):
    """
    POST /auth/login/
    Recibe email y password, devuelve los tokens en cookies HttpOnly
    El body de respuesta NO incluye los tokens — van solo en las cookies
    """

    @extend_schema(
        tags=['Autenticación'],
        summary='Iniciar sesión',
        description=(
            'Autentica al usuario con email y contraseña. '
            'Los tokens JWT (access y refresh) se envían en cookies HttpOnly y **no** aparecen en el body.\n\n'
            '- `access_token` cookie: 15 minutos de vida.\n'
            '- `refresh_token` cookie: 24 horas de vida.\n\n'
            'El body de respuesta devuelve únicamente los datos del usuario.'
        ),
        request=inline_serializer(
            name='LoginRequest',
            fields={
                'email':    drf_serializers.EmailField(),
                'password': drf_serializers.CharField(),
            },
        ),
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'message': drf_serializers.CharField(),
                    'user': inline_serializer(
                        name='LoginUserData',
                        fields={
                            'id':       drf_serializers.IntegerField(),
                            'email':    drf_serializers.EmailField(),
                            'username': drf_serializers.CharField(),
                            'role':     drf_serializers.CharField(),
                            'is_admin': drf_serializers.BooleanField(),
                        },
                    ),
                },
            ),
            401: inline_serializer(
                name='LoginUnauthorized',
                fields={'error': drf_serializers.CharField()},
            ),
        },
        examples=[
            OpenApiExample(
                'Credenciales correctas',
                value={'email': 'usuario@bocar.com', 'password': 'contraseña123'},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        email    = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {'error': 'Credenciales incorrectas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generamos los tokens para el usuario
        refresh = RefreshToken.for_user(user)
        access  = str(refresh.access_token)

        response = Response({
            'message': 'Login exitoso.',
            'user': {
                'id':       user.id,
                'email':    user.email,
                'username': user.username,
                'role':     user.role,
                'is_admin': user.is_admin,
            }
            # Los tokens NO van en el body — van en las cookies
        })

        # ── Cookie del Access Token ──────────────────────────────────────────
        # HttpOnly=True  → JavaScript no puede leerla (protege contra XSS)
        # Secure=True    → Solo se envía por HTTPS (en producción)
        # SameSite='Lax' → Protege contra CSRF
        response.set_cookie(
            key      = 'access_token',
            value    = access,
            httponly = True,
            secure   = settings.COOKIE_SECURE,
            samesite = settings.COOKIE_SAMESITE,
            max_age  = 15 * 60,     # 15 minutos en segundos
        )

        # ── Cookie del Refresh Token ─────────────────────────────────────────
        response.set_cookie(
            key      = 'refresh_token',
            value    = str(refresh),
            httponly = True,
            secure   = settings.COOKIE_SECURE,
            samesite = settings.COOKIE_SAMESITE,
            max_age  = 24 * 60 * 60,    # 1 día en segundos
        )

        return response


class LogoutView(APIView):
    """
    POST /auth/logout/
    Blacklistea el refresh token y elimina ambas cookies
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Autenticación'],
        summary='Cerrar sesión',
        description=(
            'Invalida el refresh token (lo añade a la blacklist) y elimina '
            'las cookies `access_token` y `refresh_token`.\n\n'
            'Requiere estar autenticado (cookie `access_token` válida).'
        ),
        request=None,
        responses={
            200: inline_serializer(
                name='LogoutResponse',
                fields={'message': drf_serializers.CharField()},
            ),
            400: inline_serializer(
                name='LogoutBadRequest',
                fields={'error': drf_serializers.CharField()},
            ),
        },
    )
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {'error': 'No hay sesión activa.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Blacklisteamos el refresh para que no se pueda usar más
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {'error': 'Token inválido o ya expirado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response({'message': 'Logout exitoso.'})

        # Eliminamos ambas cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class RefreshTokenView(APIView):
    """
    POST /auth/refresh/
    Lee el refresh token de la cookie, genera un nuevo access token
    y lo devuelve en una nueva cookie
    """

    @extend_schema(
        tags=['Autenticación'],
        summary='Renovar access token',
        description=(
            'Lee el `refresh_token` de la cookie HttpOnly y emite un nuevo `access_token` '
            '(también en cookie HttpOnly). No requiere body.\n\n'
            'Si `ROTATE_REFRESH_TOKENS=True` también se renueva el refresh token.'
        ),
        request=None,
        responses={
            200: inline_serializer(
                name='RefreshResponse',
                fields={'message': drf_serializers.CharField()},
            ),
            401: inline_serializer(
                name='RefreshUnauthorized',
                fields={'error': drf_serializers.CharField()},
            ),
        },
    )
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {'error': 'No se encontró refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            access  = str(refresh.access_token)

            response = Response({'message': 'Token renovado.'})

            # Sobreescribimos la cookie del access con el nuevo token
            response.set_cookie(
                key      = 'access_token',
                value    = access,
                httponly = True,
                secure   = settings.COOKIE_SECURE,
                samesite = settings.COOKIE_SAMESITE,
                max_age  = 15 * 60,
            )

            # Si ROTATE_REFRESH_TOKENS=True, también actualizamos el refresh
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS'):
                response.set_cookie(
                    key      = 'refresh_token',
                    value    = str(refresh),
                    httponly = True,
                    secure   = settings.COOKIE_SECURE,
                    samesite = settings.COOKIE_SAMESITE,
                    max_age  = 24 * 60 * 60,
                )

            return response

        except TokenError:
            return Response(
                {'error': 'Refresh token inválido o expirado.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        

class MeView(APIView):
    """
    GET /auth/me/
    Valida la sesión activa y devuelve los datos del usuario autenticado.
    El frontend debe llamar este endpoint al cargar la app para reconstruir
    la sesión de forma segura — no desde localStorage ni decodificando el token localmente.
    Si la cookie es inválida o expiró, devuelve 401 y el frontend redirige al login.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Autenticación'],
        summary='Sesión activa — datos del usuario',
        description=(
            'Valida el `access_token` de la cookie y devuelve los datos del usuario autenticado.\n\n'
            'El frontend debe llamar este endpoint al iniciar la aplicación para reconstruir '
            'la sesión sin leer localStorage ni decodificar el token en el cliente.\n\n'
            'Retorna 401 si la cookie expiró o no existe.'
        ),
        responses={
            200: inline_serializer(
                name='MeResponse',
                fields={
                    'id':       drf_serializers.IntegerField(),
                    'email':    drf_serializers.EmailField(),
                    'username': drf_serializers.CharField(),
                    'role':     drf_serializers.ChoiceField(choices=['SinRol', 'Ind', 'Com', 'Pro']),
                    'is_admin': drf_serializers.BooleanField(),
                },
            ),
            401: inline_serializer(
                name='MeUnauthorized',
                fields={'detail': drf_serializers.CharField()},
            ),
        },
    )
    def get(self, request):
        user = request.user
        return Response({
            'id':       user.id,
            'email':    user.email,
            'username': user.username,
            'role':     user.role,
            'is_admin': user.is_admin,
        })