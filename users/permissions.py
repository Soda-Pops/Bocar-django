from rest_framework.permissions import BasePermission


# ─────────────────────────────────────────────────────────────────────────────
# PERMISO 1: Solo usuarios con is_admin=True
#
# Usado en:
#   - Borrado lógico de RFQ_Mold    → PATCH /rfq-molds/<id>/delete/
#   - Borrado lógico de RFQ_Trimming → PATCH /rfq-trimmings/<id>/delete/
# ─────────────────────────────────────────────────────────────────────────────
class IsAdminUser(BasePermission):

    message = "Acceso denegado: se requiere ser administrador."

    def has_permission(self, request, view):
        # El usuario debe estar autenticado Y tener is_admin=True
        return (
            request.user.is_authenticated and
            request.user.is_admin
        )


# ─────────────────────────────────────────────────────────────────────────────
# PERMISO 2: Solo usuarios con role='Com' Y is_admin=True
#
# Usado en:
#   - Ver solicitudes de edición pendientes de RFQ_Mold
#   - Aprobar solicitudes de edición de RFQ_Mold
#   - Ver solicitudes de edición pendientes de RFQ_Trimming
#   - Aprobar solicitudes de edición de RFQ_Trimming
# ─────────────────────────────────────────────────────────────────────────────
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