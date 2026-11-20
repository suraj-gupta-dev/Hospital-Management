from django_filters import FilterSet

from .models import AuditLog


class AuditLogFilterSet(FilterSet):
    class Meta:
        model = AuditLog
        fields = {
            "action": ["exact", "iexact"],
            "actor": ["exact"],
            "content_type": ["exact"]
        }