import uuid
from datetime import datetime




class AppointmentIDService:
    """Handles generation of unique appointment IDs."""

    PREFIX = "APT"
    MAX_RETRIES = 5

    @classmethod
    def generate(cls, depart_code):
        """
        Generate a unique appointment ID using clinic, date, and patient info.
        Ensures uniqueness by retrying on collision.
        """
        for _ in range(cls.MAX_RETRIES):
            candidate = cls._build_id(depart_code)
            if not cls._exists(candidate):
                return candidate
        raise RuntimeError("Could not generate unique appointment ID")

    @classmethod
    def _build_id(cls, depart_code):
        date_part = datetime.now().strftime("%Y%m%d")
        uuid_part = uuid.uuid4().hex[:6].upper()
        return f"{cls.PREFIX}-{depart_code}-{date_part}-{uuid_part}"

    @classmethod
    def _exists(cls, appointment_number):
        from appointments.models import Appointment
        return Appointment.objects.filter(
            appointment_number=appointment_number
        ).exists()
