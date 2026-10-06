from django.contrib import admin

from .models import DoctorSchedule, Appointment, AppointmentSlot


class AppointmentAdmin(admin.ModelAdmin):
    readonly_fields = ["appointment_number"]



admin.site.register(DoctorSchedule)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(AppointmentSlot)