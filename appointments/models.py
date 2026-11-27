from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError

from hospital.models import Department
from accounts.models import DoctorProfile, PatientProfile
from .services.appointment import AppointmentServices






class DoctorSchedule(models.Model):
    class WeekDay(models.IntegerChoices):
        MONDAY    = 0, "Monday"
        TUESDAY   = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY  = 3, "Thursday"
        FRIDAY    = 4, "Friday"
        SATURDAY  = 5, "Saturday"
        SUNDAY    = 6, "Sunday"

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.PositiveSmallIntegerField(choices=WeekDay.choices)
    slot_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.slot_duration <= 0:
            raise ValidationError({
                "slot_duration": "Duration must be greater than zero."
            })

        if self.start_time >= self.end_time:
            raise ValidationError({
                "end_time": "End time must be after start time."
            })

    def __str__(self):
        return f"{self.day_of_week}-{self.start_time}:{self.end_time}"


class AppointmentSlot(models.Model):
    schedule = models.ForeignKey(DoctorSchedule, on_delete=models.CASCADE, related_name="slots")
    appointment_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["appointment_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "appointment_time"],
                name="unique_schedule_appointment_time",
            )
        ] 

    def __str__(self):
        return f"{self.schedule.doctor} - {self.appointment_time}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED   = "SCHEDULED", "Scheduled"
        CONFIRMED   = "CONFIRMED", "Confirmed"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED   = "COMPLETED", "Completed"
        CANCELLED   = "CANCELLED", "Cancelled"
        NO_SHOW     = "NO_SHOW", "No Show"

    class AppointmentType(models.TextChoices):
        CONSULTATION = "CONSULTATION", "Consultation"
        FOLLOW_UP    = "FOLLOW_UP", "Follow Up"
        EMERGENCY    = "EMERGENCY", "Emergency"

    appointment_number = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.PROTECT, related_name="appointments")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="appointments")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="appointments")
    slot = models.ForeignKey(AppointmentSlot, on_delete=models.PROTECT, related_name="appointments", null=True)
    appointment_date = models.DateField()
    appointment_type = models.CharField(max_length=30, choices=AppointmentType.choices)
    status = models.CharField(max_length=30, choices=Status.choices)
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            # Doctor cannot be double-booked in the same slot
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'slot'],
                condition=~Q(status="CANCELLED"),
                name="unique_active_appointment"
            ),

            # Patient cannot have more than one active appointment
            # with the same doctor on the same day
            models.UniqueConstraint(
                fields=["patient", "doctor", "appointment_date"],
                condition=~Q(status__in=["CANCELLED", "COMPLETED"]),
                name="unique_active_patient_doctor_per_day"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.appointment_number:
            self.appointment_number = AppointmentServices.generate(
                self.department.code
            )
        super().save(*args, **kwargs)


class BookingSettings(models.Model):
    is_closed = models.BooleanField(default=False)
    closed_from = models.DateTimeField(null=True, blank=True)
    closed_until = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def is_closed_now(cls):
        obj = cls.objects.first()
        if not obj or not obj.is_closed:
            return False

        now = timezone.now()
        if obj.closed_from and now < obj.closed_from:
            return False
        if obj.closed_until and now > obj.closed_until:
            return False
        return True