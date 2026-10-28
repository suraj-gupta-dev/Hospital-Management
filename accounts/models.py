import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .managers import UserManager







class User(AbstractBaseUser, PermissionsMixin):
    class RoleChoices(models.TextChoices):
        HOSPITAL_ADMIN = "HA", "Hospital Admin"
        DOCTOR         = "DOC", "Doctor"
        NURSE          = "NUR", "Nurse"
        RECEPTIONIST   = "REC", "Receptionist"
        LAB_TECHNICIAN = "LT", "Lab Technician"
        PHARMACIST     = "PHA", "Pharmacist"
        CASHIER        = "CAS",  "Cashier"
        PATIENT        = "PAT", "Patient"
    user_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=12)
    username = models.CharField(max_length=50, unique=True, null=True)
    role = models.CharField(choices=RoleChoices.choices, null=True)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email



"""------ID GENERATION (shared by every profile)-----"""

class PrefixIDMixin(models.Model):
    """
    Gives a profile a readable primary key like "DOC-3F9A12BC".
 
    Usage:
        class DoctorProfile(PrefixedIDMixin, ProfileBaseModel):
            ID_PREFIX = "DOC"
            doctor_id = models.CharField(max_length=50, primary_key=True, editable=False)
 
    The primary key field is found through _meta.pk, so you never name it here, and
    each model checks uniqueness against ITS OWN table (cls.objects).
    editable=False makes DRF treat the field as read-only, so clients never send it.
    """

    ID_PREFIX = None

    class Meta:
        abstract = True

    @classmethod
    def _generate_id(cls):
        while True:
            value = f"{cls.ID_PREFIX}-{uuid.uuid4().hex[:8].upper()}"
            if not cls.objects.filter(pk=value).exists():
                return value

    def save(self, *args, **kwargs):
        if self._state.adding and not self.pk:
            # self._meta.pk.attname, it gives the pk field name like, doctor_id, nurse_id
            setattr(self, self._meta.pk.attname, self._generate_id())
        super().save(*args, **kwargs)
    

"""------PROFILE MODELS FOR DIFFERENT ROLE-----"""

class ProfileBaseModel(models.Model):
    GENDER_CHOICES = [
            ("M", "Male"),
            ("F", "Female"),
            ("O", "Other")
        ]

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1)
    profile_picture = models.ImageField(upload_to="images", null=True, blank=True)

    address_line_1 = models.CharField(max_length=100, null=True, blank=True)
    address_line_2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.IntegerField(
        validators=[MinValueValidator(100000),
        MaxValueValidator(999999)],
        null=True, blank=True
    )
    emergency_contact_phone = models.CharField(max_length=12, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DoctorProfile(PrefixIDMixin, ProfileBaseModel):
    ID_PREFIX = "DOC"

    class Designation(models.TextChoices):
        HOD = "HOD", "Head of Department"
        SENIOR_CONSULTANT = "SENIOR_CONSULTANT", "Senior Consultant"
        CONSULTANT = "CONSULTANT", "Consultant"
        ASSOCIATE_CONSULTANT = "ASSOCIATE_CONSULTANT", "Associate Consultant"
        SENIOR_RESIDENT = "SENIOR_RESIDENT", "Senior Resident"
        JUNIOR_RESIDENT = "JUNIOR_RESIDENT", "Junior Resident"
        MEDICAL_OFFICER = "MEDICAL_OFFICER", "Medical Officer"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        VISITING = "VISITING", "Visiting"
        CONTRACT = "CONTRACT", "Contract"

    doctor_id = models.CharField(max_length=50, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    registration_number = models.CharField(max_length=100, unique=True)
    designation = models.CharField(max_length=50, choices=Designation.choices, blank=True)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, blank=True)
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.email


class NurseProfile(PrefixIDMixin, ProfileBaseModel):
    ID_PREFIX = "NUR"

    class Designation(models.TextChoices):
        HEAD_NURSE = "HEAD_NURSE", "Head Nurse"
        SENIOR_NURSE = "SENIOR_NURSE", "Senior Nurse"
        STAFF_NURSE = "STAFF_NURSE", "Staff Nurse"
        JUNIOR_NURSE = "JUNIOR_NURSE", "Junior Nurse"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"

    nurse_id = models.CharField(max_length=52, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="nurse_profile")
    registration_number = models.CharField(max_length=100, unique=True)
    designation = models.CharField(max_length=50, choices=Designation.choices, blank=True)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, blank=True)
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.email

    
class PatientProfile(PrefixIDMixin, ProfileBaseModel):
    ID_PREFIX = "PAT"

    class BloodGroup(models.TextChoices):
        A_POSITIVE = "A+", "A+"
        A_NEGATIVE = "A-", "A-"
        B_POSITIVE = "B+", "B+"
        B_NEGATIVE = "B-", "B-"
        AB_POSITIVE = "AB+", "AB+"
        AB_NEGATIVE = "AB-", "AB-"
        O_POSITIVE = "O+", "O+"
        O_NEGATIVE = "O-", "O-"

    patient_id = models.CharField(max_length=50, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    blood_group = models.CharField(max_length=3, choices=BloodGroup.choices, blank=True)
    occupation = models.CharField(max_length=150, blank=True)      

    def __str__(self):
            return self.user.email
    

class ReceptionistProfile(PrefixIDMixin, ProfileBaseModel):
    ID_PREFIX = "REC"

    class Designation(models.TextChoices):
        RECEPTION_MANAGER = "RECEPTION_MANAGER", "Reception Manager"
        SENIOR_RECEPTIONIST = "SENIOR_RECEPTIONIST", "Senior Receptionist"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        FRONT_DESK_EXECUTIVE = "FRONT_DESK_EXECUTIVE", "Front Desk Executive"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"

    recept_id = models.CharField(max_length=50, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="receptionist_profile")
    designation = models.CharField(max_length=50, choices=Designation.choices, blank=True)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, blank=True)
    qualification = models.CharField(max_length=255, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
            return self.user.email


class PharmacistProfile(PrefixIDMixin, ProfileBaseModel):
    ID_PREFIX = "PHA"

    class Designation(models.TextChoices):
        PHARMACY_MANAGER = "PHARMACY_MANAGER", "Pharmacy Manager"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        JUNIOR_PHARMACIST = "JUNIOR_PHARMACIST", "Junior Pharmacist"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"

    pharm_id = models.CharField(max_length=50, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pharmacist_profile")
    license_number = models.CharField(max_length=100, unique=True)
    qualification = models.CharField(max_length=255)
    designation = models.CharField(max_length=50, choices=Designation.choices, blank=True)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
            return self.user.email


class LabTechnicianProfile(PrefixIDMixin, ProfileBaseModel):
    ID_PREFIX = "LT"

    class Designation(models.TextChoices):
        LAB_MANAGER = "LAB_MANAGER", "Lab Manager"
        SENIOR_TECHNICIAN = "SENIOR_TECHNICIAN", "Senior Lab Technician"
        LAB_TECHNICIAN = "LAB_TECHNICIAN", "Lab Technician"
        JUNIOR_TECHNICIAN = "JUNIOR_TECHNICIAN", "Junior Lab Technician"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"

    lab_tech_id = models.CharField(max_length=50, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lab_technician_profile")
    designation = models.CharField(max_length=50, choices=Designation.choices, blank=True)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, blank=True)
    qualification = models.CharField(max_length=255)
    specialization = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
            return self.user.email


class CashierProfile(PrefixIDMixin, ProfileBaseModel):
    ID_PREFIX = "CAS"

    class Designation(models.TextChoices):
        FINANCE_MANAGER = "FINANCE_MANAGER", "Finance Manager"
        SENIOR_CASHIER = "SENIOR_CASHIER", "Senior Cashier"
        CASHIER = "CASHIER", "Cashier"
        BILLING_EXECUTIVE = "BILLING_EXECUTIVE", "Billing Executive"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"

    cash_id = models.CharField(max_length=50, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cashier_profile")
    designation = models.CharField(max_length=50, choices=Designation.choices, blank=True)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
            return self.user.email


class HospitalAdminProfile(PrefixIDMixin, ProfileBaseModel):
    ID_PREFIX = "HA"

    class Designation(models.TextChoices):
        HOSPITAL_ADMINISTRATOR = (
            "HOSPITAL_ADMINISTRATOR",
            "Hospital Administrator",
        )
        OPERATIONS_MANAGER = (
            "OPERATIONS_MANAGER",
            "Operations Manager",
        )
        ADMINISTRATIVE_MANAGER = (
            "ADMINISTRATIVE_MANAGER",
            "Administrative Manager",
        )
        MEDICAL_SUPERINTENDENT = (
            "MEDICAL_SUPERINTENDENT",
            "Medical Superintendent",
        )

    admin_id = models.CharField(max_length=50, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="hospital_admin_profile")
    designation = models.CharField(max_length=50, choices=Designation.choices, null=True)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
            return self.user.email


class PatientUser(User):
    class Meta:
        proxy = True

    class Manager(UserManager):
        def get_queryset(self):
            return super().get_queryset().filter(role=User.RoleChoices.PATIENT)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.role = User.RoleChoices.PATIENT
        super().save(*args, **kwargs)

    objects = Manager()
