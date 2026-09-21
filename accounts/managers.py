from django.contrib.auth.models import BaseUserManager
from django.apps import apps
from django.db import transaction



class UserManager(BaseUserManager):
    PROFILE_MAP = {
        "DOC": "DoctorProfile",
        "PAT": "PatientProfile",
        "REC": "ReceptionistProfile",
        "NUR": "NurseProfile",
    }

    def create_user(self, email, first_name, last_name, password, **extra_kwargs):
        if not email:
            raise ValueError("Email field is required")
        if not password:
            raise ValueError("Password is required")
        
        email = self.normalize_email(email)

        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_kwargs)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_kwargs):
            extra_kwargs.update({
                "is_staff": True,
                "is_verified": True,
                "is_superuser": True,
                "is_active": True
            })
    
            if extra_kwargs.get("is_staff") is not True:
                raise ValueError("Superuser must have is_staff=True.")
            if extra_kwargs.get("is_superuser") is not True:
                raise ValueError("Superuser must have is_superuser=True.")
            
            user = self.create_user(email, first_name, last_name, password, **extra_kwargs)
            return user

    @transaction.atomic
    def create_user_with_profile(self, email, first_name, last_name, password, profile, **extra_kwargs):
        user = self.create_user(email, first_name, last_name, password, **extra_kwargs)

        model = self.PROFILE_MAP.get(user.role, None)
        if not model:
            raise ValueError("user must have a role.")
        Model = apps.get_model(app_label="accounts", model_name=model)
        Model.objects.create(user=user, **profile)
        return user
