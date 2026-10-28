from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS
from .models import User



class IsAnonymousUser(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsOwnerOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return request.method in ["GET", "PUT", "PATCH"]
        

class IsDoctorReceptOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "HA":
            return True        

        if request.user.role in ["REC", "DOC"]:
            return request.method in SAFE_METHODS
        


"""------------------Reusable Base Permission------------------"""


class RoleMatrixPermission(BasePermission):
    """
    Admin → full access.
    Everyone else → method must be in ROLE_METHODS[role].
    Roles in OWNER_ROLES are additionally restricted to their own objects.
    """

    ADMIN_ROLE = "HA"
    ROLE_METHODS = {}
    OWNER_ROLES = set()

    def _role(self, request):
        return getattr(request.user, "role", None)

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role = self._role(request)
        if role == self.ADMIN_ROLE:
            return True

        return request.method in self.ROLE_METHODS.get(role, set())


class PatientAccessPermission(RoleMatrixPermission):
    ROLE_METHODS = {
        "HA":  {"GET", "POST", "PUT", "PATCH", "DELETE"},
        "REC": {"GET", "POST", "PUT", "PATCH"},
        "PAT": {"GET"},
        "DOC": {"GET", "PUT", "PATCH"},
        "NUR": {"GET"},
        "LT":  {"GET"},
        "PHA": {"GET"},
        "CAS": {"GET"},
    }
    OWNER_ROLES = {"PAT"}