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
        

class IsDoctorRecepOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "HA":
            return True        

        if request.user.role == "REC":
            return request.method in SAFE_METHODS

        if request.user.role == "DOC":
            return request.method in ["GET", "PUT", "PATCH"]

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == "HA":
            return True

        return request.user == obj.user

class IsDocRecepNurseOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "HA":
            return True

        if request.user.role in ["REC", "NUR"]:
            return request.method in SAFE_METHODS

        if request.user.role == "DOC":
            return request.method in ["GET", "PUT", "PATCH"]
        



"""------------------Reusable Base Permission------------------"""


class RoleMatrixPermission(BasePermission):
    """
    Subclass and override these class attrs:
        ROLE_METHODS     : {role: {allowed HTTP methods}}
        OWNER_ROLES      : roles that can only access their own object
        ADMIN_ROLE       : the omnipotent role
    """
    ADMIN_ROLE = "HA"
    ROLE_METHODS = {}
    OWNER_ROLES = {"PAT"}

    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user:
            return False

        role = getattr(request.user, "role", None)
        if role == self.ADMIN_ROLE:
            return True

        allowed_methods = self.ROLE_METHODS.get(role, list())
        if request.method in allowed_methods:
            return True

    def has_object_permission(self, request, view, obj):
        role = getattr(request.user, "role", None)
        if role == self.ADMIN_ROLE:
            return True

        if role in self.OWNER_ROLES:
            return getattr(obj, "user", None) == request.user

        allowed_methods = self.ROLE_METHODS.get(role, list())
        if request.method in allowed_methods:
            return True


class PatientAccessPermission(RoleMatrixPermission):
    ROLE_METHODS = {
        "HA": ["GET", "POST", "PUT", "PATCH", "DELETE"],
        "REC": ["GET", "POST", "PUT", "PATCH"],
        "PAT": ["GET", "PUT", "PATCH"],
        "DOC": ["GET", "PUT", "PATCH"],
        "NUR": ["GET"],
        "LT": ["GET"],
        "PHA": ["GET"],
        "CAS": ["GET"],
    }
    OWNER_ROLES = {"PAT"}