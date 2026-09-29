import uuid
from datetime import datetime
from django.db import transaction




class AppointmentIDService:
    """Handles generation of unique appointment IDs."""

    PREFIX = "APT"
    MAX_RETRIES = 5

    @classmethod
    def generate(cls, depart_code):
        """
        Generate a unique appointment ID using clinic, date, and patient info.
        Ensures uniqueness by retrying on collision.
        """
        for _ in range(cls.MAX_RETRIES):
            candidate = cls._build_id(depart_code)
            if not cls._exists(candidate):
                return candidate
        raise RuntimeError("Could not generate unique appointment ID")

    @classmethod
    def _build_id(cls, depart_code):
        date_part = datetime.now().strftime("%Y%m%d")
        uuid_part = uuid.uuid4().hex[:6].upper()
        return f"{cls.PREFIX}-{depart_code}-{date_part}-{uuid_part}"

    @classmethod
    def _exists(cls, appointment_number):
        from appointments.models import Appointment
        return Appointment.objects.filter(
            appointment_number=appointment_number
        ).exists()


class AppointmentBookingService:
    """
        * = "everything after me must be passed by keyword."
        create_appointment(validated_data={"x": 1})   # ✅ works
        create_appointment({"x": 1})                  # ❌ TypeError
    """

    @staticmethod
    def create_appointment(*, validated_data):
        from appointments.models import AppointmentSlot, Appointment

        with transaction.atomic():
            slot = validated_data["time_slot"]

            #Lock the slot row
            slot = (
                AppointmentSlot.objects
                .select_for_update()
                .get(pk=slot.pk)
            )

            # Check availability again
            if not slot.is_available:
                raise ValueError("This appointment slot is no longer available.")

            # Create appointment
            appointment = Appointment.objects.create(
                **validated_data
            )

            # Mark slot unavailable
            slot.is_available = False
            slot.save(update_fields=["is_available"])
            
            return appointment