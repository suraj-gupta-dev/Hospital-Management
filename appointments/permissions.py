from rest_framework.permissions import BasePermission, SAFE_METHODS




class IsPatientOrReceptionist(BasePermission):
    message = "Only patients and receptionists can perform this action."

    def has_permission(self, request, view):
        role = getattr(request.user, "role", None)

        return role in ["PAT", "REC"]


class CanManageAppointment(BasePermission):
    """
    Patients can manage their own appointments.
    Receptionists can manage appointments for all patients.
    """

    def has_object_permission(self, request, view, obj):
        role = getattr(request.user, "role", None)

        if role == "REC":
            return True

        if role == "PAT":
            patient_profile = getattr(request.user, "patient_profile", None)

            return (
                patient_profile is not None
                and
                obj.patient_id == patient_profile.pk
            )

        return False