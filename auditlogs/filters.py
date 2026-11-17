import django_filters

from .models import AuditLog


class AuditLogFilterSet(django_filters.FilterSet):
    class Meta:
        model = AuditLog
        fields = {
            "action": ["exact", "iexact"],
        }