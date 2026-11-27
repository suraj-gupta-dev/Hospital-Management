import logging
from datetime import date, timedelta

from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    DoctorScheduleSerializer, AppointmentSerializer,
    AppointmentSlotSerializer, CancelAppointmentSerializer,
    PatientAppointmentCreateSerializer, ReceptionistAppointmentCreateSerializer,
    RescheduleAppointmentSerializer
)
from accounts.models import DoctorProfile
from .models import DoctorSchedule, Appointment, AppointmentSlot
from .services.appointment import AppointmentServices
from .permissions import IsPatientOrReceptionist, CanManageAppointment
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
            "doctor__user", "patient__user", "department", "slot__schedule"
        )
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
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
        queryset = super().get_queryset()

        user = self.request.user
        role = getattr(user, "role", None)

        if role == "PAT":
            patient_profile = getattr(user, "patient_profile", None)
            return queryset.filter(patient=patient_profile)
        
        if role == "DOC":
            doctor_profile = getattr(user, "doctor_profile", None)
            return queryset.filter(doctor=doctor_profile)

        if role == "REC":
            return queryset
        
        return queryset.none()

    def get_serializer_class(self):
        if self.action == "create":
            if self.request.user.role == "PAT":
                return PatientAppointmentCreateSerializer

            if self.request.user.role == "REC":
                return ReceptionistAppointmentCreateSerializer

        if self.action == "reschedule":
            return RescheduleAppointmentSerializer

        if self.action == "cancel":
            return CancelAppointmentSerializer

        return AppointmentSerializer

    def get_permissions(self):
        if self.action in ["create", "reschedule", "cancel"]:
            return [
                IsAuthenticated(),
                IsPatientOrReceptionist()
            ]

        if self.action in ["reschedule", "cancel"]:
            return [
                IsAuthenticated(),
                IsPatientOrReceptionist(),
                CanManageAppointment()
            ]
        
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        role = getattr(request.user, "role", None)

        if role not in ["PAT", "REC"]:
            return Response(
                {"detail": "You cannot book appointments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data.copy()

        if role == "PAT":
            patient = getattr(request.user, "patient_profile", None)

        if patient is None:
            raise ValidationError({
                    "patient": "Patient profile not found."
            })

        validated_data["patient"] = patient

        try:
            appointment = AppointmentServices.create_appointment(
                validated_data=validated_data,
            )
            logger.info("appointment created successfully.")

        except IntegrityError:
            logger.warning(
                "Appointment booking conflict for user %s",
                request.user.pk,
            )

            raise ValidationError({
                "detail": (
                    "This appointment slot has already been booked "
                    "or conflicts with an existing appointment."
                ),
                "status": status.HTTP_400_BAD_REQUEST
            })
        response_serializer = AppointmentSerializer(
            appointment,
            context=self.get_serializer_context(),
        )

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["get"],
        url_path="available-slots"
    )
    def available_slots(self, request):
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

        today = timezone.localdate()
        last_booking_date = today + timedelta(days=7)

        if selected_date < today:
            raise ValidationError({
                "date": "Past dates are not available."
            })

        if selected_date > last_booking_date:
            raise ValidationError({
                "date": "Date is outside the booking window."
            })

        doctor = get_object_or_404(DoctorProfile, doctor_id=doctor_id, is_available=True)

        schedules = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=selected_date.weekday(),
            is_active=True
        )

        if not schedules.exists():
            return Response({
                "doctor_id": doctor.doctor_id,
                    "date": selected_date.isoformat(),
                    "available_slots": [],
                    "message": (
                        "This doctor has no active schedule "
                        "on the selected day."
                    ),
            }, status=status.HTTP_200_OK)

        # Find slots already booked for this doctor and date.
        booked_slot_ids = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=selected_date
        ).exclude(
            status=Appointment.Status.CANCELLED
        ).values_list("slot__id", flat=True)

        # Only return slots belonging to the selected doctor's
        # active schedules for this weekday.
        available_slots = AppointmentSlot.objects.filter(
            schedule__in=schedules,
            is_active=True
        ).exclude(
            pk__in=booked_slot_ids,
        ).select_related(
            "schedule",
        ).order_by("appointment_time")

        """
        schedule_id is not an explicitly declared field in your Django model.
        It is an automatically generated attribute by Django ORM for a ForeignKey field.
        
        slot.schedule	The related DoctorSchedule object
        slot.schedule_id	The primary key of that DoctorSchedule object
        """
        slot_data = [
            {
                "id": slot.id,
                "schedule_id": slot.schedule_id,
                "appointment_time": slot.appointment_time.strftime("%H:%M")
            }
            for slot in available_slots
        ]

        return Response({
            "doctor": doctor.user.full_name,
            "date": selected_date.isoformat(),
            "available_slots": slot_data
        }, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="reschedule",
    )
    def reschedule(self, request, appointment_number):
        appointment = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_appointment = (
                AppointmentServices.reschedule_appointment(
                    appointment_number=appointment.appointment_number,
                    new_date=serializer.validated_data["appointment_date"],
                    new_slot=serializer.validated_data["slot"],
                    requesting_user=request.user
                )
            )
        except ValidationError as exc:
            raise ValidationError({
                "detail": str(exc)
            })
        
        response_serializer = AppointmentSerializer(
            updated_appointment,
            context=self.get_serializer_context()
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


    @action(
        detail=True,
        methods=["post"],
        url_path="cancel",
    )
    def cancel(self, request, appointment_number):
        appointment = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cancellation_reason = serializer.validated_data.get(
            "cancellation_reason", ""
        )

        try:
            cancelled_appointment = AppointmentServices.cancel_appointment(
                appointment_number=appointment.appointment_number,
                reason=cancellation_reason
            )
        except ValidationError as exc:
            raise ValidationError({
                "detail": str(exc)
            })

        return Response(
            AppointmentSerializer(
                cancelled_appointment,
                context=self.get_serializer_context()
            ).data,
            status=status.HTTP_200_OK
        )

