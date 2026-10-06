from django.core.management.base import BaseCommand
from django.core.management import call_command

from hospital.models import Department




DEPARTMENTS = [
    {
        "name": "Cardiology",
        "code": "CARD",
        "description": "Diagnosis and treatment of heart and cardiovascular system disorders, including heart disease, heart failure, and arrhythmias.",
        "phone_number": "+1-555-0101",
        "email": "cardiology@hospital.com",
        "floor": "3rd Floor",
    },
    {
        "name": "Neurology",
        "code": "NEUR",
        "description": "Diagnosis and treatment of disorders of the nervous system, including the brain, spinal cord, and nerves.",
        "phone_number": "+1-555-0102",
        "email": "neurology@hospital.com",
        "floor": "4th Floor",
    },
    {
        "name": "Orthopedics",
        "code": "ORTH",
        "description": "Diagnosis and treatment of musculoskeletal system conditions involving bones, joints, ligaments, tendons, and muscles.",
        "phone_number": "+1-555-0103",
        "email": "orthopedics@hospital.com",
        "floor": "2nd Floor",
    },
    {
        "name": "Pediatrics",
        "code": "PEDI",
        "description": "Medical care for infants, children, and adolescents, covering their physical, emotional, and social health.",
        "phone_number": "+1-555-0104",
        "email": "pediatrics@hospital.com",
        "floor": "1st Floor",
    },
    {
        "name": "Emergency",
        "code": "EMER",
        "description": "Immediate assessment and treatment of acute illnesses and injuries, available 24/7 for critical care.",
        "phone_number": "+1-555-0105",
        "email": "emergency@hospital.com",
        "floor": "Ground Floor",
    },
    {
        "name": "General Medicine",
        "code": "GENM",
        "description": "Comprehensive primary care for adults, including prevention, diagnosis, and treatment of common medical conditions.",
        "phone_number": "+1-555-0106",
        "email": "generalmedicine@hospital.com",
        "floor": "2nd Floor",
    }
]

{
    "name": "Radiology",
    "code": "RADI",
    "description": "Medical imaging services including X-ray, CT scan, MRI, ultrasound, and mammography for diagnostic purposes.",
    "phone_number": "+1-555-0107",
    "email": "radiology@hospital.com",
    "floor": "Basement Level",
}

class Command(BaseCommand):
    help = "Create 3 Hospital Branches"

    def handle(self, *args, **options):
        departments = Department.objects.all().exists()
        if departments:
            Department.objects.all().delete()

        Department.objects.bulk_create(
            [Department(**depart) for depart in DEPARTMENTS]
        )

        self.stdout.write(self.style.SUCCESS("Successfully created Departments!"))

        
