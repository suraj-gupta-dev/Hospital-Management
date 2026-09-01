import re
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User




class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "password2"]

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
        if attrs['password'] != attrs['password2']:
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
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})


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