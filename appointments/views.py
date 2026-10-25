import logging
from datetime import date

from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    DoctorScheduleSerializer, AppointmentSerializer,
    AppointmentSlotSerializer, CancelAppointmentSerializer
)
from accounts.models import DoctorProfile
from .models import DoctorSchedule, Appointment, AppointmentSlot
from .services.appointment import AppointmentServices
from .permissions import IsDoctorReceptOrAdmin
from .filters import AppointmentFilter

logger = logging.getLogger(__name__)




class DoctorScheduleGenericViewSet(ModelViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleSerializer


class AppointmentSlotModelViewSet(ModelViewSet):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotSerializer


class AppointmentModelViewSet(ModelViewSet):
    queryset = Appointment.objects.select_related(
            "doctor", "patient", "department", "slot"
        )
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsDoctorReceptOrAdmin]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    lookup_field = "appointment_number"
    # filterset_fields = ["status", "appointment_date"]
    filterset_class = AppointmentFilter
    search_fields = [
        "patient__user__first_name",
        "status",
        "doctor__user__first_name",
        "department__name"
    ]
    ordering_fields = ["appointment_date", "status", "appointment_type"]

    def get_queryset(self):
        qs = super().get_queryset()

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
            logger.info("appointment created successfully.")

        except IntegrityError:
            logger.info("appointment creation failed.")

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
        detail=False,
        methods=["get"],
        url_path="appointment-slots"
    )
    def appointment_slot(self, request):
        """
        GET /appointments/available-slots/
            ?doctor_id=5&date=2026-10-12
        """

        doctor_id = request.query_params.get("doctor_id")
        appointment_date = request.query_params.get("date")

        if not doctor_id or not appointment_date:
            return Response({
                "error": "both doctor_id and date are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            selected_date = date.fromisoformat(appointment_date)
        except (ValueError, TypeError):
            return Response({
                "error": "Invalid date format. Use YYY-MM-DD"
            }, status=status.HTTP_400_BAD_REQUEST)

        doctor = get_object_or_404(DoctorProfile, id=doctor_id)

        # Find the doctor's active schedule for this weekday.
        weekday = selected_date.weekday()
        print(weekday)

        schedules = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=weekday,
            is_active=True
        )

        if not schedules.exists():
            return Response({
                "doctor_id": doctor.pk,
                    "date": selected_date.isoformat(),
                    "available_slots": [],
                    "message": (
                        "This doctor has no active schedule "
                        "on the selected day."
                    ),
            }, status=status.HTTP_200_OK)

        # Find available slots for this doctor on this date.
        booked_slot_ids = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=selected_date
        ).exclude(
            status=Appointment.Status.CANCELLED
        ).values_list("slot__id", flat=True)

        available_slot_ids = AppointmentSlot.objects.filter(
            ~Q(id__in=booked_slot_ids)
        ).values_list('id', flat=True)

        return Response({
            "doctor": f"{doctor.user.first_name} {doctor.user.last_name}",
            "date": selected_date,
            "available_slots": available_slot_ids
        })


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

