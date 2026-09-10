from django.core.management.base import BaseCommand
from django.core.management import call_command

from hospital.models import Hospital, Branch


class Command(BaseCommand):
    help = "Create 3 Hospital Branches"

    def handle(self, *args, **options):
        hospital = Hospital.objects.first()

        if Branch.objects.all().exists():
            Branch.objects.all().delete()

        branches = [
            {
                "hospital": hospital,  # Replace with actual Hospital instance
                "name": "Downtown Medical Center",
                "code": "DMC-001",
                "email": "downtown@cityhospital.com",
                "phone_number": "+91-9876543210",
                "address_line_1": "123, MG Road",
                "address_line_2": "Near City Mall",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400001",
                "is_active": True
            },
            {
                "hospital": hospital,  # Replace with actual Hospital instance
                "name": "Northside Health Hub",
                "code": "NHH-002",
                "email": "northside@cityhospital.com",
                "phone_number": "+91-9876543211",
                "address_line_1": "456, Park Avenue",
                "address_line_2": "Sector 15",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400058",
                "is_active": True
            },
            {
                "hospital": hospital,  # Replace with actual Hospital instance
                "name": "Southside Clinic",
                "code": "SSC-003",
                "email": "southside@cityhospital.com",
                "phone_number": "+91-9876543212",
                "address_line_1": "789, Marine Drive",
                "address_line_2": "Near Beach Road",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400020",
                "is_active": True
            }
        ]
        branches_instances = [Branch(**branch) for branch in branches]
        Branch.objects.bulk_create(branches_instances)
        self.stdout.write(self.style.SUCCESS("Successfully Added 3 Branches!"))
