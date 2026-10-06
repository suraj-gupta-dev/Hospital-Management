from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsDoctorRecepOrAdmin(BasePermission):
    def has_permission(self, request, view):
        role = getattr(request.user, "role", None)
        if role == "HA":
            return True
        if role == "REC":
            return request.method in ["GET", "POST", "PUT", "PATCH"]
        if role == "DOC":
            return request.method in SAFE_METHODS
        if role == "PAT":
            return request.method in SAFE_METHODS or request.method == "POST"
        return False

    def has_object_permission(self, request, view, obj):
        role = request.user.role
        if role == "HA":
            return True
        if role == "DOC":
            return request.method in SAFE_METHODS
        if role == "REC":
            return request.method in ["GET", "POST", "PATCH", "PUT"]
        if role == "PAT":
            return request.method in ["GET", "POST"]
        return False