import re
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