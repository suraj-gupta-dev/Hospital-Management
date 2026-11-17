from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import AuditLog
from .serializers import AuditLogSerializer
from .permissions import IsHospitalAdmin
from .filters import AuditLogFilterSet



class ReadOnlyAuditLogView(ListModelMixin, RetrieveModelMixin, GenericAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsHospitalAdmin]

    def get(self, request, *args, **kwargs):
        # If a primary key is provided in the URL, retrieve a single object
        if "pk" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

"========================ViewSet======================"

# Second Approach using GenericViewSet
# GenericViewSet and add the required mixins.
# This gives you a viewset that automatically handles GET requests for both
# the list and detail routes when registered with a router.

class ReadOnlyAuditLogViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = AuditLog.objects.filter()
    serializer_class = AuditLogSerializer

"========================ViewSet============================"

# A Simpler Alternative: ReadOnlyModelViewSet
# DRF provides a built-in class that already combines these exact mixins for you:

class ReadOnlyAuditLogViewSet(ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = AuditLogFilterSet
    search_fields = ["actor__email", "object_repr", "description", "request_path"]
    ordering_fields = ["action", "timestamp"]

    def get_queryset(self):
        queryset = AuditLog.objects.select_related(
            "actor",
            "content_type"
        )

        # Optional date filtering
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(
                timestamp__date__gte=start_date
            )
            
        if end_date:
            queryset.filter(
                timestamp__date__lte=end_date
            )

        return queryset