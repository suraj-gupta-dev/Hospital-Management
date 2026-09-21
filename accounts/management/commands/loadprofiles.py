import json
from pathlib import Path
from django.core.management import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from accounts.models import (
    DoctorProfile, PatientProfile,
    NurseProfile, ReceptionistProfile,
    PharmacistProfile, LabTechnicianProfile,
    CashierProfile, HospitalAdminProfile
)

User = get_user_model()


ROLE_TO_PROFILE = {
    "HA":  HospitalAdminProfile,
    "DOC": DoctorProfile,
    "NUR": NurseProfile,
    "PAT": PatientProfile,
    "REC": ReceptionistProfile,
    "PHA": PharmacistProfile,
    "LT":  LabTechnicianProfile,
    "CAS": CashierProfile,
}


class Command(BaseCommand):
    help = "creating profile for matching users"

    def handle(self, *args, **options):
        profile_file = Path(__file__).resolve().parent / "profiles.json"
        with open(profile_file) as file:
            profiles = json.load(file)

        with transaction.atomic():
            for profile in profiles:
                username = profile.pop("user__username")
                user = get_object_or_404(User, username=username)
                if user:
                    Profile = ROLE_TO_PROFILE[user.role]
                    Profile.objects.create(user=user, **profile)
                    self.stdout.write(f"✔ {username} → {Profile.__name__}")

                
