# general/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.conf import settings


class LoginView(APIView):
    """
    POST /auth/login/
    Recibe email y password, devuelve los tokens en cookies HttpOnly
    El body de respuesta NO incluye los tokens — van solo en las cookies
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope   = 'login'

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

    def get(self, request):
        user = request.user
        return Response({
            'id':       user.id,
            'email':    user.email,
            'username': user.username,
            'role':     user.role,
            'is_admin': user.is_admin,
        })