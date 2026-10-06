import uuid
import logging

from datetime import datetime
from django.utils import timezone
from django.db import transaction
from rest_framework import serializers

logg = logging.getLogger(__name__)




class AppointmentServices:
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

    """
        * = "everything after me must be passed by keyword."
        create_appointment(validated_data={"x": 1})   # ✅ works
        create_appointment({"x": 1})                  # ❌ TypeError
    """

    @staticmethod
    def create_appointment(*, validated_data):
        from appointments.models import AppointmentSlot, Appointment

        with transaction.atomic():
            slot = validated_data["slot"]

            #Lock the slot row
            slot = (
                AppointmentSlot.objects
                .select_for_update()
                .get(pk=slot.pk)
            )

            # Create appointment
            appointment = Appointment.objects.create(
                **validated_data,
                status=Appointment.Status.CONFIRMED
            )
            return appointment

    @staticmethod
    def cancel_appointment(*, appoint_id, reason):
        from appointments.models import Appointment
        
        with transaction.atomic():
            appointment = (
                Appointment.objects.select_for_update()
                .get(appointment_number=appoint_id)
            )

            if appointment.Status == Appointment.Status.CANCELLED:
                raise serializers.ValidationError({
                    "detail": "Appointment is already cancelled."
                })
    
            if appointment.status == Appointment.Status.COMPLETED:
                raise serializers.ValidationError({"detail": "Completed appointments cannot be cancelled."})
    
            # Business rule: no cancelling in the past
            if appointment.appointment_date < timezone.localdate():
                raise serializers.ValidationError({"detail": "Past appointments cannot be cancelled."})

            appointment.status = Appointment.Status.CANCELLED
            appointment.cancellation_reason = reason
            appointment.cancelled_at = timezone.now()

            appointment.save(update_fields=["cancellation_reason", "cancelled_at", "status"])

        return appointment
