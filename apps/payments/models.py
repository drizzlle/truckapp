import uuid
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Payment(BaseModel):
    """
    Payment transactions
    """
    PAYMENT_TYPE_CHOICES = [
        ('commitment_fee', 'Commitment Fee'),  # Initial 50%
        ('final_payment', 'Final Payment'),    # Remaining 50%
        ('refund', 'Refund'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    payment_reference = models.CharField(max_length=100, unique=True)  # Our reference
    job = models.ForeignKey('jobs.Job', on_delete=models.PROTECT, related_name='payments')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments_made')
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Paystack fields
    paystack_reference = models.CharField(max_length=200, unique=True)
    paystack_access_code = models.CharField(max_length=200, null=True, blank=True)
    paystack_authorization_url = models.CharField(max_length=500, null=True, blank=True)
    paystack_callback_data = models.JSONField(null=True, blank=True)
    
    # Metadata
    payment_method = models.CharField(max_length=50, null=True, blank=True)  # card, bank_transfer, etc.
    payment_channel = models.CharField(max_length=50, null=True, blank=True)
    
    # created_at is inherited
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)

class Payout(BaseModel):
    """
    Payouts to drivers at job milestones
    """
    PAYOUT_TYPE_CHOICES = [
        ('pickup_milestone', 'Pickup Milestone'),  # After pickup
        ('delivery_milestone', 'Delivery Milestone'),  # After delivery
        ('cancellation_compensation', 'Cancellation Compensation'),
    ]
    
    PAYOUT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('released', 'Released'),
        ('held', 'Held'),  # For disputes
        ('reversed', 'Reversed'),
    ]
    
    payout_reference = models.CharField(max_length=100, unique=True)
    job = models.ForeignKey('jobs.Job', on_delete=models.PROTECT, related_name='payouts')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payouts_received')
    
    payout_type = models.CharField(max_length=30, choices=PAYOUT_TYPE_CHOICES)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Before platform fee
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)  # After platform fee
    status = models.CharField(max_length=20, choices=PAYOUT_STATUS_CHOICES, default='pending')
    
    released_at = models.DateTimeField(null=True, blank=True)
    reversed_at = models.DateTimeField(null=True, blank=True)
    reversal_reason = models.TextField(null=True, blank=True)

