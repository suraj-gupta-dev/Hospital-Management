import uuid
from django.db import models



class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Hospital(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=30, unique=True)
    registration_number = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20,null=True, blank=True)
    logo = models.ImageField(upload_to="hospitals/logos/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    address_line_1 = models.CharField(max_length=255, null=True)
    address_line_2 = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, default="India", null=True)
    postal_code = models.CharField(max_length=20, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Department(BaseModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    floor = models.CharField(max_length=30,blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.branch.name}"

