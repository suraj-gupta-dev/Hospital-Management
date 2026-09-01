import uuid
from django.db import models

from django.conf import settings



class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HospitalAdminProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hospital_admin_profile")
    employee_id = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"



class Hospital(BaseModel):
    admin = models.OneToOneField(HospitalAdminProfile, on_delete=models.PROTECT, related_name="administered_hospital", null=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=30, unique=True)
    registration_number = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="hospitals/logos/", null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Branch(BaseModel):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="India")
    postal_code = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["hospital", "code"],
                name="unique_branch_code_per_hospital"
            )
        ]

    def __str__(self):
        return f"{self.hospital.name} - {self.name}"


class Department(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    floor = models.CharField(max_length=30,blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.branch.name}"


# class Rooms(models.Model):
#     pass


# class Beds(models.Model):
#     pass


# class Holidays(models.Model):
#     pass