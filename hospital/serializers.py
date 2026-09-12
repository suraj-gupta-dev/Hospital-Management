from rest_framework import serializers

from accounts.models import User
from .models import Department



class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


        


