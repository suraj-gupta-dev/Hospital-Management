
from django.contrib.contenttypes.models import ContentType

from .models import AuditLog


# Fields that must never be stored in audit change snapshots.
SENSITIVE_FIELDS = {
    "password",
    "last_login",
    "profile_picture",
    "blood_group",
    "date_of_birth",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "country",
    "postal_code",
    "emergency_contact_phone",
    "emergency_contact_name",
}

class AuditLogsServices:
    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address.

        Only trust X-Forwarded-For when your reverse proxy
        is configured to remove untrusted incoming values.
        """
        if not request:
            return None
        return request.Meta.get("REMOTE_ADDR")

    @staticmethod
    def get_model_snapshot(instance):
        """
        Capture non-sensitive fields from a model instance.
        """
        snapshot = {}
        if not instance:
            return snapshot

        for field in instance._meta.concrete_fields:
            field_name = field.name

            if field_name in SENSITIVE_FIELDS:
                continue

            if field.is_relation:
                continue

            value = getattr(instance, field_name, None)
            if value is None:
                snapshot[field_name] = None
            else:
                snapshot[field_name] = str(value)

        return snapshot

    @staticmethod
    def get_changes(old_data: dict, new_data: dict):
        """
        Compare old and new model values.
        set(old_data) | set(new_data) return the set of unique dict keys.
        """
        changes = {}

        for field in set(old_data) | set(new_data):
            old_value = old_data.get(field)
            new_value = new_data.get(field)

            if old_value != new_value:
                changes[field] = {
                    "old": old_value,
                    "new": new_value
                }
        return changes

    @staticmethod
    def create_audit_log(*, request=None, action, instance=None, description="", changes=None, actor=None):
        """
        Centralized audit log creation.
        """
        if action is None and request:
            if request.user.is_authenticated:
                actor = request.user

        content_type = None
        object_id = None
        object_repr = ""

        if instance is not None:
            """
            for_concrete_model=True (the default) → always returns the concrete model's content type.
            This is what GenericForeignKey uses by default, so generic relations resolve to the real table.
            for_concrete_model=False → returns the proxy model's own content type if the instance is a proxy.
            """
            content_type = ContentType.objects.get_for_model(
                instance,
                for_concrete_model=False
            )
            object_id = str(instance.pk)
            object_repr = str(instance)[:255]

            return AuditLog.objects.create(
                actor=actor,
                action=action,
                content_type=content_type,
                object_id=object_id,
                object_repr=object_repr,
                changes=changes or {},
                user_agent=(
                    request.META.get("HTTP_USER_AGENT")[:1000]
                    if request else ""
                ),
                request_method=request.method if request else "",
                request_path=request.path[:500] if request else "",
                description=description
            )

    @staticmethod
    def log_model_create(request, instance, description=""):
        """
        Record model creation.
        """
        return AuditLogsServices.create_audit_log(
            request=request,
            instance=instance,
            description=description or f"{instance._meta.verbose_name} created.",
            action=AuditLog.ActionChoices.CREATE
        )

    @staticmethod
    def log_model_update(request, instance, old_data, description=""):
        """
        Record model update.
        """
        new_data = AuditLogsServices.get_model_snapshot(instance)
        changes = AuditLogsServices.get_changes(old_data, new_data)

        if not changes:
            return None

        return AuditLogsServices.create_audit_log(
            request=request,
            action=AuditLog.ActionChoices.UPDATE,
            instance=instance,
            changes=changes,
            description=description or f"{instance._meta.verbose_name} update."
        )

    @staticmethod
    def log_model_delete(request, instance, description=""):
        """
        Record model deletion before deleting the object.
        """
        return AuditLogsServices.create_audit_log(
            request=request,
            action=AuditLog.ActionChoices.DELETE,
            instance=instance,
            changes={
                "delete": True
            },
            description=description or f"{instance._meta.verbose_name} deleted."
        )

