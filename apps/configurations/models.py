import uuid
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class VehicleType(BaseModel):
    """
    Admin-configurable vehicle categories
    """
    name = models.CharField(max_length=100, unique=True)  # e.g., "Motorcycle", "Van", "Pickup Truck"
    description = models.TextField(null=True, blank=True)
    max_weight_kg = models.DecimalField(max_digits=8, decimal_places=2)  # Maximum weight capacity
    pricing_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    icon_url = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

class VehicleYearPricing(BaseModel):
    """
    Admin-configurable pricing multiplier based on vehicle year
    """
    year_from = models.IntegerField()  # e.g., 2020
    year_to = models.IntegerField()    # e.g., 2024
    multiplier = models.DecimalField(max_digits=4, decimal_places=2)  # e.g., 1.20 (20% premium)
    description = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)

class ItemCategory(BaseModel):
    """
    Admin-configurable item categories for pricing
    """
    name = models.CharField(max_length=100, unique=True)  # e.g., "Food", "Household", "Electronics"
    description = models.TextField(null=True, blank=True)
    pricing_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    icon_url = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

class PricingConfig(BaseModel):
    """
    Global pricing configuration (admin managed)
    Only one active record at a time
    """
    base_rate_per_km = models.DecimalField(max_digits=8, decimal_places=2)  # e.g., 50.00 (₦50/km)
    weight_rate_per_kg = models.DecimalField(max_digits=8, decimal_places=2)  # e.g., 10.00 (₦10/kg)
    minimum_fare = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 500.00 (₦500 minimum)
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # 10%
    is_active = models.BooleanField(default=True)
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='pricing_configs')

class SystemSetting(BaseModel):
    """
    Key-value store for system-wide settings
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)
    value_type = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ], default='string')
    
    is_public = models.BooleanField(default=False)  # Can be exposed to frontend
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

