from django_filters import rest_framework as filters

from accounts.models import PatientProfile, DoctorProfile




class PatientFilterSet(filters.FilterSet):
    city = filters.CharFilter(field_name="patient_profile__city", lookup_expr="iexact")
    state = filters.CharFilter(field_name="patient_profile__state", lookup_expr="iexact")
    country = filters.CharFilter(field_name="patient_profile__country", lookup_expr="iexact")
    patient_id = filters.CharFilter(field_name="patient_profile__patient_id", lookup_expr="iexact")
    gender = filters.ChoiceFilter(field_name="patient_profile__gender", choices=PatientProfile.GENDER_CHOICES)
    blood_group = filters.ChoiceFilter(
        field_name="patient_profile__blood_group",
        choices=PatientProfile.BloodGroup.choices
    )


class DoctorFilterSet(filters.FilterSet):
    is_available = filters.BooleanFilter(field_name="is_available")

    class Meta:
        model = DoctorProfile
        fields = {
            "doctor_id": ["exact"],
            "designation": ["iexact"],
            "employment_type": ["iexact"],
            "specialization": ["iexact", "in"],
            "experience_years": ["exact", "range", "in", "gt", "lt"],
            "consultation_fee": ["exact", "range", "in", "gt", "lt"],
        }