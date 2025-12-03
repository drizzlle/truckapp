import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from apps.core.models import BaseModel

class Rating(BaseModel):
    """
    Ratings given after job completion
    """
    RATER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('driver', 'Driver'),
    ]
    
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_given')
    ratee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_received')
    rater_type = models.CharField(max_length=10, choices=RATER_TYPE_CHOICES)
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(null=True, blank=True)
    
    # Specific rating categories (optional)
    professionalism = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    timeliness = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    vehicle_condition = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    is_visible = models.BooleanField(default=True)
    flagged_by_admin = models.BooleanField(default=False)
    admin_notes = models.TextField(null=True, blank=True)

