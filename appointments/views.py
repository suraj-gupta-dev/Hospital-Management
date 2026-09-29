from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from .serializers import DoctorScheduleSerializer, AppointmentSerializer, AppointmentSlotSerializer
from .models import DoctorSchedule, Appointment, AppointmentSlot
from .services.appointment import AppointmentBookingService
from .permissions import IsDoctorRecepOrAdmin




class DoctorScheduleGenericViewSet(ModelViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleSerializer


class AppointmentSlotModelViewSet(ModelViewSet):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotSerializer


class AppointmentModelViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsDoctorRecepOrAdmin]
    lookup_field = "appointment_number"

    def get_queryset(self):
        qs = Appointment.objects.select_related(
            "doctor",
            "patient",
            "department",
            "appointment_slot"
        )
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            AppointmentBookingService.create_appointment(
                validated_data=serializer.validate_data
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)
