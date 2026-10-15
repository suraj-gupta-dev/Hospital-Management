from django_filters import FilterSet
from rest_framework.filters import BaseFilterBackend

from .models import Appointment



class AppointmentFilter(FilterSet):
    class Meta:
        model = Appointment
        fields = {
            "patient": ["exact"],
            "doctor": ["exact"],
            "appointment_date": ["exact", "lte", "gte"],
            "department": ["exact", "in"],
            "status": ["exact", "iexact", "in"]
        }


class AvailableSlotFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return super().filter_queryset(request, queryset, view)