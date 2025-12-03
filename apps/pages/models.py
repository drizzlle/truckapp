from django.db import models
from apps.core.models import BaseModel


class WaitingList(BaseModel):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('both', 'Both'),
    ]
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Waiting List Entry'
        verbose_name_plural = 'Waiting List Entries'
    
    def __str__(self):
        return f"{self.email} ({self.user_type})"
