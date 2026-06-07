from rest_framework.permissions import BasePermission


class IsChatbotAllowed(BasePermission):
    message = "Tu cuenta no tiene un rol asignado. Contacta al administrador."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role != 'SinRol'
        )
