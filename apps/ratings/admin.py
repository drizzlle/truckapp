from django.contrib import admin
from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('job', 'rater', 'ratee', 'rating', 'rater_type', 'is_visible', 'created_at')
    list_filter = ('rating', 'rater_type', 'is_visible', 'flagged_by_admin')
    search_fields = ('job__job_number', 'rater__username', 'ratee__username', 'review')

