from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register("doctor-schedule", views.DoctorScheduleGenericViewSet)
router.register("appointments", views.AppointmentModelViewSet)
router.register("appointment-slot", views.AppointmentSlotModelViewSet)


urlpatterns = [
    path("", include(router.urls))
]
