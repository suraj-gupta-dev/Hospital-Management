from rest_framework import serializers

from accounts.models import User
from .models import Hospital, Department




class HospitalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove the field you want to move to last
        


