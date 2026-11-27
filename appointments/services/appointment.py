import uuid
import logging

from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db import transaction

from rest_framework.exceptions import ValidationError
from rest_framework import serializers

logger = logging.getLogger(__name__)


BOOKING_WINDOW_DAYS = getattr(
    settings,
    "APPOINTMENT_BOOKING_WINDOW_DAYS",
    7,
)


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
    def validate_booking_date(appointment_date):
        today = timezone.localdate()
        last_booking_date = today + timedelta(days=BOOKING_WINDOW_DAYS)

        if appointment_date <= today:
            raise ValidationError({
                "appointment_date": "Past dates cannot be booked."
            })

        if appointment_date > last_booking_date:
            raise ValidationError({
                "appointment_date": (
                    f"Appointments can only be booked "
                    f"within {BOOKING_WINDOW_DAYS} days."
                )
            })

    @staticmethod
    def validate_slot(*, slot, doctor, appointment_date):
        if not slot.is_active:
            raise ValidationError({
                "slot": "This appointment slot is inactive."
            })
        schedule = slot.schedule

        if not schedule.is_active:
            raise ValidationError({
                "slot": "Doctor schedule is inactive."
            })

        if schedule.doctor_id != doctor.doctor_id:
            raise ValidationError({
                "slot": "This slot does not belong to the selected doctor."
            })

        if schedule.day_of_week != appointment_date.weekday():
            raise ValidationError({
                "appointment_date": (
                    "This slot is not available on the selected weekday."
                )
            })

    @classmethod
    @transaction.atomic
    def create_appointment(cls, *, validated_data):
        from appointments.models import AppointmentSlot, Appointment

        slot = validated_data.get("slot")
        doctor = validated_data.get("doctor")
        appointment_date = validated_data.get("appointment_date")

        cls.validate_booking_date(appointment_date)

        #Lock the slot row
        slot = (
            AppointmentSlot.objects
            .select_for_update()
            .select_related("schedule")
            .get(pk=slot.pk)
        )

        cls.validate_slot(
            slot=slot,
            doctor=doctor,
            appointment_date=appointment_date
        )
            

        # Create appointment
        appointment = Appointment.objects.create(
            **validated_data,
            status=Appointment.Status.CONFIRMED
        )
        return appointment

    @classmethod
    @transaction.atomic
    def reschedule_appointment(cls, *, appointment_number, new_date, new_slot, requesting_user):
        from appointments.models import Appointment, AppointmentSlot

        appointment = (
            Appointment.objects
            .select_for_update()
            .prefetch_related("doctor", "slot", "appointment_date")
            .get(appointment_number=appointment_number)
        )

        if Appointment.Status in [Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW, Appointment.Status.COMPLETED]:
            raise ValidationError({
                "detail": "This appointment cannot be rescheduled."
            })

        if appointment.appointment_date < timezone.localdate():
            raise ValidationError({
                "detail": "Past appointments cannot be rescheduled."
            })

        cls.validate_booking_date(new_date)

        new_slot = (
            AppointmentSlot.objects
            .select_for_update()
            .select_related("schedule")
            .get(pk=new_slot.pk)
        )

        cls.validate_slot(slot=new_slot, doctor=appointment.doctor, appointment_date=new_date)

        appointment.appointment_date = new_date
        appointment.slot = new_slot
        appointment.save(updated_fields=["appointment_date", "slot"])

        return appointment

    @staticmethod
    def cancel_appointment(*, appointment_number, reason):
        from appointments.models import Appointment
        
        with transaction.atomic():
            appointment = (
                Appointment.objects.select_for_update()
                .get(appointment_number=appointment_number)
            )

            if appointment.Status == Appointment.Status.CANCELLED:
                raise serializers.ValidationError({
                    "detail": "Appointment is already cancelled."
                })
    
            if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.NO_SHOW]:
                raise serializers.ValidationError({"detail": "Completed appointments cannot be cancelled."})
    
            # Business rule: no cancelling in the past
            if appointment.appointment_date < timezone.localdate():
                raise serializers.ValidationError({"detail": "Past appointments cannot be cancelled."})

            appointment.status = Appointment.Status.CANCELLED
            appointment.cancellation_reason = reason
            appointment.cancelled_at = timezone.now()

            appointment.save(update_fields=["cancellation_reason", "cancelled_at", "status"])

        return appointment
