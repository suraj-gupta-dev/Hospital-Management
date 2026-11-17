from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "actor", "action", "object_repr", "ip_address", "timestamp"
    ]

    list_filter = [
        "action", "timestamp"
    ]

    search_fields = [
        "actor__email",
        "object_repr",
        "description"
    ]

    readonly_fields = [field.name for field in AuditLog._meta.fields]

    ordering = ["timestamp"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj = None):
        return False

    def has_delete_permission(self, request, obj = None):
        return False