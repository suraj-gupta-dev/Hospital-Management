from django.contrib import admin

from .models import HospitalAdminProfile, Hospital, Branch, Department


admin.site.register(HospitalAdminProfile)
admin.site.register(Hospital)
admin.site.register(Branch)
admin.site.register(Department)