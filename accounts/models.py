import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .managers import UserManager




class BaseModel(models.Model):
    GENDER_CHOICES = [
            ("M", "Male"),
            ("F", "Female"),
            ("O", "Other")
        ]

    date_of_birth = models.DateField(null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1)
    profile_picture = models.ImageField(upload_to="uploads/images", null=True)

    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    postal_code = models.IntegerField(validators=[MinValueValidator(6), MaxValueValidator(6)])

    emergency_contact_name = models.CharField(max_length=10)
    emergency_contact_phone = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class UserRoleChoices(models.TextChoices):
    HOSPITAL_ADMIN = "Hospita Admin"
    DOCTOR = "Doctor"
    NURSE = "Nurse"
    RECEPTIONIST = "Receptionist"
    LAB_TECHNICIAN = "Lab Technician"
    PHARMACIST = "Pharmacist"
    CASHIER = "Cashier"
    PATIENT = "Patient"



class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=12)
    username = models.CharField(max_length=50, unique=True, null=True)
    role = models.CharField(choices=UserRoleChoices.choices, null=True)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_varified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email


class DoctorProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    registration_number = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)


class NurseProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="nurse_profile")
    registration_number = models.CharField(max_length=100, unique=True)
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    nursing_type = models.CharField(max_length=100, blank=True)

    
class PatientProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    patient_number = models.CharField(max_length=50, unique=True)
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)


class ReceptionistProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="receptionist_profile")
    employee_id = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=255, blank=True)
    joining_date = models.DateField(null=True, blank=True)


class PharmacistProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pharmacist_profile")
    license_number = models.CharField(max_length=100, unique=True)
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    joining_date = models.DateField(null=True, blank=True)


class LabTechnicianProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lab_technician_profile")
    employee_id = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=255)
    specialization = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    joining_date = models.DateField(null=True, blank=True)


class CashierProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cashier_profile")
    employee_id = models.CharField(max_length=50, unique=True)
    joining_date = models.DateField(null=True, blank=True)

