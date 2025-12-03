import uuid
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Job(BaseModel):
    """
    Main job/delivery request
    """
    JOB_STATUS_CHOICES = [
        ('pending', 'Pending'),  # Customer created, waiting for driver response
        ('driver_assigned', 'Driver Assigned'),  # Driver accepted
        ('pickup_confirmed', 'Pickup Confirmed'),  # Both confirmed pickup
        ('in_transit', 'In Transit'),  # Delivery in progress
        ('delivered', 'Delivered'),  # Driver marked as delivered
        ('completed', 'Completed'),  # Customer confirmed delivery
        ('cancelled_by_customer', 'Cancelled by Customer'),
        ('cancelled_by_driver', 'Cancelled by Driver'),
        ('disputed', 'Disputed'),  # Flagged for admin review
    ]
    
    job_number = models.CharField(max_length=20, unique=True)  # e.g., "JOB-20251127-0001"
    
    # Parties
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='jobs_as_customer')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='jobs_as_driver')
    
    # Job Details
    status = models.CharField(max_length=30, choices=JOB_STATUS_CHOICES, default='pending')
    vehicle_type = models.ForeignKey('configurations.VehicleType', on_delete=models.PROTECT)
    
    # Pickup
    pickup_address = models.TextField()
    pickup_city = models.CharField(max_length=100)
    pickup_state = models.CharField(max_length=100)
    pickup_lat = models.DecimalField(max_digits=10, decimal_places=8)
    pickup_lng = models.DecimalField(max_digits=11, decimal_places=8)
    pickup_contact_name = models.CharField(max_length=200)
    pickup_contact_phone = models.CharField(max_length=20)
    
    # Delivery
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=100)
    delivery_lat = models.DecimalField(max_digits=10, decimal_places=8)
    delivery_lng = models.DecimalField(max_digits=11, decimal_places=8)
    delivery_contact_name = models.CharField(max_length=200)
    delivery_contact_phone = models.CharField(max_length=20)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    scheduled_pickup_time = models.DateTimeField(null=True, blank=True)
    
    # Calculated fields
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    total_weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    highest_category_multiplier = models.DecimalField(max_digits=4, decimal_places=2)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)  # After all multipliers
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    driver_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Special instructions
    special_instructions = models.TextField(null=True, blank=True)
    
    # Timestamps
    # created_at and updated_at are inherited from BaseModel
    driver_assigned_at = models.DateTimeField(null=True, blank=True)
    pickup_confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Cancellation/Dispute
    cancellation_reason = models.TextField(null=True, blank=True)
    dispute_reason = models.TextField(null=True, blank=True)
    dispute_resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disputes')
    dispute_resolved_at = models.DateTimeField(null=True, blank=True)

    VALID_TRANSITIONS = {
        'pending': ['driver_assigned', 'cancelled_by_customer'],
        'driver_assigned': ['pickup_confirmed', 'cancelled_by_customer', 'cancelled_by_driver'],
        'pickup_confirmed': ['in_transit', 'cancelled_by_driver'],
        'in_transit': ['delivered', 'cancelled_by_driver'],
        'delivered': ['completed', 'disputed'],
        'completed': [],
        'cancelled_by_customer': [],
        'cancelled_by_driver': [],
        'disputed': ['completed'],
    }

    def can_transition_to(self, new_status):
        """Check if status transition is valid"""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def change_status(self, new_status, changed_by, reason=None):
        """
        Change status with validation and history tracking

        Args:
            new_status: The new status to transition to
            changed_by: User making the change
            reason: Optional reason for the change

        Returns:
            bool: True if successful

        Raises:
            ValueError: If transition is invalid
        """
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition from '{self.status}' to '{new_status}'. "
                f"Valid transitions: {', '.join(self.VALID_TRANSITIONS.get(self.status, []))}"
            )

        old_status = self.status
        self.status = new_status

        JobStatusHistory.objects.create(
            job=self,
            from_status=old_status,
            to_status=new_status,
            changed_by=changed_by,
            notes=reason
        )

        self.save()
        return True

class JobItem(models.Model):
    """
    Items being delivered in a job
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey('configurations.ItemCategory', on_delete=models.PROTECT)
    description = models.CharField(max_length=500)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)
    photo_url = models.CharField(max_length=500, null=True, blank=True)  # Optional item photo
    created_at = models.DateTimeField(auto_now_add=True)

class JobStatusHistory(models.Model):
    """
    Audit trail for job status changes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=30, null=True, blank=True)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class DriverLocationHistory(models.Model):
    """
    Track driver location during active jobs for replay/analytics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='location_history')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    accuracy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # meters
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # km/h
    created_at = models.DateTimeField(auto_now_add=True)

