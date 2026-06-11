from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):

    message = "Acceso denegado: se requiere ser administrador."

    def has_permission(self, request, view):
        # El usuario debe estar autenticado Y tener is_admin=True
        return (
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsComercializacionAdmin(BasePermission):

    message = "Acceso denegado: se requiere ser administrador del área de Comercialización."

    def has_permission(self, request, view):
        # El usuario debe estar autenticado, tener is_admin=True Y role='Com'
        return (
            request.user.is_authenticated and
            request.user.is_admin and
            request.user.role == 'Com'      # 'Com' es el value definido en CustomUser.Roles
        )
    
class IsComercializacionUser(BasePermission):

    message = "Acceso denegado: se requiere ser del área de Comercialización."

    def has_permission(self, request, view):
        # El usuario debe estar autenticado, tener Y role='Com'
        return (
            request.user.is_authenticated and
            request.user.role == 'Com'      # 'Com' es el value definido en CustomUser.Roles
        )
    
class IsProveedor(BasePermission):
    """
    Solo usuarios con role='Pro' que tengan un Proveedor asociado.
    Usado en: consulta de asignaciones propias del proveedor.
    """
    message = "Acceso denegado: se requiere ser un proveedor registrado."

    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.role == 'Pro'):
            return False
        try:
            request.user.proveedor
        except request.user.__class__.proveedor.RelatedObjectDoesNotExist:
            self.message = "El usuario no tiene un perfil de proveedor asociado."
            return False
        return True


class IsIndustrializacionUser(BasePermission):

    message = "Acceso denegado: se requiere ser del área de Industrialización."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'Ind'
        )


class IsIndustrializacionAdmin(BasePermission):

    message = "Acceso denegado: se requiere ser administrador del área de Industrialización."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_admin and
            request.user.role == 'Ind'
        )


class IsSistemas(BasePermission):
    """
    Solo usuarios con role='IT'.
    Usado en: endpoints de administración del sistema.
    """
    message = "Acceso denegado: se requiere ser un usuario del área de Sistemas."
 
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'IT'
        )
