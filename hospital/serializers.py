from rest_framework import serializers

from accounts.models import User
from .models import Department, StaffDeparment




class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class StaffDepartmentSerializer(serializers.ModelSerializer):
    ALLOWED_ROLES = ["DOC", "NUR", "REC", "PHA", "LT", "CAS"]
        
    class Meta:
        model = StaffDeparment
        fields = ["staff", "department", "is_primary", "is_active"]


    def validate_staff(self, user):
        if not user.is_active:
            raise serializers.ValidationError(
                "This user is inactive."
            )

        if user.role not in self.ALLOWED_ROLES:
            raise serializers.ValidationError(
                "This user does not have a staff role and "
                "cannot be assigned to a department."
            )
        return user
