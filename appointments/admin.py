from django.contrib import admin

from .models import DoctorSchedule, Appointment



admin.site.register(DoctorSchedule)
admin.site.register(Appointment)