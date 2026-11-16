from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType




class AuditLog(models.Model):
    class ActionChoices(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password Change"
        PROFILE_PICTURE_UPDATE = "PROFILE_PICTURE_UPDATE", "Profile Picture Update"
        FAILED_LOGIN = "FAILED_LOGIN", "Failed Login"

    # Who performed the action?
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    # What action was performed?
    action = models.CharField(
        max_length=30,
        choices=ActionChoices.choices,
        db_index=True
    )

    # Which model/object was affected?
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    object_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")
    object_repr = models.CharField(max_length=255, blank=True)

    # Changed fields and their non-sensitive values
    changes = models.JSONField(default=dict, blank=True)

    # Request information
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)

    # When the action happened
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["actor", "-timestamp"]),
            models.Index(fields=["action", "-timestamp"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.actor} - {self.action} - {self.timestamp}"

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Audit logs cannot be modified.")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Audit logs cannot be deleted.")


    