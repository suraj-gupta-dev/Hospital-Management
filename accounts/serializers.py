import re
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers


from .models import (
    User,
    DoctorProfile, PatientProfile,
    NurseProfile, ReceptionistProfile,
    PharmacistProfile, LabTechnicianProfile,
    CashierProfile
)




class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        ]

    def validate_username(self, value):
        """Validate username for allowed characters"""
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and @/./+/-/_ characters."
            )
        return value

    def validate(self, attrs):
        """Validate password match and additional constraints"""
        # Check password match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        
        # Check email and username are not same
        if attrs.get('username') == attrs.get('email'):
            raise serializers.ValidationError({
                "username": "Username cannot be same as email."
            })
        
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})

    # for just testing purpose i am listing all email so that i can loging with selected email.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        emails = User.objects.all().values_list("email", flat=True)
        self.fields["email"] = serializers.ChoiceField(
            choices=[(email, email) for email in emails],
            required=True
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        # Validate password strength using Django's validators
        validate_password(value)
        return value

    def validate(self, attrs):
        # Check if new password and confirm password match
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "The two password fields did not match."})

        # Check if new password is same as old password
        if attrs["new_password"] == attrs["old_password"]:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as your current password."})

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "username",
            "role",
            "first_name",
            "last_name",
        ]


class BaseProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "id",
            "date_of_birth",
            "gender",
            "profile_picture",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "country",
            "postal_code",
            "emergency_contact_name",
            "emergency_contact_phone",
            "created_at",
            "updated_at",
            "user",
        ]
        read_only_fields = [
            "id",
            "profile_picture",
            "created_at",
            "updated_at",
            "user",
        ]


class DoctorProfileSerializer(BaseProfileSerializer):
    class Meta:
        model = DoctorProfile
        fields = BaseProfileSerializer.Meta.fields + [
            "registration_number",
            "specialization", "qualification", "experience_years",
            "consultation_fee", "bio", "is_available",
        ]


class PatientProfileSerializer(BaseProfileSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = PatientProfile
        fields = ["full_name", "email"] + BaseProfileSerializer.Meta.fields + [
            "patient_number", "blood_group",
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class PatientProfileCreateSerializer(serializers.ModelSerializer):
    class PatientProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = PatientProfile
            fields = [
                "date_of_birth",
                "gender",
                "patient_number",
                "blood_group",
            ]
    patient_profile = PatientProfileSerializer()
    password = serializers.CharField(style={"input_type": "password"}, required=True, write_only=True)
    confirm_password = serializers.CharField(style={"input_type": "password"}, required=True, write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "confirm_password", "patient_profile"]

    def validate(self, attrs):
        """Validate password match and additional constraints"""
        # Check password match
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data):
        profile = validated_data.pop("patient_profile")
        print(validated_data)
        user = User.objects.create_user_with_profile(**validated_data, profile=profile)
        return user


class NurseProfileSerializer(BaseProfileSerializer):
    class Meta:
        model = NurseProfile
        fields = BaseProfileSerializer.Meta.fields + [
            "registration_number",
            "qualification", "experience_years",
        ]


class ReceptionistProfileSerializer(BaseProfileSerializer):
    class Meta:
        model = ReceptionistProfile
        fields = BaseProfileSerializer.Meta.fields + [
            "employee_id", "qualification",
            "joining_date",
        ]


class PharmacistProfileSerializer(BaseProfileSerializer):
    class Meta:
        model = PharmacistProfile
        fields = BaseProfileSerializer.Meta.fields + [
            "license_number", "qualification",
            "experience_years", "joining_date",
        ]


class LabTechnicianProfileSerializer(BaseProfileSerializer):
    class Meta:
        model = LabTechnicianProfile
        fields = BaseProfileSerializer.Meta.fields + [
            "employee_id", "qualification",
            "specialization", "experience_years", "joining_date",
        ]


class CashierProfileSerializer(BaseProfileSerializer):
    class Meta:
        model = CashierProfile
        fields = BaseProfileSerializer.Meta.fields + [
            "employee_id", "joining_date",
        ]

