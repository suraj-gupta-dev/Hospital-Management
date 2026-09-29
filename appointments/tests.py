from django.test import TestCase
from django.urls import reverse
from datetime import date, time

from rest_framework.test import APIClient
from rest_framework import status
from appointments.models import Appointment, AppointmentSlot
from hospital.models import Department, StaffDeparment
from accounts.models import User, PatientProfile, DoctorProfile




class AppointmentBookingTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("appointment-list")

        p_user = User.objects.create_user(
            email="ptest@gmail.com",
            password="test@123",
            first_name="subject",
            last_name="one",
            role="PAT"
        )
        d_user = User.objects.create_user(
            email="dtest@gmail.com",
            password="test@123",
            first_name="subject",
            last_name="one",
            role="DOC"

        )

        self.patient = PatientProfile.objects.create(user=p_user)
        self.doctor = DoctorProfile.objects.create(user=d_user, specialization="General")
        self.department = Department.objects.create(name="Gastrology", code="GAST")
        self.staffdepartment = StaffDeparment.objects.create(
            staff=self.doctor.user,
            department=self.department
        )

        self.appointment_slot = AppointmentSlot.objects.create(
            doctor=self.doctor, date=date.today(), appointment_time=time(minute=4)
        )

        # Create an existing appointment for today
        self.appointment_date = date.today()

        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.department,
            appointment_date=self.appointment_date
        )

        self.client.force_authenticate(user=p_user)


    def test_duplicate_appointment_same_doctor_same_day(self):
        response = self.client.post(self.url, {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "department": self.department.id,
            "appointment_type": "CONSULTATION",
            "appointment_slot": self.appointment_slot.id,
            "appointment_date": self.appointment_date.isoformat()
        }, format="json")

        # should fall with 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already", str(response.data).lower())



