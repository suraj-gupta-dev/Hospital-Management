import logging

from django.utils import timezone
from django.db import transaction, IntegrityError

from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action

from .serializers import (
    DoctorScheduleSerializer, AppointmentSerializer,
    AppointmentSlotSerializer, CancelAppointmentSerializer
)
from .models import DoctorSchedule, Appointment, AppointmentSlot
from .services.appointment import AppointmentServices
from .permissions import IsDoctorRecepOrAdmin

logg = logging.getLogger(__name__)




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
        qs = super().get_queryset().select_related(
            "doctor", "patient", "department", "slot"
        )

        user = self.request.user
        role = getattr(user, "role", None)

        if role == "PAT":
            patient_profile = getattr(user, "patient_profile", None)
            return qs.filter(patient=patient_profile)
        if role == "DOC":
            doctor_profile = getattr(user, "doctor_profile", None)
            return qs.filter(doctor=doctor_profile)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            validated_data = serializer.validated_data
            patient = self.get_serializer_context().get("patient", None)
            if patient:
                validated_data["patient"] = patient

            AppointmentServices.create_appointment(
                validated_data=serializer.validated_data,
            )
            logg.info("appointment created successfully.")

        except IntegrityError:
            logg.info("appointment creation failed.")

            raise serializers.ValidationError({
                "error": "time slot is already booked.",
                "status": status.HTTP_400_BAD_REQUEST
            })
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        role = getattr(user, "role", None)
        if role == "PAT":
            patient_profile = getattr(user, "patient_profile", None)
            context["patient"] = patient_profile
            return context
        return context

    @action(
        detail=True,
        methods=["post"],
        url_path="cancel",
        serializer_class=CancelAppointmentSerializer
    )
    def cancel(self, request, appointment_number=None):
        appointment = self.get_object()
        serializer = CancelAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cancellation_reason = serializer.validated_data.get(
            "cancellation_reason", ""
        )

        appointment = AppointmentServices.cancel_appointment(
            appoint_id=appointment.appointment_number,
            reason=cancellation_reason
        )

        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

