from datetime import timedelta, datetime
from django.db import transaction

from appointments.models import DoctorSchedule, AppointmentSlot



class AppointmentSlotGenerator:
    @staticmethod
    def generate_for_schedule(*, schedule: DoctorSchedule):
        """
        Generate reusable time slots for one DoctorSchedule.

        Example:
            09:00 - 11:00
            Duration: 30 minutes

            Generated:
                09:00
                09:30
                10:00
                10:30
        """
        if not schedule.is_active:
            return 0

        if schedule.slot_duration <= 0:
            raise ValueError(
                "Slot duration must be greater than zero."
            )

        if schedule.start_time >= schedule.end_time:
            raise ValueError(
                "Schedule start time must be before end time."
            )

        duration = timedelta(minutes=schedule.slot_duration)

        # A fixed reference date is used only to perform
        # time arithmetic. Slots themselves are reusable.
        reference_date = datetime.today().date()

        current_time = datetime.combine(
            reference_date,
            schedule.start_time
        )
        schedule_end = datetime.combine(
            reference_date,
            schedule.end_time
        )

        generate_times = []
        while current_time <= schedule_end:
            generate_times.append(current_time.time())
            current_time += duration

        with transaction.atomic():
            # Lock schedule to reduce concurrent generation
            # for the same schedule.
            locked_schedule = (
                DoctorSchedule.objects
                .select_for_update()
                .get(pk=schedule.pk)
            )
            if not locked_schedule.is_active:
                return 0

            created_counter = 0

            for appointment_time in generate_times:
                slot, created = AppointmentSlot.objects.get_or_create(
                    schedule=locked_schedule,
                    appointment_time=appointment_time,
                    defaults={"is_active": True}
                )

                if created:
                    created_counter += 1
                elif not slot.is_active:
                    # Reactivate a slot if it is still part
                    # of the current schedule.
                    slot.is_active = True
                    slot.save(update_fields=["is_active"])

            # Deactivate old slots that no longer belong
            # to the schedule. Do not delete them because
            # existing appointments may reference them.
            AppointmentSlot.objects.filter(
                schedule=locked_schedule,
                is_active=True
            ).exclude(
                appointment_time__in=generate_times
            ).update(is_active=False)

        return created_counter