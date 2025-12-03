from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from apps.users.models import DriverProfile, VehiclePhoto
from apps.payments.models import Payout
from apps.jobs.models import Job
from apps.api.users.serializers import UserSerializer, VehicleTypeSerializer

User = get_user_model()

class VehiclePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePhoto
        fields = ('id', 'photo_url', 'photo_order', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')

class DriverAvailabilitySerializer(serializers.Serializer):
    is_available = serializers.BooleanField()
    current_lat = serializers.DecimalField(max_digits=10, decimal_places=8, required=False)
    current_lng = serializers.DecimalField(max_digits=11, decimal_places=8, required=False)

class DriverStatsSerializer(serializers.ModelSerializer):
    total_earnings = serializers.SerializerMethodField()
    this_month_earnings = serializers.SerializerMethodField()
    this_week_jobs = serializers.SerializerMethodField()
    
    class Meta:
        model = DriverProfile
        fields = (
            'total_jobs', 'completed_jobs', 'cancelled_jobs', 'average_rating',
            'total_earnings', 'this_month_earnings', 'this_week_jobs'
        )
        
    def get_total_earnings(self, obj):
        return Payout.objects.filter(
            driver=obj.user, 
            status='released'
        ).aggregate(total=Sum('net_amount'))['total'] or 0.00
        
    def get_this_month_earnings(self, obj):
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return Payout.objects.filter(
            driver=obj.user,
            status='released',
            created_at__gte=start_of_month
        ).aggregate(total=Sum('net_amount'))['total'] or 0.00
        
    def get_this_week_jobs(self, obj):
        now = timezone.now()
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        return Job.objects.filter(
            driver=obj.user,
            created_at__gte=start_of_week
        ).count()

class DriverSearchResultSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vehicle_type = VehicleTypeSerializer(read_only=True)
    vehicle_photos = VehiclePhotoSerializer(many=True, read_only=True)
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        model = DriverProfile
        fields = (
            'id', 'user', 'vehicle_type', 'vehicle_make', 'vehicle_model',
            'vehicle_year', 'vehicle_plate_number', 'vehicle_capacity_kg',
            'vehicle_health_status', 'average_rating', 'completed_jobs', 'distance_km',
            'vehicle_photos'
        )
