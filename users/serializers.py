from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Genera el token base
        token = super().get_token(user)
        
        # Le inyectas tus campos personalizados
        token['role'] = user.role
        token['is_admin'] = user.is_admin
        token['email'] = user.email
        
        return token