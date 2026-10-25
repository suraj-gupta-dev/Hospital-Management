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

    # def validate_username(self, value):
    #     """Validate username for allowed characters"""
    #     if not re.match(r'^[\w.@+-]+$', value):
    #         raise serializers.ValidationError(
    #             "Username can only contain letters, numbers, and @/./+/-/_ characters."
    #         )
    #     return value

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

    # for just testing purpose i am listing all email so that i can logging with selected email.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        emails = User.objects.all().order_by("email").values_list("email", flat=True)
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
            "user_id",
            "email",
            "phone_number",
            "username",
            "role",
            "first_name",
            "last_name",
        ]


class BaseProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source="user.user_id", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        fields = [
            "user_id", "first_name", "last_name", "email", "phone_number",
            "date_of_birth", "gender",
            "profile_picture", "address_line_1",
            "address_line_2", "city",
            "state", "country",
            "postal_code", "emergency_contact_name",
            "emergency_contact_phone", "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "profile_picture",
            "created_at",
            "updated_at",
        ]


class DoctorProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = DoctorProfile
        fields = ["doctor_id"] + BaseProfileSerializer.Meta.fields + [
            "registration_number", "specialization",
            "qualification", "experience_years",
            "consultation_fee", "bio", "is_available",
        ]



class PatientProfileSerializer(BaseProfileSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta(BaseProfileSerializer.Meta):
        model = PatientProfile
        fields = ["patient_id"] + BaseProfileSerializer.Meta.fields + [
            "blood_group", "full_name"
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    

class ReceptCreatePatientSerializer(serializers.ModelSerializer):
    class PatientProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = PatientProfile
            fields = [
                "date_of_birth", "gender",
                "patient_id", "blood_group",
                "gender", "profile_picture",
                "address_line_1", "address_line_2",
                "city", "state",
                "country", "postal_code",
                "emergency_contact_phone",
                "emergency_contact_name"
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
    class Meta(BaseProfileSerializer.Meta):
        model = NurseProfile
        fields = ["nurse_id"] + BaseProfileSerializer.Meta.fields + [
            "registration_number",
            "qualification", "experience_years",
        ]


class ReceptionistProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = ReceptionistProfile
        fields = ["recept_id"] + BaseProfileSerializer.Meta.fields + [
            "qualification", "joining_date",
        ]


class PharmacistProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = PharmacistProfile
        fields = ["pharm_id"] + BaseProfileSerializer.Meta.fields + [
            "license_number", "qualification",
            "experience_years", "joining_date",
        ]


class LabTechnicianProfileSerializer(BaseProfileSerializer):
    class MetaMeta(BaseProfileSerializer.Meta):
        model = LabTechnicianProfile
        fields = ["lab_tech_id"] + BaseProfileSerializer.Meta.fields + [
            "qualification",
            "specialization", "experience_years", "joining_date",
        ]


class CashierProfileSerializer(BaseProfileSerializer):
    class MetaMeta(BaseProfileSerializer.Meta):
        model = CashierProfile
        fields = ["cash_id"] + BaseProfileSerializer.Meta.fields + [
            "joining_date",
        ]


"""
    Admin-only staff creation: creates User + role-specific profile in ONE transaction.
    
    Put this file next to views.py / serializers.py in your accounts app.
    Request (POST /api/staff/), JSON:
    
    {
    "role": "DOC",
    "email": "dr.sharma@hospital.com",
    "first_name": "Anita",
    "last_name": "Sharma",
    "phone_number": "9876543210",
    "password": "Str0ng!Pass123",
    "confirm_password": "Str0ng!Pass123",
    "profile": {
        "gender": "F",
        "registration_number": "MCI-12345",
        "specialization": "Cardiology",
        "qualification": "MBBS, MD",
        "designation": "CONSULTANT",
        "employment_type": "FULL_TIME",
        "consultation_fee": "800.00"
    }
    }
"""

STAFF_PROFILE_MAP = {
    User.RoleChoices.DOCTOR: (DoctorProfile, DoctorProfileSerializer),
    User.RoleChoices.NURSE: (NurseProfile, NurseProfileSerializer),
    User.RoleChoices.CASHIER: (CashierProfile, CashierProfileSerializer),
    User.RoleChoices.LAB_TECHNICIAN: (LabTechnicianProfile, LabTechnicianProfileSerializer),
    User.RoleChoices.PHARMACIST: (PharmacistProfile, PharmacistProfileSerializer),
    User.RoleChoices.RECEPTIONIST: (ReceptionistProfile, ReceptionistProfileSerializer),
}


class StaffCreateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[(role.value, role.label) for role in STAFF_PROFILE_MAP])
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(min_length=10, max_length=12, required=True)
    password = serializers.CharField(style={"input_type": "password"}, required=True, write_only=True)
    confirm_password = serializers.CharField(style={"input_type": "password"}, required=True, write_only=True)
    profile = serializers.DictField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})

        # Validate `profile` with the serializer that matches the chosen role.
        # `user` is read-only in those serializers, so it is not required here.

        _, serializer_profile_cls = STAFF_PROFILE_MAP[attrs["role"]]
        profile_serializer = serializer_profile_cls(data=attrs["profile"], context=self.context)
        if not profile_serializer.is_valid():
            raise serializers.ValidationError({"profile": profile_serializer.errors})

        attrs["profile"] = profile_serializer.validated_data
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        profile = validated_data.pop("profile")
        role = validated_data["role"]
        profile_model, _ = STAFF_PROFILE_MAP[role]

        # Assumes UserManager.create_user(email, password, **extra_fields)
        user = User.objects.create(**validated_data, is_verified=True)  # created by an admin, so no email verification step
        profile = profile_model.objects.create(user=user, **profile)
        return {"user": user, "profile": profile}
    

    
