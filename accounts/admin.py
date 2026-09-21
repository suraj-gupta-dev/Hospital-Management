from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import (
    User, DoctorProfile, NurseProfile,
    PatientProfile, ReceptionistProfile, HospitalAdminProfile,
    LabTechnicianProfile, CashierProfile
)




class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Mark non-editable fields as read-only so they can be displayed
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_verified']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'last_name', 'phone_number', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
admin.site.register(NurseProfile)
admin.site.register(ReceptionistProfile)
admin.site.register(HospitalAdminProfile)
admin.site.register(LabTechnicianProfile)
admin.site.register(CashierProfile)