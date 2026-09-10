from rest_framework import serializers


from accounts.models import User
from .models import HospitalAdminProfile, Hospital, Department, Branch



class HospitalAdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalAdminProfile
        fields = ["user", "employee_id", "designation", "joining_date"]


class HospitalBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["name", "code", "city", "state"]


class HospitalSerializer(serializers.ModelSerializer):
    branches = HospitalBranchSerializer(many=True, read_only=True)

    class Meta:
        model = Hospital
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove the field you want to move to last
        branches = data.pop("branches", None)

        # Re-add it at the end
        if branches is not None:
            data["branches"] = branches
        return data


class HospitalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ["name", "code", "registration_number"]


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        exclude = ["id", "created_at", "updated_at"]