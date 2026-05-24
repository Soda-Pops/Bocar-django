# general/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CookieJWTAuthentication(JWTAuthentication):
    """
    Extiende JWTAuthentication para leer el access token
    de la cookie HttpOnly en lugar del header Authorization
    """
    def authenticate(self, request):
        # Intentamos leer el token de la cookie
        access_token = request.COOKIES.get('access_token')

        if access_token is None:
            # Si no hay cookie, intentamos el header normal como fallback
            return super().authenticate(request)

        # Validamos el token con la lógica base de SimpleJWT
        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            return None
        
class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'users.authentication.CookieJWTAuthentication'
    name = 'CookieJWT'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'access_token',
            'description': 'Token JWT enviado via cookie HttpOnly',
        }