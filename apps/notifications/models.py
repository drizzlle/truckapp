import uuid
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Notification(models.Model):
    """
    Push notifications and in-app alerts
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('job_request', 'Job Request'),  # Driver receives job offer
        ('job_accepted', 'Job Accepted'),  # Customer notified driver accepted
        ('job_rejected', 'Job Rejected'),  # Customer notified driver rejected
        ('driver_assigned', 'Driver Assigned'),
        ('pickup_confirmed', 'Pickup Confirmed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('payment_received', 'Payment Received'),
        ('payout_released', 'Payout Released'),
        ('rating_received', 'Rating Received'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(null=True, blank=True)  # Additional payload (job_id, etc.)
    
    # Delivery
    is_read = models.BooleanField(default=False)
    is_push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    fcm_message_id = models.CharField(max_length=200, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

class FCMDevice(BaseModel):
    """
    Store FCM tokens for push notifications
    """
    DEVICE_TYPE_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_devices')
    device_token = models.CharField(max_length=500)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)

