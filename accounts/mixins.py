import uuid
from django.db import models



"""------ID GENERATION (shared by every profile)-----"""

class PrefixIDMixin(models.Model):
    """
    Gives a profile a readable primary key like "DOC-3F9A12BC".
 
    Usage:
        class DoctorProfile(PrefixedIDMixin, ProfileBaseModel):
            ID_PREFIX = "DOC"
            doctor_id = models.CharField(max_length=50, primary_key=True, editable=False)
 
    The primary key field is found through _meta.pk, so you never name it here, and
    each model checks uniqueness against ITS OWN table (cls.objects).
    editable=False makes DRF treat the field as read-only, so clients never send it.
    """

    ID_PREFIX = None

    class Meta:
        abstract = True

    @classmethod
    def _generate_id(cls):
        while True:
            value = f"{cls.ID_PREFIX}-{uuid.uuid4().hex[:8].upper()}"
            if not cls.objects.filter(pk=value).exists():
                return value

    def save(self, *args, **kwargs):
        if self._state.adding and not self.pk:
            # self._meta.pk.attname, it gives the pk field name like, doctor_id, nurse_id
            setattr(self, self._meta.pk.attname, self._generate_id())
        super().save(*args, **kwargs)
    
