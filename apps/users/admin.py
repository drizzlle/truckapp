from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomerProfile, DriverProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active', 'phone_verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'phone_verified', 'profile_photo')}),
    )

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'kyc_status', 'total_jobs')
    list_filter = ('kyc_status', 'city')
    search_fields = ('user__username', 'user__email', 'address')

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_plate_number', 'is_available', 'kyc_status')
    list_filter = ('kyc_status', 'is_available', 'vehicle_type')
    search_fields = ('user__username', 'user__email', 'license_number', 'vehicle_plate_number')

