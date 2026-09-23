from rest_framework.permissions import BasePermission


class IsStafforAdminOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "HA":
            return True
        return False