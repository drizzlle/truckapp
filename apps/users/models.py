import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import BaseModel

class User(AbstractUser):
    """
    Extended Django User model
    Handles both Customers and Drivers
    """
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=20, unique=True)
    phone_verified = models.BooleanField(default=False)
    phone_verification_code = models.CharField(max_length=6, null=True, blank=True)
    phone_verification_expires = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, null=True, blank=True)
    email_verification_expires = models.DateTimeField(null=True, blank=True)
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    profile_photo = models.CharField(max_length=500, null=True, blank=True)  # Azure Blob URL
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CustomerProfile(BaseModel):
    """
    Additional customer-specific information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    # KYC fields
    kyc_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], default='pending')
    kyc_reference = models.CharField(max_length=200, null=True, blank=True)  # Youverify reference
    kyc_verified_at = models.DateTimeField(null=True, blank=True)
    # Stats
    total_jobs = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

class DriverProfile(BaseModel):
    """
    Driver-specific information and verification
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')

    # Personal Info
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    # KYC fields
    kyc_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], default='pending')
    kyc_reference = models.CharField(max_length=200, null=True, blank=True)
    kyc_verified_at = models.DateTimeField(null=True, blank=True)

    # Driver's License
    license_number = models.CharField(max_length=50)
    license_photo = models.CharField(max_length=500)  # Azure Blob URL
    license_expiry = models.DateField()

    # Vehicle Info
    vehicle_type = models.ForeignKey('configurations.VehicleType', on_delete=models.PROTECT, null=True, blank=True)
    vehicle_make = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    vehicle_year = models.IntegerField()
    vehicle_plate_number = models.CharField(max_length=20, unique=True)
    vehicle_capacity_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    vehicle_health_status = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ], default='good')

    # Availability
    is_available = models.BooleanField(default=False)
    current_location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    current_location_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)

    # Stats
    total_jobs = models.IntegerField(default=0)
    completed_jobs = models.IntegerField(default=0)
    cancelled_jobs = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

class VehiclePhoto(BaseModel):
    """
    Multiple photos for a driver's vehicle
    """
    driver_profile = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='vehicle_photos')
    photo_url = models.CharField(max_length=500)
    photo_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['photo_order', 'created_at']

