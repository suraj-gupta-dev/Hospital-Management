from django.contrib import admin

from .models import HospitalAdminProfile, Hospital, Branch, Department


class HospitalStackInLine(admin.StackedInline):
    model = Hospital

class HospitalAdmin(admin.ModelAdmin):
    inlines = [HospitalStackInLine]


admin.site.register(HospitalAdminProfile, HospitalAdmin)
admin.site.register(Hospital)
admin.site.register(Branch)
admin.site.register(Department)