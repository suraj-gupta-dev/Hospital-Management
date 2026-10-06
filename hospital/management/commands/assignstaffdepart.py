from django.core.management import BaseCommand
from django.contrib.auth import get_user_model

from hospital.models import Department, StaffDeparment
from accounts.models import UserRoleChoices

User = get_user_model()



class Command(BaseCommand):
    help = """Assigning Staff to a department."""

    def handle(self, *args, **options):
        users = User.objects.select_related("doctor_profile").filter(role=UserRoleChoices.DOCTOR)
        for user in users:
            department = Department.objects.filter(name=user.doctor_profile.specialization)
            if department.exists():
                StaffDeparment.objects.create(
                    staff=user,
                    department=department[0],
                    is_primary=True
                )
        self.stdout.write(self.style.SUCCESS("Doctors Assign to Departments"))