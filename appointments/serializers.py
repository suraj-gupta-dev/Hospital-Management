import logging

from rest_framework import serializers
from datetime import timedelta

from .models import DoctorSchedule, Appointment, AppointmentSlot
from hospital.models import StaffDepartment

logger = logging.getLogger(__name__)


class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = [
            "id",
            "doctor",
            "day_of_week",
            "start_time",
            "end_time",
            "is_active"
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        start = attrs["start_time"]
        end = attrs["end_time"]

        if start is None or end is None:
            raise serializers.ValidationError("start_time and end_time are required.")
        if start >= end:
            raise serializers.ValidationError("start_time must be before end_time.")

        # When updating, exclude THIS row from the check (it would match itself)
        if self.instance is None:
            overlapping = DoctorSchedule.objects.filter(
                doctor=attrs.get("doctor", None),
                day_of_week=attrs.get("day_of_week"),
                is_active=True
            )
            if overlapping.exists():
                raise serializers.ValidationError(
                    "This schedule overlaps with an existing one for the same doctor and day."
                )
        return attrs


class AppointmentSlotSerializer(serializers.ModelSerializer):
    SLOT_GAP = 15

    class Meta:
        model = AppointmentSlot
        fields = ["appointment_time"]

    def _to_dt(self, t):
        return timedelta(hours=t.hour, minutes=t.minute)

    def validate(self, attrs):
        last_appoint_slot = AppointmentSlot.objects.last()

        if last_appoint_slot:
            gap = self._to_dt(attrs["appointment_time"]) - self._to_dt(last_appoint_slot.appointment_time)
            if gap != self.SLOT_GAP:
                raise serializers.ValidationError("Gap between 2 appointment slot should be 15.")
        return attrs


class PatientAppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "doctor",
            "department",
            "slot",
            "appointment_date",
            "appointment_type",
            "reason",
        ]


class ReceptionistAppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "patient",
            "doctor",
            "department",
            "slot",
            "appointment_date",
            "appointment_type",
            "reason",
        ]


class RescheduleAppointmentSerializer(serializers.Serializer):
    appointment_date = serializers.DateField()
    slot = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentSlot.objects.filter(is_active=True)
    )
    

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.full_name", read_only=True)
    slot_time = serializers.CharField(source="slot.appointment_time", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "patient_name", "doctor_name",
            "appointment_number", "patient",
            "doctor", "department", "department_name",
            "appointment_date", "slot",  "slot_time",
            "appointment_type", "status",
            "reason", "notes",
            "cancelled_at", "cancellation_reason",
        ]

        read_only_fields = [
            "patient_name", "doctor_name", "slot_time",
            "appointment_number", "status", "cancelled_at",
            "cancellation_reason", "patient", "department_name",
        ]

    def validate(self, attrs):
        department = attrs["department"]
        doctor = attrs["doctor"]
        patient_profile = self.context.get("patient") 

        # 1. Doctor → Department
        is_assigned = StaffDepartment.objects.filter(
            staff=doctor.user,
            department=department,
            is_active=True
        )

        if not is_assigned:
            logger.error(f"{doctor} doesn't belong to {department}")
            raise serializers.ValidationError({
                "department": (
                    "This doctor is not assigned to the selected department."
                )
            })

        # 3. Check if there is a appointment already exist for same day.
        have_appointment = Appointment.objects.filter(
            patient = patient_profile,
            doctor=doctor,
            department=department,
            appointment_date=attrs["appointment_date"],
        ).exclude(
            status=Appointment.Status.CANCELLED
        )

        if have_appointment.exists():
            logger.error(f"{patient_profile} already have appointment with-{doctor}")
            raise serializers.ValidationError({
                "slot": (
                    "This patient already has an appointment "
                    "at this time."
                )
            })
        return attrs

class CancelAppointmentSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )