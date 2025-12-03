from django.contrib import admin
from .models import Job, JobItem, JobStatusHistory, DriverLocationHistory

class JobItemInline(admin.TabularInline):
    model = JobItem
    extra = 0

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_number', 'customer', 'driver', 'status', 'pickup_city', 'delivery_city', 'final_price', 'created_at')
    list_filter = ('status', 'vehicle_type', 'is_scheduled', 'created_at')
    search_fields = ('job_number', 'customer__username', 'driver__username', 'pickup_address', 'delivery_address')
    inlines = [JobItemInline]

@admin.register(JobStatusHistory)
class JobStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('job', 'from_status', 'to_status', 'changed_by', 'created_at')
    list_filter = ('to_status', 'created_at')
    search_fields = ('job__job_number',)

@admin.register(DriverLocationHistory)
class DriverLocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('driver', 'job', 'latitude', 'longitude', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('driver__username', 'job__job_number')

