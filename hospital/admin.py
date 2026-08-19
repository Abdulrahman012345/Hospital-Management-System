from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Doctor, Patient, Appointment, Prescription, Bill


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role']
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role', 'phone')}),
    )


admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Bill)
