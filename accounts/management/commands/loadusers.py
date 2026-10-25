import json
from pathlib import Path
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction



User = get_user_model()



class Command(BaseCommand):
    help = "Seed users from users.json"

    def handle(self, *args, **options):
        users = Path(__file__).resolve().parent / "users.json"

        with open(users) as file:
            users_data = json.load(file)

        roles = {
            "Hospital Admin": User.RoleChoices.HOSPITAL_ADMIN,
            "Doctor": User.RoleChoices.DOCTOR,
            "Nurse": User.RoleChoices.NURSE,
            "Receptionist": User.RoleChoices.RECEPTIONIST,
            "Lab Technician": User.RoleChoices.LAB_TECHNICIAN,
            "Pharmacist": User.RoleChoices.PHARMACIST,
            "Cashier": User.RoleChoices.CASHIER,
            "Patient": User.RoleChoices.PATIENT
        }

        User.objects.all().delete()
        with transaction.atomic():
            for data in users_data:
                data["role"] = roles[data["role"]]
                if data["is_superuser"] == "true":
                    User.objects.create_superuser(**data)
                else:
                    User.objects.create_user(**data)
        self.stdout.write(self.style.SUCCESS("Successfully users added!"))