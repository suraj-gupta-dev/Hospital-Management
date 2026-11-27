from django.core.management.base import BaseCommand, CommandError

from appointments.models import DoctorSchedule
from appointments.services.slot_generator import AppointmentSlotGenerator


class Command(BaseCommand):
    help = "Generate appointment slots from doctor schedules."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schedule-id",
            type=int,
            help="Generate slots for a specific schedule.",
        )

        parser.add_argument(
            "--doctor-id",
            type=str,
            help="Generate slots for a specific doctor.",
        )

    def handle(self, *args, **options):
        schedule_id = options.get("schedule_id")
        doctor_id = options.get("doctor_id")

        schedules = DoctorSchedule.objects.filter(is_active=True)
        print(schedules.values())

        if schedule_id:
            schedules = schedules.filter(
                pk=schedule_id
            )

        if doctor_id:
            schedules = schedules.filter(
                doctor_id=doctor_id
            )

        total_create = 0
        for schedule in schedules.iterator():
            try:
                created = (
                    AppointmentSlotGenerator
                    .generate_for_schedule(schedule=schedule)
                )
                total_create += created
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Schedule {schedule.pk}: {created} new slots generated."
                    )
                )
            except (ValueError, DoctorSchedule.DoesNotExist)as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Schedule {schedule.pk}: {exc}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Total new slots generate: {total_create}"
            )
        )