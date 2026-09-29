from rest_framework import serializers
from datetime import timedelta

from .models import DoctorSchedule, Appointment, AppointmentSlot
from hospital.models import StaffDeparment



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
                raise serializers.ValidationError("This schedule overlaps with an existing one for the same doctor and day.")
        return attrs


class AppointmentSlotSerializer(serializers.ModelSerializer):
    SLOT_GAP = timedelta(minutes=15)

    class Meta:
        model = AppointmentSlot
        fields = ["doctor", "date", "appointment_time", "is_available"]
        read_only_fields = ["is_available"]

    def _to_dt(self, t):
        return timedelta(hours=t.hour, minutes=t.minute)

    def validate(self, attrs):
        last_appoint_slot = AppointmentSlot.objects.last()
        if last_appoint_slot:
            gap = self._to_dt(attrs["appointment_time"]) - self._to_dt(last_appoint_slot.appointment_time)
            if gap != self.SLOT_GAP:
                raise serializers.ValidationError("Gap between 2 appointment slot should be 15.")
        return attrs
    

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "appointment_number",
            "patient",
            "doctor",
            "department",
            "appointment_date",
            "appointment_slot",
            "appointment_type",
            "status",
            "reason",
            "notes",
            "cancelled_at",
            "cancellation_reason",
        ]
        read_only_fields = [ "appointment_number", "status", "cancelled_at", "cancellation_reason"]

    def validate(self, attrs):
        department = attrs["department"]
        doctor = attrs["doctor"]
        slot = attrs["appointment_slot"]

        # 1. Doctor → Department
        is_assinged = StaffDeparment.objects.filter(
            staff=doctor.user,
            department=department,
            is_active=True
        )

        if not is_assinged:
            raise serializers.ValidationError({
                "department": (
                    "This doctor is not assigned to the selected department."
                )
            })

        # 2. Slot → Doctor
        if slot.doctor.id != doctor.id:
            raise serializers.ValidationError({
                "slot": "This appointment slot does not belong to the selected doctor."
            })

        # 3. Check if there is a apoointment already exist for same day.
        have_appointment = Appointment.objects.filter(
            patient=attrs["patient"],
            doctor=doctor,
            department=department,
            appointment_date=attrs["appointment_date"],
        )

        if have_appointment.exists():
            raise serializers.ValidationError({
                "slot": (
                    "This patient already has an appointment "
                    "at this time."
                )
            })
        
        return attrs