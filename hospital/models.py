import uuid
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()



class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    floor = models.CharField(max_length=30,blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.branch.name}"


class StaffDeparment(models.Model):
    staff = models.ForeignKey(User, on_delete=models.PROTECT, related_name="department_assignments")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="staff_assignments")
    is_primary = models.BooleanField(default=False)
    joined_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["staff", "department"],
                name="unique_staff_department",
            ),
        ]

    def __str__(self):
        return f"{self.staff} - {self.department}"