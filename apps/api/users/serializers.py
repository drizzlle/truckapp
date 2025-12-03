from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.users.models import CustomerProfile, DriverProfile, VehiclePhoto
from apps.configurations.models import VehicleType

User = get_user_model()

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ('address', 'city', 'state', 'kyc_status', 'total_jobs', 'average_rating')
        read_only_fields = ('kyc_status', 'total_jobs', 'average_rating')

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ('id', 'name', 'icon_url')

class VehiclePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePhoto
        fields = ('id', 'photo_url', 'photo_order', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')

class DriverProfileSerializer(serializers.ModelSerializer):
    vehicle_type = VehicleTypeSerializer(read_only=True)
    vehicle_photos = VehiclePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = DriverProfile
        fields = (
            'vehicle_type', 'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_plate_number',
            'vehicle_capacity_kg', 'vehicle_health_status', 'average_rating', 'completed_jobs', 'total_jobs',
            'vehicle_photos'
        )

class UserSerializer(serializers.ModelSerializer):
    customer_profile = CustomerProfileSerializer(read_only=True)
    driver_profile = DriverProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'phone_verified', 'profile_photo', 'customer_profile', 'driver_profile')
        read_only_fields = ('id', 'user_type', 'phone_verified')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profile_photo', 'phone_number') # Can update basic info
    
    def update(self, instance, validated_data):
        # Also allow updating profile fields if passed in flattening (e.g., address)
        # But strictly per doc: "first_name", "address". 
        # The address is on CustomerProfile or DriverProfile.
        
        # Check for profile update request context
        request = self.context.get('request')
        if request and 'address' in request.data:
            address = request.data['address']
            if instance.user_type == 'customer' and hasattr(instance, 'customer_profile'):
                instance.customer_profile.address = address
                instance.customer_profile.save()
            elif instance.user_type == 'driver' and hasattr(instance, 'driver_profile'):
                instance.driver_profile.address = address
                instance.driver_profile.save()
                
        return super().update(instance, validated_data)
