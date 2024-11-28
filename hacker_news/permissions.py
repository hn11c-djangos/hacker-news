# apis/permissions.py
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed

class HasAuthToken(BasePermission):
    def has_permission(self, request, view):
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            raise AuthenticationFailed(detail="Your request has no user auth. token", code=401)
        return True

class TokenRequiredForUnsafeMethods(BasePermission):
    """
    solo permite solicitudes seguras (GET, OPTIONS, HEAD) sin token de autenticación
    """
    def has_permission(self, request, view):
        # Para solicitudes seguras, permitir sin token de autenticación
        if request.method in ['GET', 'OPTIONS', 'HEAD']:
            return True
        # Para solicitudes inseguras, requerir token de autenticación
        return request.user and request.user.is_authenticated