from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.users.models import CustomerProfile, DriverProfile
from apps.configurations.models import VehicleType
from apps.api.users.serializers import UserSerializer
from django.utils import timezone
from datetime import timedelta
import secrets

User = get_user_model()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Map 'email' to 'username' if present
        if 'email' in attrs:
            attrs['username'] = attrs.pop('email')
        return super().validate(attrs)

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone_number')

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['email'],
            user_type='customer',
            **validated_data
        )
        CustomerProfile.objects.create(user=user)
        return user

class DriverRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    # Driver Profile Fields
    address = serializers.CharField(write_only=True)
    city = serializers.CharField(write_only=True)
    state = serializers.CharField(write_only=True)
    license_number = serializers.CharField(write_only=True)
    license_expiry = serializers.DateField(write_only=True)
    vehicle_make = serializers.CharField(write_only=True)
    vehicle_model = serializers.CharField(write_only=True)
    vehicle_year = serializers.IntegerField(write_only=True)
    vehicle_plate_number = serializers.CharField(write_only=True)
    vehicle_type_id = serializers.UUIDField(write_only=True)
    vehicle_capacity_kg = serializers.DecimalField(max_digits=8, decimal_places=2, write_only=True, required=False)
    vehicle_health_status = serializers.CharField(write_only=True, required=False)
    
    # File uploads (URLs or actual files? Docs imply files, but for MVP simplicity we might handle as strings or files. 
    # Docs say [FILE], but here we'll use CharField/FileField depending on requirements. 
    # The model has CharField (URL), assuming upload is handled elsewhere or passed as URL. 
    # For strict MVP per instructions "do not over engineer", I will use CharFields assuming frontend uploads to blob storage first 
    # OR use FileField if I was implementing the upload. 
    # The prompt implies standard Django Rest Framework. I'll stick to CharField for URLs as per the model definition.)
    license_photo = serializers.CharField(write_only=True, required=False)
    vehicle_photos = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        max_length=5,
        min_length=1
    )
    profile_photo = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone_number', 'profile_photo',
            'address', 'city', 'state',
            'license_number', 'license_expiry', 'license_photo',
            'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_plate_number',
            'vehicle_type_id', 'vehicle_capacity_kg', 'vehicle_health_status', 'vehicle_photos'
        )

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_vehicle_plate_number(self, value):
        from apps.users.models import DriverProfile
        if DriverProfile.objects.filter(vehicle_plate_number=value).exists():
            raise serializers.ValidationError("Vehicle plate number already registered")
        return value

    def validate_license_expiry(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("License has expired")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        vehicle_type_id = attrs.get('vehicle_type_id')
        if vehicle_type_id and not VehicleType.objects.filter(id=vehicle_type_id, is_active=True).exists():
            raise serializers.ValidationError({"vehicle_type_id": "Invalid vehicle type"})

        return attrs

    def create(self, validated_data):
        from apps.users.models import VehiclePhoto

        validated_data.pop('password_confirm')
        vehicle_photos_urls = validated_data.pop('vehicle_photos', [])

        profile_data = {
            'address': validated_data.pop('address'),
            'city': validated_data.pop('city'),
            'state': validated_data.pop('state'),
            'license_number': validated_data.pop('license_number'),
            'license_expiry': validated_data.pop('license_expiry'),
            'license_photo': validated_data.pop('license_photo', ''),
            'vehicle_make': validated_data.pop('vehicle_make'),
            'vehicle_model': validated_data.pop('vehicle_model'),
            'vehicle_year': validated_data.pop('vehicle_year'),
            'vehicle_plate_number': validated_data.pop('vehicle_plate_number'),
            'vehicle_type_id': validated_data.pop('vehicle_type_id'),
            'vehicle_capacity_kg': validated_data.pop('vehicle_capacity_kg', None),
            'vehicle_health_status': validated_data.pop('vehicle_health_status', 'good'),
        }

        user = User.objects.create_user(
            username=validated_data['email'],
            user_type='driver',
            **validated_data
        )

        driver_profile = DriverProfile.objects.create(user=user, **profile_data)

        for index, photo_url in enumerate(vehicle_photos_urls):
            VehiclePhoto.objects.create(
                driver_profile=driver_profile,
                photo_url=photo_url,
                photo_order=index,
                is_primary=(index == 0)
            )

        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match"})

        token = attrs.get('token')
        try:
            user = User.objects.get(password_reset_token=token)
            if not user.password_reset_expires or user.password_reset_expires < timezone.now():
                raise serializers.ValidationError({"token": "Password reset token has expired"})
            attrs['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid password reset token"})

        return attrs

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match"})
        return attrs

class EmailVerificationRequestSerializer(serializers.Serializer):
    pass

class EmailVerificationConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)

