from django_filters import FilterSet, DateFilter


from .models import Appointment



class AppointmentFilter(FilterSet):
    class Meta:
        model = Appointment
        fields = {
            "patient": ["exact"],
            "doctor": ["exact"],
            "appointment_date": ["exact", "lte", "gte", "lt", "gt"],
            "department": ["exact", "in"],
            "status": ["exact", "iexact", "in"]
        }
