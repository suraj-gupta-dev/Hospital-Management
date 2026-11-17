from rest_framework import serializers
from .models import AuditLog



class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source="actor.email", read_only=True)
    actor_role = serializers.CharField(source="actor.role", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor",
            "actor_email",
            "actor_role",
            "action",
            "content_type",
            "object_id",
            "object_repr",
            "changes",
            "description",
            "ip_address",
            "user_agent",
            "request_method",
            "request_path",
            "timestamp",
        ]

        read_only_fields = fields