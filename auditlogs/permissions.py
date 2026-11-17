from rest_framework.permissions import BasePermission



class IsHospitalAdmin(BasePermission):
    def has_permission(self, request, view):
        User = request.user
        return bool(
            User
            and User.is_authenticated
            and (
                User.is_superuser
                or User.role == User.RoleChoices.HOSPITAL_ADMIN
            )
        )