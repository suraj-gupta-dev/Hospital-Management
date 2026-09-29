from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "HA":
            return True
        return request.method in SAFE_METHODS